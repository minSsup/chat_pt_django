from django.shortcuts import render

from DLmodel.models import oracle_teamd

# Create your views here.
import pandas as pd
from surprise import Dataset, Reader, SVD, KNNBasic, NMF, accuracy
from sklearn.metrics.pairwise import cosine_similarity
from surprise.model_selection import train_test_split
import numpy as np
from django.http import JsonResponse, HttpResponse
import json

from datetime import datetime


def recommand(request):
    if request.method == 'GET':
        user_id = request.GET.get('id')
        df_food_data, df_food_rating_data = load_data()

        # 데이터셋 로딩 및 모델 학습
        trainset, testset = prepare_dataset(df_food_rating_data)
        svd_model, knn_model, nmf_model = train_models(trainset)

        # 예측 평가
        evaluate_predictions(testset, svd_model, knn_model, nmf_model)

        recommand_cal =cal_Recommended_Calories(user_id)
        recommand_tan, recommand_dan, recommand_gi = recommand_tandangi(recommand_cal,user_id)

        # 추천 항목 가져오기
        recommended_items = get_recommendations(user_id, trainset, svd_model, knn_model, nmf_model)

        # 추천된 항목들에 대한 정보 찾기
        recommended_foods = df_food_data[df_food_data['FOODNUM'].isin(recommended_items)]

        # 결과를 JSON 형식으로 변환
        resJson = recommended_foods.to_json(orient='records', force_ascii=False)
        resData = json.loads(resJson)

        return JsonResponse(resData, safe=False)


def load_data():
    # 데이터 불러오기 및 전처리
    df_food_data = pd.DataFrame(oracle_teamd().food_DB(), columns = ['FOODNUM', 'FOODCAL','FOODIMG','FOOD_TAN','FOOD_DAN','FOOD_GI','FOODWEIGHT','FOODNAME'])
    df_food_rating_data = pd.DataFrame(oracle_teamd().food_rating_DB(), columns=['USERID', 'FOODNUM', 'RATING'])

    return df_food_data, df_food_rating_data


def prepare_dataset(df_food_rating_data):
    # 데이터셋 로딩 및 분할
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df_food_rating_data[['USERID', 'FOODNUM', 'RATING']], reader)
    trainset = data.build_full_trainset()
    testset = trainset.build_testset()
    return trainset, testset


def train_models(trainset):
    # 모델 학습
    svd_model = SVD(n_factors=200, n_epochs=50)
    knn_model = KNNBasic(sim_options={'name': 'cosine'})
    nmf_model = NMF(n_factors=200, n_epochs=50)

    svd_model.fit(trainset)
    knn_model.fit(trainset)
    nmf_model.fit(trainset)

    return svd_model, knn_model, nmf_model


def evaluate_predictions(testset, svd_model, knn_model, nmf_model):
    # 예측 평가
    for model in [svd_model, knn_model, nmf_model]:
        predictions = model.test(testset)
        rmse = accuracy.rmse(predictions)
        print(f"Model {model.__class__.__name__} RMSE: {rmse}")

# 추천 목록 5개를 반환하는 함수
def get_recommendations(user_id, trainset, svd_model, knn_model, nmf_model, top_n=5):
    # 사용자가 평가하지 않은 항목들 찾기
    user_inner_id = trainset.to_inner_uid(user_id)
    user_rated_items = set([j for (j, _) in trainset.ur[user_inner_id]])
    all_items = set(trainset.all_items())
    unrated_items = all_items - user_rated_items

    # 각 모델을 사용하여 예측 평점 계산
    predictions = []
    for item_inner_id in unrated_items:
        svd_pred = svd_model.predict(user_id, trainset.to_raw_iid(item_inner_id)).est
        knn_pred = knn_model.predict(user_id, trainset.to_raw_iid(item_inner_id)).est
        nmf_pred = nmf_model.predict(user_id, trainset.to_raw_iid(item_inner_id)).est
        avg_pred = (svd_pred + knn_pred + nmf_pred) / 3
        predictions.append((item_inner_id, avg_pred))

    # 평점이 가장 높은 상위 N개 항목 추천
    predictions.sort(key=lambda x: x[1], reverse=True)
    top_items = [trainset.to_raw_iid(iid) for (iid, _) in predictions[:top_n]]

    return top_items


# 권장 칼로리를 구하는 함수
def cal_Recommended_Calories(user_id):
    meminfo = oracle_teamd().member_DB(user_id)
    user_name = meminfo[0][0]  # 유저이름
    user_gender = meminfo[0][4] # 유저 성별
    user_height = meminfo[0][8] # 유저 키
    user_weight = meminfo[0][7] # 유저 몸무게
    user_purpose = int(meminfo[0][9]) # 식단 목적
    user_activity = int(meminfo[0][11]) # 유저 활동량
    user_age = calculate_age(meminfo[0][6]) # 유저 나이


    print("만나이 : " , user_age)
    print("이름 : " ,user_name)
    recommand_cal = 0

    # 성별에 따른 칼로리 계산 (해리스-베네딕트 방정식)
    if user_gender  == '남자':
        recommand_cal = 88.362  + (13.397  *user_weight) + (4.799 * user_height) - (5.677 * user_age)
    elif user_gender == '여자':
        recommand_cal = 447.593  + (9.247  * user_weight) + (3.098  * user_height) - (4.330  * user_age)

    # 활동양에 따른 칼로리 계산 (해리스-베네딕트 방정식)
    activity_multiplier = {0: 1.375, 1: 1.55, 2: 1.725}  # 활동양에 따른 칼로리 배율 (0 : 가벼운 활동 , 1 : 중간 정도 활동, 2 : 활동적)
    multiplier_a = activity_multiplier[user_activity]
    recommand_cal *= multiplier_a

    # 다이어트 목적에 따른 칼로리 계산
    purpose_multiplier = {0: -500 ,1: 0 , 2: 500} # 목적에 따른 칼로리 증가량 (0: 다이어트, 1: 체중 유지 , 2 : 벌크업)
    multiplier_p = purpose_multiplier[user_purpose]
    recommand_cal += multiplier_p
    print ("권장 칼로리 : " ,recommand_cal)
    return recommand_cal



# 생년월일을 이용해 만 나이를 구하는 공식
def calculate_age(birthdate):
    current_date = datetime.now()

    # 생년월일과 현재 날짜의 차이를 계산
    age_in_days = (current_date - birthdate).days

    # 일수를 연도로 변환하여 나이 계산
    age_in_years = age_in_days / 365.25

    return int(age_in_years)

# 권장 탄수화물, 단백질 지방을 구하는 공식
def recommand_tandangi(recommand_cal,user_id):
    meminfo = oracle_teamd().member_DB(user_id)
    user_purpose = int(meminfo[0][9])  # 식단 목적
    # 목적에 따른 번호 (0: 다이어트, 1: 체중 유지 , 2 : 벌크업)
    tan_multiplier = {0: 0.40 ,1: 0.45 , 2: 0.50} # 탄수화물 권장 칼로리 비율
    multiplier_t = tan_multiplier[user_purpose]
    recommand_tan = recommand_cal * multiplier_t / 4

    dan_multiplier = {0: 0.33, 1: 0.25, 2: 0.35}  # 단백질 권장 칼로리 비율
    multiplier_d = dan_multiplier[user_purpose]
    recommand_dan = recommand_cal * multiplier_d / 4

    gi_multiplier = {0: 0.27, 1: 0.30, 2: 0.15}  # 지방 권장 칼로리 비율
    multiplier_g = gi_multiplier[user_purpose]
    recommand_gi = recommand_cal * multiplier_g / 9

    print("추천 탄수화물(g) : ", recommand_tan)
    print("추천 단백질(g) : ", recommand_dan)
    print("추천 지방(g) : ", recommand_gi)

    return recommand_tan, recommand_dan, recommand_gi

