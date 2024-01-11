from django.apps import AppConfig
from keras.models import load_model
import json
from pathlib import Path

class ImgmodelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ImgModel"

    # Keras 모델 초기화
    model = None
    food_names = None
    def ready(self):
        # 모델 로드
        ImgmodelConfig.model = load_model('modelFoodName1_200.h5')
        # JSON 파일 읽기
        with open('food_names.json', 'r', encoding='utf-8') as file:
            ImgmodelConfig.food_names = json.load(file)
