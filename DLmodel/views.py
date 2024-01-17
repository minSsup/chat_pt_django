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
from django.core.cache import cache  # 캐싱을 위한 임포트
from django.db.models import F  # 데이터베이스 연산을 위한 임포트

from datetime import datetime

def calory(request):
    if request.method == 'GET':
        user_id = request.GET.get('id')
        df_food_data, df_food_rating_data = load_data()
        nomeminfo = oracle_teamd().normal_member_DB(user_id)
        userNum = int(nomeminfo[0][0])
        #현재 칼로리 정보
        nowcalory = nowcal(userNum)

        # 권장 칼로리 정보
        recommand_cal,userage, userpurpose =cal_Recommended_Calories(user_id)

        # 연령대 정보
        age_Decade = np.floor(userage / 10) * 10

        # 연령대별 최신 25개 음식 정보 및 등록자 정보
        list_age_food = getListAgeFood(userNum, age_Decade)

        # 목적별 최신 25개 음식 정보 및 등록자 정보
        list_purpose_food = getListPurposeFood(userNum, userpurpose)

        #현재 탄단지 양
        now_tan, now_dan, now_gi = nowNutrient(userNum)

        #권장 탄단지 양
        recommand_tan, recommand_dan, recommand_gi = recommand_tandangi(recommand_cal,user_id)

        #마지막으로 먹은 음식 이름
        lastfoodName = lastfoodInfo(userNum)

        # 데이터셋 로딩 및 모델 학습
        trainset, testset = prepare_dataset(df_food_rating_data)
        svd_model, knn_model, nmf_model = train_models(trainset)

        # 예측 평가
        evaluate_predictions(testset, svd_model, knn_model, nmf_model)
        # 추천 항목 가져오기
        recommended_items = get_recommendations(userNum, trainset, svd_model, knn_model, nmf_model)

        # 추천된 항목들에 대한 정보 찾기
        recommended_foods = df_food_data[df_food_data['FOODNUM'].isin(recommended_items)]

        resData = {
            "recommand_cal": recommand_cal  # Add recommand_cal to the response
            ,"now_cal" : nowcalory
            ,"recomand_nutrition" : [recommand_tan, recommand_dan, recommand_gi]
            ,"now_nutrition" :  [now_tan, now_dan, now_gi]
            ,"lastfood" : lastfoodName
            ,"recomandfood" : json.loads(recommended_foods.to_json(orient='records', force_ascii=False))
            , "userage": userage
            , "age_food_info": list_age_food
            , "purpose_food_info": list_purpose_food
            , 'userpurpose': userpurpose

        }




        return JsonResponse(resData, safe=False)

def recommand(request):
    if request.method == 'GET':

        user_id = request.GET.get('id')
        nomeminfo = oracle_teamd().normal_member_DB(user_id)
        userNum = int(nomeminfo[0][0])
        df_food_data, df_food_rating_data = load_data()

        # 데이터셋 로딩 및 모델 학습
        trainset, testset = prepare_dataset(df_food_rating_data)
        svd_model, knn_model, nmf_model = train_models(trainset)

        # 예측 평가
        evaluate_predictions(testset, svd_model, knn_model, nmf_model)

        # 추천 항목 가져오기
        recommended_items = get_recommendations(userNum, trainset, svd_model, knn_model, nmf_model)

        # 추천된 항목들에 대한 정보 찾기
        recommended_foods = df_food_data[df_food_data['FOODNUM'].isin(recommended_items)]

        # 결과를 JSON 형식으로 변환
        resData = {
            "recommended_foods": json.loads(recommended_foods.to_json(orient='records', force_ascii=False)),
        }

        return JsonResponse(resData, safe=False)


def load_data():
    # oracle_teamd 클래스의 인스턴스를 생성합니다.
    oracle_teamd_instance = oracle_teamd()

    # 인스턴스 메서드를 호출합니다.
    df_food_data = pd.DataFrame(
        oracle_teamd_instance.food_DB(),
        columns=['FOODNUM', 'FOODCAL', 'FOODIMG', 'FOOD_TAN', 'FOOD_DAN', 'FOOD_GI', 'FOODWEIGHT', 'FOODNAME']
    )
    df_food_rating_data = pd.DataFrame(
        oracle_teamd_instance.food_rating_DB(),
        columns=['NNUM', 'FOODNUM', 'RATING']
    )

    return df_food_data, df_food_rating_data


def prepare_dataset(df_food_rating_data):
    # 데이터셋 로딩 및 분할
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df_food_rating_data[['RATING', 'FOODNUM', 'NNUM']], reader)
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

# 추천 목록 10개를 반환하는 함수
def get_recommendations(user_id, trainset, svd_model, knn_model, nmf_model, top_n=10):
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
    # 멤버 기본 정보
    meminfo  = oracle_teamd().member_DB(user_id)
    # 일반 회원 정보
    nomeminfo = oracle_teamd().normal_member_DB(user_id)
    user_name = meminfo[0][0]  # 유저이름
    user_gender = meminfo[0][1] # 유저 성별
   # print(meminfo[0][2])
    user_age = calculate_age(meminfo[0][2])  # 유저 나이
    user_weight = float(nomeminfo[0][2])  # 유저 몸무게
    user_height = float(nomeminfo[0][3]) # 유저 키
    user_purpose = int(nomeminfo[0][4]) # 식단 목적
    user_activity = int(nomeminfo[0][5]) # 유저 활동량
    print(user_purpose)

    # print("만나이 : " , user_age)
    # print("성별 : ", user_gender)
    # print("이름 : " ,user_name)
    # print("키 : ", user_height)
    # print("몸무게 : ", user_weight)
    # print("목적 : ", user_purpose)
    # print("활동량 : ", user_activity)
    recommand_cal = 0

    # 성별에 따른 칼로리 계산 (해리스-베네딕트 방정식)
    if user_gender  == 'Male':
        recommand_cal = 88.362  + (13.397  *user_weight) + (4.799 * user_height) - (5.677 * user_age)
    elif user_gender == 'Female':
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
    return recommand_cal,user_age,user_purpose



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
    nomeminfo = oracle_teamd().normal_member_DB(user_id)
    user_purpose = int(nomeminfo[0][4]) # 식단 목적
    # 목적에 따른 번호 (0: 다이어트, 1: 체중 유지 , 2 : 벌크업)
    tan_multiplier = {0: 0.40 ,1: 0.45 , 2: 0.40} # 탄수화물 권장 칼로리 비율
    multiplier_t = tan_multiplier[user_purpose]
    recommand_tan = recommand_cal * multiplier_t / 4

    dan_multiplier = {0: 0.33, 1: 0.25, 2: 0.30}  # 단백질 권장 칼로리 비율
    multiplier_d = dan_multiplier[user_purpose]
    recommand_dan = recommand_cal * multiplier_d / 4

    gi_multiplier = {0: 0.27, 1: 0.30, 2: 0.30}  # 지방 권장 칼로리 비율
    multiplier_g = gi_multiplier[user_purpose]
    recommand_gi = recommand_cal * multiplier_g / 9

    print("추천 탄수화물(g) : ", recommand_tan)
    print("추천 단백질(g) : ", recommand_dan)
    print ("추천 지방(g) : ", recommand_gi)

    return recommand_tan, recommand_dan, recommand_gi

def nowcal(user_num):
    dietInfo = oracle_teamd().diet_DB(user_num)
    nowcalory = 0
    for i in range(len(dietInfo)):
        food_num = dietInfo[i][0]
        mass = dietInfo[i][1]
       #print("음식번호 : ", food_num)
       #print("질량(g) : ",mass)
        foodCal,foodmass = foodcalInfo(food_num)
        foodCal = foodCal*(mass/foodmass)
       #print("칼로리 -> 질량 : ",foodCal)
        nowcalory += foodCal
    print("총 현재 칼로리 : " ,nowcalory)
    return nowcalory



def foodcalInfo(food_num):
    foodInfo = oracle_teamd().food_Num_DB(food_num)
    foodCal = foodInfo[0][1]
    foodmass = foodInfo[0][6]
    return foodCal,foodmass

def nowNutrient(user_num):
    dietInfo = oracle_teamd().diet_DB(user_num)
    now_tan,now_dan,now_gi = 0,0,0
    for i in range(len(dietInfo)):
        food_num = dietInfo[i][0]
        mass = dietInfo[i][1]
        food_tan,food_dan,food_gi,foodmass = foodnutrientInfo(food_num)
        food_tan = food_tan*(mass/foodmass)
        food_dan = food_dan * (mass / foodmass)
        food_gi = food_gi * (mass / foodmass)
        now_tan += food_tan
        now_dan += food_dan
        now_gi += food_gi
    print("총 현재 탄수화물 : " ,now_tan)
    print("총 현재 단백질 : ", now_dan)
    print("총 현재 지방 : ", now_gi)
    return now_tan,now_dan,now_gi



def foodnutrientInfo(food_num):
    foodInfo = oracle_teamd().food_Num_DB(food_num)
    food_tan = foodInfo[0][3]
    food_dan = foodInfo[0][4]
    food_gi = foodInfo[0][5]
    foodmass = foodInfo[0][6]
    return food_tan,food_dan,food_gi,foodmass

def lastfoodInfo(usernum):
    lastfoodInfo = oracle_teamd().last_food_DB(usernum)
    print(lastfoodInfo)
    foodInfo = oracle_teamd().food_Num_DB(lastfoodInfo[0][0])
    foodName =  foodInfo[0][7]
    return foodName

def getListAgeFood(usernum, ageDecade):
    ageFoodList = oracle_teamd().list_age_food_info(usernum,ageDecade)
    return ageFoodList

def getListPurposeFood(usernum, purpose):
    purposeFoodList = oracle_teamd().list_purpose_food_info(usernum,purpose)
    return purposeFoodList
