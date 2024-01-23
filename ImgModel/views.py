from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ImgModel import apps
import cv2
import numpy as np
from ImgModel.models import oracle_teamd
import base64
import logging
from PIL import Image
import io
import requests

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로그 레벨 설정
handler = logging.StreamHandler()  # 콘솔 출력 핸들러
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@csrf_exempt
def find_food(request):
    if request.method == 'POST':
        # Base64 인코딩된 이미지 데이터와 사용자 이름 추출
        user_name = request.POST.get('userName', 'default_user')
        images_data = {k: v for k, v in request.POST.items() if k != 'userName'}
        print("user_name : ", user_name)
        results = []  # 각 이미지에 대한 예측 결과를 저장할 리스트
        # 이미지 데이터 처리
        for category, base64_img in images_data.items():
            try:
                # Base64 데이터에서 MIME 타입 부분을 제거
                if base64_img.startswith('data:image'):
                    # 'data:image/jpeg;base64,' 부분을 제거
                    header, base64_encoded_data = base64_img.split(';base64,')
                    # Base64 디코딩
                    img_data = base64.b64decode(base64_encoded_data)
                    # 바이너리 데이터를 PIL Image 객체로 변환
                    image = Image.open(io.BytesIO(img_data))
                    image_resize = image.resize((300, 300))  # 모델이 기대하는 입력 크기 (이 경우 300x300)

                    # RGBA 이미지를 RGB로 변환
                    if image_resize.mode != 'RGB':
                        image_resize = image_resize.convert('RGB')

                    # 음식 이름 예측
                    model = apps.ImgmodelConfig.model
                    img_array = np.expand_dims(np.asarray(image_resize), axis=0)
                    predictions = model.predict(img_array)
                    # 상위 4개 인덱스 가져오기
                    top_4_foods = [int(e) for e in np.argsort(predictions[0])[-4:]]
                    # 상위 4개 확률 가져오기
                    top_4_probabilities = [round(float(prob) * 100, 2) for prob in predictions[0][top_4_foods]]

                    # 각 이미지에 대한 예측 결과 생성
                    result = {
                        'base64_encoded_data': base64_encoded_data,
                        'category': category[:category.find('[')],
                        'foodnum': top_4_foods[3],
                        'candidate1': top_4_foods[2],
                        'candidate2': top_4_foods[1],
                        'candidate3': top_4_foods[0],
                        'predictrate': top_4_probabilities[3],
                        'candidate1rate': top_4_probabilities[2],
                        'candidate2rate': top_4_probabilities[1],
                        'candidate3rate': top_4_probabilities[0],
                    }
                    results.append(result)
                else:
                    logger.error(f"Invalid image data format for category {category}")
            except Exception as e:
                logger.error(f"Error processing image for category {category}: {e}")

        if results:
            print(results)
            return JsonResponse({'status': 'success', 'results': results})
        else:
            return JsonResponse({'status': 'error', 'message': 'No files processed'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def find_food_for_kakao(request):
    if request.method == 'POST':
        user_name = request.POST.get('userName', 'default_user')
        meal_time = request.POST.get('meal_time')
        images_urls = {k: v for k, v in request.POST.items() if k.startswith('image')}

        results = []  # 각 이미지에 대한 예측 결과를 저장할 리스트

        # 이미지 URL 데이터 처리
        for category, image_url in images_urls.items():
            response = requests.get(image_url)  # URL로부터 이미지를 가져옴
            image = Image.open(io.BytesIO(response.content))  # 응답에서 이미지를 로드
            image_resize = image.resize((300, 300))

            # 음식 이름 예측
            model = apps.ImgmodelConfig.model
            img_array = np.expand_dims(np.asarray(image_resize), axis=0)
            predictions = model.predict(img_array)
            # 상위 4개 인덱스 가져오기
            top_4_foods = [int(e) for e in np.argsort(predictions[0])[-4:]]
            # 상위 4개 확률 가져오기
            top_4_probabilities = [round(float(prob) * 100, 2) for prob in predictions[0][top_4_foods]]

            # 각 이미지에 대한 예측 결과 생성!
            result = {
                'base64_encoded_data': "null",
                'category': category[:category.find('[')],
                'foodnum': top_4_foods[3],
                'candidate1': top_4_foods[2],
                'candidate2': top_4_foods[1],
                'candidate3': top_4_foods[0],
                'predictrate': top_4_probabilities[3],
                'candidate1rate': top_4_probabilities[2],
                'candidate2rate': top_4_probabilities[1],
                'candidate3rate': top_4_probabilities[0],
            }
            results.append(result)

    return JsonResponse({'status': 'success', 'results': results})
