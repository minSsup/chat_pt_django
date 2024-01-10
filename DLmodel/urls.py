from django.urls import path

from DLmodel import views

urlpatterns =[
    path('getCal',views.calory),
]