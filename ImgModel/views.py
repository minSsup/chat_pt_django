from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from ImgModel import apps
import cv2
import numpy as np
from ImgModel.models import oracle_teamd
import base64
import logging

# @csrf_exempt
# def find_food(request):
#     if request.method == 'POST':
#
#         images_data = request.FILES
#         processed_files = []  # 처리된 파일명을 저장할 리스트
#         predicted_foods = []  # 예측된 음식명을 저장할 리스트
#
#         for category in images_data:
#             for img_file in images_data.getlist(category):
#                 if img_file:
#                     # 이미지 데이터를 NumPy 배열로 읽기
#                     nparr = np.fromstring(img_file.read(), np.uint8)
#                     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#                     # 이미지 현재 크기 확인 및 리사이즈
#                     height, width = image.shape[:2]
#                     if height != 300 or width != 300:
#                         image = cv2.resize(image, (300, 300))
#
#
#                     #음식 이름 예측
#                     model = apps.ImgmodelConfig.model
#                     # if image.mode != 'RGB':
#                     #     image = image.convert('RGB')
#                     img_array = np.asarray(image)
#                     img_array = np.expand_dims(img_array, axis=0)
#
#                     predictions = str(model.predict(img_array).argmax())
#                     food_name = apps.ImgmodelConfig.food_names[predictions]
#                     predicted_foods.append(food_name)
#
#                     # 이미지 저장 및 시퀀스 이름 반환
#                     file_name = oracle_teamd().up_photo_DB(nnum='401', foodnum=predictions, category='아침', mass='300')
#                     file_path = 'E:/chat_PT_Spring/src/main/resources/static/images/upphoto/' + file_name + '.jpg'
#                     print(file_path)
#                     cv2.imwrite(file_path, image)
#
#                     processed_files.append(file_name)
#
#
#
#         if processed_files:
#             return JsonResponse({'status': 'success', 'files': processed_files, 'foods': predicted_foods})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'No files processed'}, status=400)
#

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
        processed_files = []  # 처리된 파일명을 저장할 리스트
        predicted_foods = []  # 예측된 음식명을 저장할 리스트

        # 이미지 데이터 처리
        for category, base64_img in images_data.items():
            try:
                if len(base64_img) % 4 == 0:
                    # Base64 디코딩 및 이미지 데이터 변환
                    img_data = base64.b64decode(base64_img)
                    nparr = np.frombuffer(img_data, np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    # 이미지 현재 크기 확인 및 리사이즈
                    height, width = image.shape[:2]
                    if height != 300 or width != 300:
                        image = cv2.resize(image, (300, 300))

                    # 음식 이름 예측
                    model = apps.ImgmodelConfig.model
                    img_array = np.expand_dims(np.asarray(image), axis=0)
                    predictions = str(model.predict(img_array).argmax())
                    food_name = apps.ImgmodelConfig.food_names[predictions]
                    predicted_foods.append(food_name)

                    category = category[:category.find('[')]
                    # 이미지 저장 및 시퀀스 이름 반환
                    file_name = oracle_teamd().up_photo_DB(normal_id=user_name, foodnum=predictions, category=category, mass='300')
                    file_path = f'E:/chat_PT_Spring/src/main/resources/static/images/upphoto/{file_name}.jpg'
                    cv2.imwrite(file_path, image)
                    processed_files.append(file_name)
                else:
                    logger.error(f"Invalid Base64 data for category {category}")
            except Exception as e:
                logger.error(f"Error processing image for category {category}: {e}")

        if processed_files:
            return JsonResponse({'status': 'success', 'files': processed_files, 'foods': predicted_foods})
        else:
            return JsonResponse({'status': 'error', 'message': 'No files processed'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
