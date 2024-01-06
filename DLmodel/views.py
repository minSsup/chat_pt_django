from django.shortcuts import render

from DLmodel.models import oracle_teamd
from django.http import JsonResponse, HttpResponse
import json  # JSON 데이터를 다루기 위한 모듈
import pandas as pd

# Create your views here.
def gogojsjs(request):
    if request.method == 'GET':
        modelaccess = oracle_teamd().origin_DB()
        print(f'DB접근 완료 {type(modelaccess)}')

        resJson = type(modelaccess)

        return JsonResponse(resJson, json_dumps_params={'ensure_ascii': False}, safe=False)
