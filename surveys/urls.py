# surveys/urls.py (새 파일)

from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # 설문조사 작성 페이지
    # http://127.0.0.1:8000/surveys/create/
    path('create/', views.survey_create, name='create'),
    
    # 내 설문조사 목록 페이지
    # http://127.0.0.1:8000/surveys/list/
    path('list/', views.survey_list, name='list'),
    
    # 설문조사 결과 페이지 
    # http://127.0.0.1:8000/surveys/results/
    path('results/', views.survey_results, name='results'),
]