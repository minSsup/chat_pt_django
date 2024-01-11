from django.urls import path

from ImgModel import views

urlpatterns =[
    path('findFood', views.find_food),
]
