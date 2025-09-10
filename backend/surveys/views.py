import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Survey
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

@csrf_exempt
# @login_required
def survey_api(request):
    """
    HTML 설문과 연동되는 API
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 JSON 형식입니다.'})

    user_id = data.get('user_id')
    try:
        user = User.objects.get(id=1) # << 임시
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': '사용자가 존재하지 않습니다.'})

    # Survey 생성
    print('data',data)
    survey = Survey(
        user=user, 
        age_group=data.get('q1'),
        gender=data.get('q2'),
        vacation_type=data.get('q3'),
        location_type=data.get('q4'),
        domestic_location=data.get('q4-1') if data.get('q4')=='국내' else None,
        overseas_location=data.get('q4-2') if data.get('q4')=='해외' else None,
        transportation=data.get('q5'),
        duration=data.get('q6'),
        companion=data.get('q7'),
        cost=data.get('q8'),
        satisfaction=int(data.get('q9')),  # JS에서 1~5점으로 보내야 함
        next_vacation_type=data.get('q10')
    )
    survey.save()

    return JsonResponse({'success': True, 'message': '설문조사가 저장되었습니다.'})



# surveys/views.py에 추가
from .ml_mapping import SurveyMLMapper
from .utils import generate_ml_compatible_csv


@login_required
def recommendation_view(request):
    """사용자 맞춤 추천 페이지"""
    try:
        # 사용자 설문 데이터 가져오기
        survey = Survey.objects.get(user=request.user)
        
        # ML 형식으로 변환
        ml_user_data = SurveyMLMapper.django_to_ml(survey)
        
        # TODO: ML 추천 시스템과 연동
        # 현재는 변환된 데이터만 표시
        
        context = {
            'survey': survey,
            'ml_data': ml_user_data,  # 디버깅용
            'user': request.user
        }
        
        return render(request, 'surveys/recommendation.html', context)
        
    except Survey.DoesNotExist:
        return render(request, 'surveys/no_survey.html')


def admin_generate_ml_csv(request):
    """관리자용: ML CSV 생성"""
    if not request.user.is_staff:
        return JsonResponse({'error': '권한이 없습니다.'}, status=403)
    
    try:
        csv_path = generate_ml_compatible_csv()
        if csv_path:
            return JsonResponse({
                'status': 'success',
                'message': 'ML 호환 CSV가 성공적으로 생성되었습니다.',
                'csv_path': csv_path
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': '데이터가 부족하거나 CSV 생성에 실패했습니다.'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'오류 발생: {str(e)}'
        })
        
        
        
# surveys/views.py
# 기존 views.py 파일에 아래 코드를 추가하세요
from .ml_service import get_ml_service, is_ml_service_ready
from .models import Survey

@csrf_exempt  # CSRF 토큰 검증 건너뛰기 (API용)
@require_http_methods(["POST"])  # POST 요청만 허용
def get_vacation_recommendations(request):
    """
    사용자 설문 데이터를 받아서 AI 휴가 추천을 반환하는 API
    
    요청 형식 (JSON):
    {
        "age_group": "20대",
        "gender": "여성",
        "recent_vacation_activity": "해수욕, 물놀이",
        ... 기타 설문 항목들
    }
    
    응답 형식 (JSON):
    {
        "success": true,
        "recommendations": [...],
        "similar_users": [...],
        "cost_info": {...}
    }
    """
    try:
        # 1. 요청 데이터 파싱
        data = json.loads(request.body)
        
        # 2. ML 서비스 준비 상태 확인
        if not is_ml_service_ready():
            return JsonResponse({
                'success': False,
                'error': '추천 서비스가 준비되지 않았습니다. 관리자에게 문의하세요.',
                'details': 'ML 모델이 학습되지 않았거나 로드되지 않았습니다.'
            }, status=503)  # 503: Service Unavailable
        
        # 3. 사용자 데이터를 ML 모델이 이해할 수 있는 형식으로 변환
        # HTML form의 name 속성과 ML 모델의 컬럼명을 매핑
        user_data = {
            '연령대': data.get('age_group'),
            '성별': data.get('gender'),
            '가장_최근_여름_휴가': data.get('recent_vacation_activity'),
            '휴가_장소_국내_해외': data.get('vacation_location'),
            '주요_교통수단': data.get('transportation'),
            '휴가_기간': data.get('vacation_duration'),
            '함께한_사람': data.get('companion'),
            '이_비용': data.get('total_cost'),
            '만족도': data.get('satisfaction'),
            '다음_휴가_경험': data.get('next_vacation_preference')
        }
        
        # 4. 필수 필드 검증
        required_fields = ['연령대', '성별', '가장_최근_여름_휴가']
        missing_fields = []
        
        for field in required_fields:
            if not user_data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': '필수 정보가 누락되었습니다.',
                'missing_fields': missing_fields,
                'message': f'다음 항목을 입력해주세요: {", ".join(missing_fields)}'
            }, status=400)  # 400: Bad Request
        
        # 5. ML 서비스로 추천 생성
        ml_service = get_ml_service()
        recommendations = ml_service.get_recommendations(user_data)
        
        # 6. 추천 결과 반환
        return JsonResponse(recommendations)
        
    except json.JSONDecodeError:
        # JSON 파싱 오류
        return JsonResponse({
            'success': False,
            'error': '잘못된 요청 형식입니다.',
            'details': 'JSON 형식이 올바르지 않습니다.'
        }, status=400)
        
    except Exception as e:
        # 기타 예상치 못한 오류
        return JsonResponse({
            'success': False,
            'error': '추천 생성 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)  # 500: Internal Server Error

@csrf_exempt
@require_http_methods(["POST"])
def save_survey_and_get_recommendations(request):
    """
    설문 응답을 데이터베이스에 저장하고 동시에 AI 추천을 생성하는 API
    
    현재 프로젝트의 실제 HTML 구조 (q1~q10)에 맞게 수정된 버전
    """
    try:
        # 1. 요청 데이터 파싱
        data = json.loads(request.body)
        print(f"받은 데이터: {data}")
        
        # # 2. ML 서비스 준비 상태 확인
        # if not is_ml_service_ready():
        #     return JsonResponse({
        #         'success': False,
        #         'error': '추천 서비스가 준비되지 않았습니다.',
        #         'can_save_survey': True,
        #         'message': '설문은 저장되지만 추천은 나중에 제공됩니다.'
        #     }, status=503)
        
        # 3. HTML 폼 데이터 (q1~q10)를 데이터베이스 필드에 매핑
        # 현재 프로젝트의 실제 Survey 모델 구조에 맞게 수정
        try:
            # Survey 모델 import (실제 모델 구조에 맞게 조정)
            from .models import Survey  # 또는 SurveyResponse
            
            # 올바른 Survey 모델 필드명 사용
            survey_response = Survey.objects.create(
                user=User.objects.get(id=2),  # 임시 사용자
                age_group=data.get('q1'),
                gender=data.get('q2'),
                vacation_type=data.get('q3'),           # 올바른 필드명
                location_type=data.get('q4'),           # 올바른 필드명
                domestic_location=data.get('q4-1') if data.get('q4')=='국내' else None,
                overseas_location=data.get('q4-2') if data.get('q4')=='해외' else None,
                transportation=data.get('q5'),
                duration=data.get('q6'),                # 올바른 필드명
                companion=data.get('q7'),
                cost=data.get('q8'),                    # 올바른 필드명
                satisfaction=int(data.get('q9')),
                next_vacation_type=data.get('q10')      # 올바른 필드명
            )
            
            print(f"✅ 설문 응답 저장 완료: ID={survey_response.id}")
            
        except Exception as db_error:
            print(f"❌ 데이터베이스 저장 오류: {db_error}")
            # DB 저장 실패해도 추천은 생성해보기
            survey_response = None
        
        # 4. 저장된 데이터를 ML 모델 형식으로 변환
        # HTML의 q1~q10 값을 ML 모델이 이해하는 한글 키로 변환
        satisfaction_map = {
            1: '매우 불만족',
            2: '불만족', 
            3: '보통',
            4: '만족',
            5: '매우 만족'
        }
        
        location_detail = None
        if data.get('q4') == '국내' and data.get('q4-1'):
            location_detail = data.get('q4-1')  # domestic_location 활용
        elif data.get('q4') == '해외' and data.get('q4-2'):
            location_detail = data.get('q4-2')  # overseas_location 활용

        print('location_detail',location_detail)
        user_data = {
            '연령대': data.get('q1'),
            '성별': data.get('q2'),
            '가장_최근_여름_휴가': data.get('q3'),
            '휴가_장소_국내_해외': data.get('q4'),
            '주요_교통수단': data.get('q5'),
            '휴가_기간': data.get('q6'),
            '함께한_사람': data.get('q7'),
            '이_비용': data.get('q8'),
            '만족도': satisfaction_map.get(data.get('q9'), '보통'),  # 숫자를 문자로 변환
            '다음_휴가_경험': data.get('q10')
        }

        
        print(f"ML 서비스에 전달할 데이터: {user_data}")
        
        # 5. ML 서비스로 추천 생성
        ml_service = get_ml_service()
        recommendations = ml_service.get_recommendations(user_data)
        
        # 6. 새로운 데이터로 ML 모델 업데이트 (선택사항)
        try:
            ml_service.update_model_with_new_data(user_data)
            print("🔄 ML 모델 업데이트 완료")
        except Exception as e:
            print(f"⚠️ ML 모델 업데이트 실패 (추천은 정상 제공): {e}")
        
        # 7. 응답에 추가 정보 포함
        if survey_response:
            recommendations['survey_id'] = survey_response.id
        recommendations['user_name'] = data.get('name', '익명')
        recommendations['message'] = f"{data.get('name', '익명')}님의 맞춤 휴가 추천이 생성되었습니다!"
        
        return JsonResponse(recommendations)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '잘못된 JSON 형식입니다.',
            'details': '요청 데이터를 파싱할 수 없습니다.'
        }, status=400)
        
    except Exception as e:
        print(f"❌ 전체 오류: {e}")
        return JsonResponse({
            'success': False,
            'error': '설문 저장 및 추천 생성 중 오류가 발생했습니다.',
            'details': str(e)
        }, status=500)
