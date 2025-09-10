# surveys/utils.py - 실제 설문 선택지 반영
import pandas as pd
import os
from django.conf import settings
from datetime import datetime
from .models import Survey

def generate_ml_compatible_csv():
    """ML 호환 CSV 생성 - 실제 설문 선택지 반영"""
    print("ML 호환 CSV 생성 시작...")
    
    surveys = Survey.objects.all().select_related('user')
    if not surveys.exists():
        print("설문 데이터가 없습니다!")
        return None
    
    print(f"총 {surveys.count()}개 설문 응답 변환 중...")
    
    # 휴가 유형 매핑 (ML 시스템 요구사항)
    vacation_mapping = {
        '해수욕, 물놀이': '해수욕, 물놀이 (바다/섬 여행)',
        '등산, 캠핑': '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)',
        '맛집 투어': '맛집 투어 (맛집 탐방, 지역 특산물 체험)',
        '도시 관광': '도시 관광 (쇼핑, 카페, 시내 구경)',
        '휴양·힐링': '휴양·힐링 (스파, 리조트, 펜션 휴식)',
        '문화생활': '문화생활 (박물관, 유적지, 공연 관람)',
        '친척·지인 방문': '친척·지인 방문',
        '기타': '기타'
    }
    
    satisfaction_mapping = {
        1: '매우 불만족', 2: '불만족', 3: '보통', 4: '만족', 5: '매우 만족'
    }
    
    data_list = []
    for survey in surveys:
        # 휴가 장소 - 설문 선택지 그대로 사용
        if survey.location_type == '국내':
            # 국내: 서울, 부산, 대구, 대전, 광주, 울산, 인천, 세종, 강원, 경북, 경남, 전북, 전남, 충북, 충남, 제주
            vacation_place = survey.domestic_location or '서울'
        else:  # 해외
            # 해외: 동아시아, 동남아시아, 서유럽, 동유럽, 북미, 남미, 중동, 오세아니아, 아프리카
            vacation_place = survey.overseas_location or '동아시아'
        
        row_data = {
            '연령대': survey.age_group,
            '성별': survey.gender,
            '가장_최근_여름_휴가': vacation_mapping.get(survey.vacation_type, survey.vacation_type),
            '휴가_장소_국내_해외': survey.location_type,
            '휴가_장소': vacation_place,  # 설문 선택지 그대로
            '주요_교통수단': survey.transportation,
            '휴가_기간': survey.duration,
            '함께한_사람': survey.companion,
            '총_비용': survey.cost,
            '만족도': satisfaction_mapping.get(survey.satisfaction, '보통'),
            '다음_휴가_경험': vacation_mapping.get(survey.next_vacation_type, survey.next_vacation_type),
            'user_id': survey.user.id,
            'username': survey.user.username
        }
        data_list.append(row_data)
    
    df = pd.DataFrame(data_list)
    df.fillna('기타', inplace=True)
    
    # 결과 확인
    print("설문 선택지 기반 결과:")
    print("국내 지역:")
    domestic_places = df[df['휴가_장소_국내_해외'] == '국내']['휴가_장소'].value_counts()
    print(domestic_places.to_dict())
    print("\n해외 지역:")
    overseas_places = df[df['휴가_장소_국내_해외'] == '해외']['휴가_장소'].value_counts()
    print(overseas_places.to_dict())
    
    # CSV 저장
    data_dir = os.path.join(settings.BASE_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f'ml_survey_data_{timestamp}.csv'
    csv_path = os.path.join(data_dir, csv_filename)
    
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\nCSV 생성 완료: {csv_path}")
    print(f"데이터 크기: {df.shape}")
    return csv_path