from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # API 상태 확인 (테스트용)
    path('surveys/', views.survey_api, name='survey_api'),
    # path('register/', views.api_register, name='api_register'),  # ← 추가
    path('data/survey-and-recommendations/', views.save_survey_and_get_recommendations, name='survey_and_recommendations')
]