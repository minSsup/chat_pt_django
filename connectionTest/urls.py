from django.urls import path

from connectionTest import views

urlpatterns =[
    path('', views.connectionTest),
]
