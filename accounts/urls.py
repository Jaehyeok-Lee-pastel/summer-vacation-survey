# accounts/urls.py

# Django URL 관련 함수들을 가져옵니다
from django.urls import path
# Django에서 제공하는 기본 인증 뷰들을 가져옵니다
from django.contrib.auth import views as auth_views
# 우리가 만든 뷰 함수들을 가져옵니다
from . import views

# 이 앱의 이름을 지정 (URL 역참조할 때 사용)
app_name = 'accounts'

urlpatterns = [
    # 회원가입 URL
    # http://127.0.0.1:8000/accounts/signup/
    path('signup/', views.signup, name='signup'),
    
    # 로그인 URL  
    # http://127.0.0.1:8000/accounts/login/
    path('login/', views.user_login, name='login'),
    
    # 로그아웃 URL
    # http://127.0.0.1:8000/accounts/logout/
    path('logout/', views.user_logout, name='logout'),
    
    # 프로필 URL
    # http://127.0.0.1:8000/accounts/profile/
    path('profile/', views.profile, name='profile'),
    
    # AJAX 아이디 중복체크 URL (프론트엔드 통합을 위해 추가)
    # http://127.0.0.1:8000/accounts/check-username/
    path('check-username/', views.check_username, name='check_username'),
]