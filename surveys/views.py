from django.shortcuts import render

# surveys/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SurveyForm
from .models import Survey

@login_required
def survey_create(request):
    """
    설문조사 작성 페이지
    로그인한 사용자만 접근 가능
    """
    
    # 이미 설문조사를 작성한 사용자인지 확인 (선택사항)
    existing_survey = Survey.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        # 설문조사 폼이 제출되었을 때
        form = SurveyForm(request.POST)
        
        if form.is_valid():
            # 폼이 유효하면 설문조사 저장
            survey = form.save(commit=False)  # 아직 데이터베이스에 저장하지 않음
            survey.user = request.user        # 현재 로그인한 사용자를 작성자로 설정
            survey.save()                     # 데이터베이스에 저장
            
            # 성공 메시지 표시
            messages.success(request, '설문조사가 성공적으로 제출되었습니다! 감사합니다.')
            
            # 분석 결과 페이지로 이동 (나중에 만들 예정)
            return redirect('accounts:profile')  # 임시로 프로필 페이지로 이동
        
        else:
            # 폼이 유효하지 않으면 오류 메시지 표시
            messages.error(request, '입력한 정보를 다시 확인해주세요.')
    
    else:
        # GET 요청일 때 (설문조사 페이지를 처음 방문했을 때)
        form = SurveyForm()
    
    context = {
        'form': form,
        'existing_survey': existing_survey,
    }
    
    return render(request, 'surveys/survey_create.html', context)

@login_required 
def survey_list(request):
    """
    사용자의 설문조사 목록을 보여주는 페이지 (선택사항)
    """
    surveys = Survey.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'surveys': surveys
    }
    
    return render(request, 'surveys/survey_list.html', context)

def survey_results(request):
    """
    전체 설문조사 결과를 보여주는 페이지 (나중에 팀원 B와 협업)
    """
    # 기본 통계 데이터
    total_surveys = Survey.objects.count()
    
    context = {
        'total_surveys': total_surveys,
    }
    
    return render(request, 'surveys/survey_results.html', context)