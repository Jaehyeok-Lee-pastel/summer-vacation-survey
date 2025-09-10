# surveys/ml_mapping.py
"""
Django 모델과 새 ML 시스템 간의 스마트 매핑 유틸리티
"""

class SurveyMLMapper:
    """Django Survey 모델을 새 ML 시스템 형식으로 변환"""
    
    # 🎯 휴가 유형 매핑 테이블
    VACATION_TYPE_MAPPING = {
        '해수욕, 물놀이': '해수욕, 물놀이 (바다/섬 여행)',
        '등산, 캠핑': '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)',
        '맛집 투어': '맛집 투어 (맛집 탐방, 지역 특산물 체험)',
        '도시 관광': '도시 관광 (쇼핑, 카페, 시내 구경)',
        '휴양·힐링': '휴양·힐링 (스파, 리조트, 펜션 휴식)',
        '문화생활': '문화생활 (박물관, 유적지, 공연 관람)',
        '친척·지인 방문': '친척·지인 방문',
        '기타': '기타'
    }
    
    # 🗺️ 지역 분류 매핑
    DOMESTIC_REGION_MAPPING = {
        # 국내 주요 지역 → 동아시아로 통합
        '서울': '동아시아', '부산': '동아시아', '제주': '동아시아',
        '대구': '동아시아', '인천': '동아시아', '광주': '동아시아',
        '대전': '동아시아', '울산': '동아시아', '세종': '동아시아',
        '경기도': '동아시아', '강원도': '동아시아', '충청도': '동아시아',
        '경상도': '동아시아', '전라도': '동아시아', '제주도': '동아시아',
        '강릉': '동아시아', '속초': '동아시아', '전주': '동아시아',
        '경주': '동아시아', '여수': '동아시아', '포항': '동아시아'
    }
    
    OVERSEAS_REGION_MAPPING = {
        # 동아시아
        '일본': '동아시아', '중국': '동아시아', '대만': '동아시아',
        '홍콩': '동아시아', '마카오': '동아시아',
        
        # 동남아시아
        '태국': '동남아시아', '베트남': '동남아시아', '싱가포르': '동남아시아',
        '필리핀': '동남아시아', '인도네시아': '동남아시아', '말레이시아': '동남아시아',
        '캄보디아': '동남아시아', '라오스': '동남아시아', '미얀마': '동남아시아',
        
        # 북미
        '미국': '북미', '캐나다': '북미', '멕시코': '북미',
        
        # 유럽
        '프랑스': '유럽', '영국': '유럽', '독일': '유럽', '이탈리아': '유럽',
        '스페인': '유럽', '네덜란드': '유럽', '스위스': '유럽', '오스트리아': '유럽',
        '체코': '유럽', '그리스': '유럽', '터키': '유럽', '러시아': '유럽',
        
        # 아프리카
        '이집트': '아프리카', '모로코': '아프리카', '남아프리카공화국': '아프리카',
        '케냐': '아프리카', '탄자니아': '아프리카',
        
        # 오세아니아
        '호주': '오세아니아', '뉴질랜드': '오세아니아',
        
        # 기타
        '인도': '기타', '네팔': '기타', '몰디브': '기타', '스리랑카': '기타'
    }
    
    # 🎭 만족도 변환
    SATISFACTION_MAPPING = {
        1: '매우 불만족',
        2: '불만족', 
        3: '보통',
        4: '만족',
        5: '매우 만족'
    }
    
    @classmethod
    def django_to_ml(cls, survey):
        """Django Survey 객체를 ML 형식으로 변환"""
        
        # 휴가 장소 통합 및 지역 분류
        if survey.location_type == '국내':
            # 국내 지역 분류
            domestic_place = survey.domestic_location or '서울'
            vacation_place = cls.DOMESTIC_REGION_MAPPING.get(domestic_place, '동아시아')
        else:  # 해외
            # 해외 지역 분류  
            overseas_place = survey.overseas_location or '일본'
            vacation_place = cls.OVERSEAS_REGION_MAPPING.get(overseas_place, '기타')
        
        return {
            '연령대': survey.age_group,
            '성별': survey.gender,
            '가장_최근_여름_휴가': cls.VACATION_TYPE_MAPPING.get(
                survey.vacation_type, survey.vacation_type
            ),
            '휴가_장소_국내_해외': survey.location_type,
            '휴가_장소': vacation_place,
            '주요_교통수단': survey.transportation,
            '휴가_기간': survey.duration,
            '함께한_사람': survey.companion,
            '총_비용': survey.cost,
            '만족도': cls.SATISFACTION_MAPPING.get(survey.satisfaction, '보통'),
            '다음_휴가_경험': cls.VACATION_TYPE_MAPPING.get(
                survey.next_vacation_type, survey.next_vacation_type
            ),
            'user_id': survey.user.id,
            'username': survey.user.username  # 디버깅용
        }
    
    @classmethod
    def bulk_convert(cls, surveys):
        """여러 Survey 객체를 일괄 변환"""
        return [cls.django_to_ml(survey) for survey in surveys]
    
    @classmethod
    def get_mapping_stats(cls):
        """매핑 통계 정보 반환"""
        return {
            'vacation_types': len(cls.VACATION_TYPE_MAPPING),
            'domestic_regions': len(cls.DOMESTIC_REGION_MAPPING), 
            'overseas_regions': len(cls.OVERSEAS_REGION_MAPPING),
            'satisfaction_levels': len(cls.SATISFACTION_MAPPING)
        }