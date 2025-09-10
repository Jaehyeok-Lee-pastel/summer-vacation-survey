from django.http import JsonResponse
from django.db.models import Max
from surveys.models import Survey
from django.views.decorators.csrf import csrf_exempt

# data_analysis/views.py에 추가
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .ml_integration import ml_recommender


def recent_vacation_by_age_activity(request):
    age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]

    # 1. 사용자별 최신 여행 기록 선택
    latest_qs = Survey.objects.values('user_id').annotate(
        latest_id=Max('id')
    ).values_list('latest_id', flat=True)

    recent_qs = Survey.objects.filter(id__in=latest_qs)
    print('recent_qs', recent_qs)
    # 2. 연령대+활동 집계
    count_map = {}
    vacation_labels = [v[0] for v in Survey.VACATION_CHOICES]  # 모델 choices
    for row in recent_qs:
        key = (row.age_group, row.vacation_type)
        count_map[key] = count_map.get(key, 0) + 1

    # 연령대별 총합
    total_map = {age: sum(count_map.get((age, v), 0) for v in vacation_labels) for age in age_labels}

    # 3. datasets 생성
    colors = [
        "#3498db", "#e74c3c", "#2ecc71", "#9b59b6",
        "#f1c40f", "#1abc9c", "#e67e22", "#34495e"
    ]
    datasets = []
    print(vacation_labels)
    for i, vtype in enumerate(vacation_labels):
        data = []
        for age in age_labels:
            total = total_map[age]
            cnt = count_map.get((age, vtype), 0)
            ratio = round(cnt / total * 100, 2) if total else 0.0
            data.append(ratio)
        datasets.append({
            "label": vtype,
            "data": data,
            "backgroundColor": colors[i % len(colors)]
        })
    print(datasets)
    return JsonResponse({
        "labels": age_labels,
        "datasets": datasets,
        "meta": {"unit": "%"}
    })
    
import logging

@csrf_exempt
def vacation_by_age_activity_all(request):
    print('here')
    age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]

    # 1. 모든 레코드 가져오기
    all_qs = Survey.objects.all()
    
    # 2. 연령대+활동 집계
    count_map = {}
    vacation_labels = [v[0] for v in Survey.VACATION_CHOICES]  # 모델 choices
    for row in all_qs:
        key = (row.age_group.strip(), row.vacation_type.strip())
        print('row', row)
        count_map[key] = count_map.get(key, 0) + 1

    # 3. 연령대별 총합
    total_map = {age: sum(count_map.get((age, v), 0) for v in vacation_labels) for age in age_labels}

    # 4. datasets 생성
    colors = [
        "#3498db", "#e74c3c", "#2ecc71", "#9b59b6",
        "#f1c40f", "#1abc9c", "#e67e22", "#34495e"
    ]
    datasets = []
    for i, vtype in enumerate(vacation_labels):
        data = []
        for age in age_labels:
            total = total_map[age]
            cnt = count_map.get((age, vtype), 0)
            ratio = round(cnt / total * 100, 2) if total else 0.0
            data.append(ratio)
        datasets.append({
            "label": vtype,
            "data": data,
            "backgroundColor": colors[i % len(colors)]
        })

    return JsonResponse({
        "labels": age_labels,
        "datasets": datasets,
        "meta": {"unit": "%"}
    })


@csrf_exempt  
def vacation_by_male_only(request):
    """
    남성의 연령대별 선호 활동 통계
    연령대 x 활동 매트릭스 형태로 데이터 반환
    """
    logger = logging.getLogger(__name__)
    # 연령대 라벨
    age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
    
    # 남성 설문 데이터만 필터링
    male_surveys = Survey.objects.filter(gender="남성")
    
    # DB에 실제 있는 vacation type으로 라벨 생성
    vacation_labels = list({row.vacation_type for row in male_surveys})
    vacation_labels.sort()  # 정렬해서 일관성 유지
    
    # 연령대+활동 집계용 딕셔너리
    count_map = {}
    for survey in male_surveys:
        key = (survey.age_group.strip(), survey.vacation_type.strip())
        count_map[key] = count_map.get(key, 0) + 1
    
    # 연령대별 남성 총 응답자 수 계산
    total_by_age = {}
    for age in age_labels:
        total_by_age[age] = sum(count_map.get((age, v), 0) for v in vacation_labels)
    
    # Chart.js용 datasets 생성
    colors = [
        "#3498db",  # 파란색 - 해수욕, 물놀이
        "#e74c3c",  # 빨간색 - 등산, 캠핑
        "#2ecc71",  # 초록색 - 문화생활
        "#9b59b6",  # 보라색 - 도시 관광
        "#f1c40f",  # 노란색 - 휴양·힐링
        "#1abc9c",  # 청록색 - 맛집 투어
        "#e67e22",  # 주황색 - 친척·지인 방문
        "#34495e"   # 진회색 - 기타
    ]
    
    datasets = []
    for i, vacation_type in enumerate(vacation_labels):
        data = []
        for age in age_labels:
            total_count = total_by_age[age]
            activity_count = count_map.get((age, vacation_type), 0)
            # 백분율 계산 (소수점 1자리까지)
            percentage = round(activity_count / total_count * 100, 1) if total_count > 0 else 0.0
            data.append(percentage)
        
        datasets.append({
            "label": vacation_type,
            "data": data,
            "backgroundColor": colors[i % len(colors)],
            "borderColor": colors[i % len(colors)],
            "borderWidth": 1
        })
    
    # 응답 반환
    return JsonResponse({
        "labels": age_labels,
        "datasets": datasets,
        "meta": {
            "unit": "%",
            "gender": "남성",
            "total_by_age": total_by_age,
            "total_male_responses": sum(total_by_age.values()),
            "description": "남성의 연령대별 선호 휴가 활동 통계"
        }
    })


@csrf_exempt  
def vacation_by_female_only(request):
    """여성의 연령대별 선호 활동 통계"""
    try:
        age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
        female_surveys = Survey.objects.filter(gender="여성")
        
        if not female_surveys.exists():
            return JsonResponse({
                "labels": age_labels,
                "datasets": [],
                "meta": {
                    "total_female_responses": 0,
                    "total_by_age": {age: 0 for age in age_labels},
                    "error": "여성 응답자 데이터가 없습니다."
                }
            })
        
        # 활동 종류 추출
        vacation_labels = list({survey.vacation_type.strip() for survey in female_surveys})
        vacation_labels.sort()
        
        # 연령대+활동 집계
        count_map = {}
        for survey in female_surveys:
            key = (survey.age_group.strip(), survey.vacation_type.strip())
            count_map[key] = count_map.get(key, 0) + 1
        
        # 연령대별 총 응답자 수
        total_by_age = {}
        for age in age_labels:
            total_by_age[age] = sum(count_map.get((age, v), 0) for v in vacation_labels)
        
        # 색상 정의
        colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#9b59b6",
            "#f1c40f", "#1abc9c", "#e67e22", "#34495e"
        ]
        
        # 데이터셋 생성
        datasets = []
        for i, vacation_type in enumerate(vacation_labels):
            data = []
            for age in age_labels:
                total_count = total_by_age[age]
                activity_count = count_map.get((age, vacation_type), 0)
                percentage = round(activity_count / total_count * 100, 1) if total_count > 0 else 0.0
                data.append(percentage)
            
            datasets.append({
                "label": vacation_type,
                "data": data,
                "backgroundColor": colors[i % len(colors)],
                "borderColor": colors[i % len(colors)],
                "borderWidth": 1
            })
        
        return JsonResponse({
            "labels": age_labels,
            "datasets": datasets,
            "meta": {
                "unit": "%",
                "gender": "여성",
                "total_by_age": total_by_age,
                "total_female_responses": sum(total_by_age.values()),
                "description": "여성의 연령대별 선호 휴가 활동 통계"
            },
            "success": True
        })
        
    except Exception as e:
        return JsonResponse({
            "labels": age_labels,
            "datasets": [],
            "meta": {
                "error": f"API 오류: {str(e)}",
                "total_female_responses": 0,
                "total_by_age": {age: 0 for age in age_labels}
            },
            "success": False
        })
        
        
@csrf_exempt
def companion_by_age_activity(request):
    """연령대별 함께한 사람 통계"""
    try:
        age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
        all_surveys = Survey.objects.all()
        
        if not all_surveys.exists():
            return JsonResponse({
                "labels": age_labels,
                "datasets": [],
                "meta": {
                    "total_responses": 0,
                    "total_by_age": {age: 0 for age in age_labels},
                    "error": "응답자 데이터가 없습니다."
                }
            })
        
        # 함께한 사람 종류 추출
        companion_labels = list({survey.companion.strip() for survey in all_surveys})
        companion_labels.sort()
        
        # 연령대+함께한사람 집계
        count_map = {}
        for survey in all_surveys:
            key = (survey.age_group.strip(), survey.companion.strip())
            count_map[key] = count_map.get(key, 0) + 1
        
        # 연령대별 총 응답자 수
        total_by_age = {}
        for age in age_labels:
            total_by_age[age] = sum(count_map.get((age, c), 0) for c in companion_labels)
        
        # 색상 정의
        colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#9b59b6",
            "#f1c40f", "#1abc9c", "#e67e22", "#34495e"
        ]
        
        # 데이터셋 생성
        datasets = []
        for i, companion_type in enumerate(companion_labels):
            data = []
            for age in age_labels:
                total_count = total_by_age[age]
                companion_count = count_map.get((age, companion_type), 0)
                percentage = round(companion_count / total_count * 100, 1) if total_count > 0 else 0.0
                data.append(percentage)
            
            datasets.append({
                "label": companion_type,
                "data": data,
                "backgroundColor": colors[i % len(colors)],
                "borderColor": colors[i % len(colors)],
                "borderWidth": 1
            })
        
        return JsonResponse({
            "labels": age_labels,
            "datasets": datasets,
            "meta": {
                "unit": "%",
                "total_by_age": total_by_age,
                "total_responses": sum(total_by_age.values()),
                "description": "연령대별 함께한 사람 통계"
            },
            "success": True
        })
        
    except Exception as e:
        return JsonResponse({
            "labels": age_labels,
            "datasets": [],
            "meta": {
                "error": f"API 오류: {str(e)}",
                "total_responses": 0,
                "total_by_age": {age: 0 for age in age_labels}
            },
            "success": False
        })


@csrf_exempt
def next_vacation_by_age_activity(request):
    """연령대별 희망하는 다음 휴가 통계"""
    try:
        age_labels = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
        all_surveys = Survey.objects.all()
        
        if not all_surveys.exists():
            return JsonResponse({
                "labels": age_labels,
                "datasets": [],
                "meta": {
                    "total_responses": 0,
                    "total_by_age": {age: 0 for age in age_labels},
                    "error": "응답자 데이터가 없습니다."
                }
            })
        
        # 다음 휴가 희망 활동 종류 추출
        next_vacation_labels = list({survey.next_vacation_type.strip() for survey in all_surveys if survey.next_vacation_type})
        next_vacation_labels.sort()
        
        # 연령대+다음휴가희망 집계
        count_map = {}
        for survey in all_surveys:
            if survey.next_vacation_type:  # next_vacation_type이 있는 경우만
                key = (survey.age_group.strip(), survey.next_vacation_type.strip())
                count_map[key] = count_map.get(key, 0) + 1
        
        # 연령대별 총 응답자 수 (next_vacation_type 답변한 사람만)
        total_by_age = {}
        for age in age_labels:
            total_by_age[age] = sum(count_map.get((age, nv), 0) for nv in next_vacation_labels)
        
        # 색상 정의
        colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#9b59b6",
            "#f1c40f", "#1abc9c", "#e67e22", "#34495e"
        ]
        
        # 데이터셋 생성
        datasets = []
        for i, next_vacation_type in enumerate(next_vacation_labels):
            data = []
            for age in age_labels:
                total_count = total_by_age[age]
                next_vacation_count = count_map.get((age, next_vacation_type), 0)
                percentage = round(next_vacation_count / total_count * 100, 1) if total_count > 0 else 0.0
                data.append(percentage)
            
            datasets.append({
                "label": next_vacation_type,
                "data": data,
                "backgroundColor": colors[i % len(colors)],
                "borderColor": colors[i % len(colors)],
                "borderWidth": 1
            })
        
        return JsonResponse({
            "labels": age_labels,
            "datasets": datasets,
            "meta": {
                "unit": "%",
                "total_by_age": total_by_age,
                "total_responses": sum(total_by_age.values()),
                "description": "연령대별 희망하는 다음 휴가 통계"
            },
            "success": True
        })
        
    except Exception as e:
        return JsonResponse({
            "labels": age_labels,
            "datasets": [],
            "meta": {
                "error": f"API 오류: {str(e)}",
                "total_responses": 0,
                "total_by_age": {age: 0 for age in age_labels}
            },
            "success": False
        })


@csrf_exempt
# @login_required
def get_ml_recommendation_api(request):
    try:
        # Django Survey 모델 필드명 그대로 사용
        survey = Survey.objects.get(user=2)
        
        # ML 추천 시스템 호출 (필드명 변환 없이)
        recommendation_result = ml_recommender.get_recommendation_for_user(survey)
        
        if recommendation_result['status'] == 'success':
            # 응답 데이터도 Django 모델 필드명과 매칭
            formatted_recommendations = []
            for rec in recommendation_result['recommendations']:
                formatted_recommendations.append({
                    "similarity_score": rec['similarity_score'],
                    "vacation_type": rec['vacation_type'],  # Django 필드명 그대로
                    "location_type": rec['location_type'],  # Django 필드명 그대로
                    "recommended_destinations": rec['recommended_destinations'],
                    "reference_data": rec['reference_data']
                })
            
            return JsonResponse({
                "success": True,
                "user_profile": {
                    "age_group": survey.age_group,      # Django 필드명
                    "gender": survey.gender,            # Django 필드명
                    "recent_vacation": survey.vacation_type,  # Django 필드명
                    "location_preference": survey.location_type  # Django 필드명
                },
                "recommendations": formatted_recommendations,
                "meta": {
                    "total_recommendations": len(formatted_recommendations),
                    "ml_status": "active",
                    "description": "원본 데이터 기반 여행지 추천"
                }
            })
            
    except Survey.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "survey_not_found",
            "message": "설문조사를 먼저 완료해주세요.",
            "recommendations": [],
            "meta": {
                "total_recommendations": 0,
                "ml_status": "no_data"
            }
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": "api_error",
            "message": f"추천 생성 중 오류가 발생했습니다: {str(e)}",
            "recommendations": [],
            "meta": {
                "total_recommendations": 0,
                "ml_status": "error"
            }
        })