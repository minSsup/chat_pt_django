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
                # Base64 데이터에서 MIME 타입 부분을 제거
                if base64_img.startswith('data:image'):
                    # 'data:image/jpeg;base64,' 부분을 제거
                    header, base64_encoded_data = base64_img.split(';base64,')
                    # Base64 디코딩
                    img_data = base64.b64decode(base64_encoded_data)
                    # 바이너리 데이터를 PIL Image 객체로 변환
                    image = Image.open(io.BytesIO(img_data))
                    image = image.resize((300, 300))  # 모델이 기대하는 입력 크기 (이 경우 300x300)

                    # RGBA 이미지를 RGB로 변환
                    if image.mode != 'RGB':
                        image = image.convert('RGB')

                    # 음식 이름 예측
                    model = apps.ImgmodelConfig.model
                    img_array = np.expand_dims(np.asarray(image), axis=0)
                    predictions = model.predict(img_array)
                    # 상위 4개 인덱스 가져오기
                    top_4_foods = [ int(e) for e in np.argsort(predictions[0])[-4:]]
                    # 상위 4개 확률 가져오기
                    top_4_probabilities = [round(float(prob) * 100, 2) for prob in predictions[0][top_4_foods]]
                    # 가장 확률이 높은 예측 사용
                    primary_prediction = top_4_foods[-1]
                    predicted_foods.append(primary_prediction)

                    # 나머지 3개는 후보로 사용
                    candidate_predictions = top_4_foods[:-1]

                    category = category[:category.find('[')]
                    # 이미지 저장 및 시퀀스 이름 반환
                    file_name = oracle_teamd().up_photo_DB(normal_id=user_name, foodnum=primary_prediction, category=category, mass='300',
                                                           candidate_predictions=candidate_predictions, top_4_probabilities=top_4_probabilities)
                    file_path = f'E:/chat_PT_Spring/src/main/resources/static/images/upphoto/{file_name}.jpg'
                    image.save(file_path)
                    processed_files.append(file_name)
                else:
                    logger.error(f"Invalid image data format for category {category}")
            except Exception as e:
                logger.error(f"Error processing image for category {category}: {e}")

        if processed_files:
            return JsonResponse({'status': 'success', 'files': processed_files, 'foods': predicted_foods})
        else:
            return JsonResponse({'status': 'error', 'message': 'No files processed'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
