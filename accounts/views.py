# accounts/views.py

# Django에서 제공하는 기본 함수들을 가져옵니다
from django.shortcuts import render, redirect
# 인증 관련 함수들을 가져옵니다
from django.contrib.auth import login, authenticate, logout
# Django 기본 로그인 폼을 가져옵니다
from django.contrib.auth.forms import AuthenticationForm
# 메시지 기능을 가져옵니다 (성공/실패 알림용)
from django.contrib import messages
# 로그인이 필요한 페이지를 만들기 위한 데코레이터
from django.contrib.auth.decorators import login_required
# AJAX 요청을 위한 추가 import
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import json
# 우리가 만든 커스텀 회원가입 폼을 가져옵니다
from .forms import CustomUserCreationForm

def signup(request):
    """
    회원가입을 처리하는 뷰 함수 (프론트엔드 디자인 통합)
    GET 요청: 회원가입 폼을 보여줍니다
    POST 요청: 입력받은 데이터로 계정을 생성합니다
    """
    
    if request.method == 'POST':
        # 사용자가 회원가입 폼을 제출했을 때
        
        # 제출된 데이터로 폼 객체 생성
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            # 폼 데이터가 유효하면 (모든 검증을 통과하면)
            
            # 새 사용자 계정 생성
            user = form.save()
            
            # 성공 메시지 설정
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}님의 계정이 생성되었습니다! 로그인해주세요.')
            
            # 회원가입 후 로그인 페이지로 이동 (프론트엔드 플로우에 맞춤)
            return redirect('accounts:login')
        
        else:
            # 폼 데이터가 유효하지 않으면 오류 메시지 표시
            messages.error(request, '입력한 정보를 다시 확인해주세요.')
    
    else:
        # GET 요청일 때 (처음 회원가입 페이지에 접속했을 때)
        # 빈 회원가입 폼 생성
        form = CustomUserCreationForm()
    
    # 회원가입 템플릿을 렌더링해서 응답 (새로운 프론트엔드 디자인 적용)
    # form 변수를 템플릿으로 전달
    return render(request, 'accounts/signup.html', {'form': form})

def user_login(request):
    """
    로그인을 처리하는 뷰 함수 (프론트엔드 디자인 통합)
    GET 요청: 로그인 폼을 보여줍니다
    POST 요청: 입력받은 계정 정보로 로그인을 시도합니다
    """
    
    if request.method == 'POST':
        # 사용자가 로그인 폼을 제출했을 때
        
        # Django 기본 로그인 폼 사용 (request와 POST 데이터 전달)
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            # 폼 데이터가 유효하면 (사용자명과 비밀번호가 일치하면)
            
            # 폼에서 검증된 사용자명과 비밀번호 가져오기
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # 인증 시도 (사용자명과 비밀번호가 맞는지 확인)
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # 인증이 성공하면 로그인 처리
                login(request, user)
                
                # 환영 메시지 표시
                messages.success(request, f'{username}님, 환영합니다!')
                
                # 프로필 페이지로 이동 (나중에 설문 페이지로 변경 가능)
                return redirect('accounts:profile')
            else:
                # 인증에 실패하면 오류 메시지 표시
                messages.error(request, '아이디 또는 비밀번호가 잘못되었습니다.')
        
        else:
            # 로그인에 실패하면 오류 메시지 표시
            messages.error(request, '사용자명 또는 비밀번호가 올바르지 않습니다.')
    
    else:
        # GET 요청일 때 (처음 로그인 페이지에 접속했을 때)
        # 빈 로그인 폼 생성
        form = AuthenticationForm()
    
    # 로그인 템플릿을 렌더링해서 응답 (새로운 프론트엔드 디자인 적용)
    return render(request, 'accounts/login.html', {'form': form})

@csrf_exempt
def check_username(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            
            if not username:
                return JsonResponse({'error': 'Username is required'})
            
            if User.objects.filter(username=username).exists():
                return JsonResponse({'available': False})
            else:
                return JsonResponse({'available': True})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'})
    
    return JsonResponse({'error': 'Invalid request method'})

def user_logout(request):
    """
    로그아웃을 처리하는 뷰 함수
    현재 로그인된 사용자를 로그아웃시키고 로그인 페이지로 이동합니다
    """
    # 현재 사용자를 로그아웃 처리
    logout(request)
    
    # 로그아웃 완료 메시지 표시
    messages.info(request, '로그아웃되었습니다.')
    
    # 로그인 페이지로 이동
    return redirect('accounts:login')

@login_required
def profile(request):
    """
    사용자 프로필을 보여주는 뷰 함수
    @login_required 데코레이터: 로그인한 사용자만 접근 가능
    로그인하지 않은 사용자가 접근하면 자동으로 로그인 페이지로 이동
    """
    # 현재 로그인한 사용자의 정보를 템플릿으로 전달
    return render(request, 'accounts/profile.html', {'user': request.user})