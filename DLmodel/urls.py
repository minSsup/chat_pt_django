from django.urls import path

from DLmodel import views

urlpatterns =[
    path('recommand', views.recommand),
]