from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # API 상태 확인 (테스트용)
    path('status/', views.api_status, name='api_status'),
    path('register/', views.api_register, name='api_register'),  # ← 추가
    path('login/', views.api_login, name='api_login'),  
]