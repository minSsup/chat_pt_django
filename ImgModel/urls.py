from django.urls import path

from ImgModel import views

urlpatterns =[
    path('findFood', views.find_food),
    path('findFood_for_kakao', views.find_food_for_kakao),
]
