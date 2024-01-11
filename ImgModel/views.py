from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.http import JsonResponse
from ImgModel import apps
import cv2
import numpy as np
from ImgModel.models import oracle_teamd
from PIL import Image

@csrf_exempt
def find_food(request):
    if request.method == 'POST':
        images_data = request.FILES
        processed_files = []  # 처리된 파일명을 저장할 리스트
        predicted_foods = []  # 예측된 음식명을 저장할 리스트

        for category in images_data:
            for img_file in images_data.getlist(category):
                if img_file:
                    # 이미지 데이터를 NumPy 배열로 읽기
                    nparr = np.fromstring(img_file.read(), np.uint8)
                    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    # 이미지 현재 크기 확인 및 리사이즈
                    height, width = image.shape[:2]
                    if height != 300 or width != 300:
                        image = cv2.resize(image, (300, 300))


                    #음식 이름 예측
                    model = apps.ImgmodelConfig.model
                    # if image.mode != 'RGB':
                    #     image = image.convert('RGB')
                    img_array = np.asarray(image)
                    img_array = np.expand_dims(img_array, axis=0)

                    predictions = str(model.predict(img_array).argmax())
                    food_name = apps.ImgmodelConfig.food_names[predictions]
                    predicted_foods.append(food_name)

                    # 이미지 저장 및 시퀀스 이름 반환
                    file_name = oracle_teamd().up_photo_DB(nnum='401', foodnum=predictions, category='아침', mass='300')
                    file_path = 'E:/chat_PT_Spring/src/main/resources/static/images/upphoto/' + file_name + '.jpg'
                    print(file_path)
                    cv2.imwrite(file_path, image)

                    processed_files.append(file_name)



        if processed_files:
            return JsonResponse({'status': 'success', 'files': processed_files, 'foods': predicted_foods})
        else:
            return JsonResponse({'status': 'error', 'message': 'No files processed'}, status=400)

