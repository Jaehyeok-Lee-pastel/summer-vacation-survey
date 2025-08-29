from django.db import models

# surveys/models.py

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Survey(models.Model):
    """
    여름휴가 설문조사 응답을 저장하는 모델
    """
    
    # 1. 연령대 선택지 (확장됨)
    AGE_CHOICES = [
        ('10s', '10대'),
        ('20s', '20대'),
        ('30s', '30대'),
        ('40s', '40대'),
        ('50s', '50대'),
        ('60s', '60대 이상'),
    ]
    
    # 2. 성별 선택지
    GENDER_CHOICES = [
        ('male', '남성'),
        ('female', '여성'),
    ]
    
    # 3. 휴가 유형 선택지
    VACATION_TYPE_CHOICES = [
        ('beach', '해수욕, 물놀이 (바다/섬 여행)'),
        ('outdoor', '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)'),
        ('culture', '문화생활 (전시, 공연, 역사 탐방, 축제 등)'),
        ('city', '도시 관광 (쇼핑, 카페, 시내 구경)'),
        ('healing', '휴양·힐링 (스파, 리조트, 펜션 휴식)'),
        ('food', '맛집 투어 (맛집 탐방, 지역 특산물 체험)'),
        ('visit', '친척·지인 방문'),
        ('other', '기타'),
    ]
    
    # 4-1. 국내 지역 선택지
    DOMESTIC_LOCATION_CHOICES = [
        ('seoul', '서울'),
        ('busan', '부산'),
        ('daegu', '대구'),
        ('daejeon', '대전'),
        ('gwangju', '광주'),
        ('ulsan', '울산'),
        ('incheon', '인천'),
        ('sejong', '세종'),
        ('gangwon', '강원'),
        ('gyeongbuk', '경북'),
        ('gyeongnam', '경남'),
        ('jeonbuk', '전북'),
        ('jeonnam', '전남'),
        ('chungbuk', '충북'),
        ('chungnam', '충남'),
        ('jeju', '제주'),
    ]
    
    # 4-2. 해외 지역 선택지
    OVERSEAS_LOCATION_CHOICES = [
        ('east_asia', '동아시아'),
        ('southeast_asia', '동남아시아'),
        ('west_europe', '서유럽'),
        ('east_europe', '동유럽'),
        ('north_america', '북미'),
        ('south_america', '남미'),
        ('middle_east', '중동'),
        ('oceania', '오세아니아'),
        ('africa', '아프리카'),
    ]
    
    # 5. 교통수단 선택지
    TRANSPORTATION_CHOICES = [
        ('car', '자동차'),
        ('bus', '버스'),
        ('train', '기차'),
        ('airplane', '항공편'),
        ('ship', '배(선박)'),
        ('walk', '도보'),
    ]
    
    # 6. 휴가 기간 선택지
    DURATION_CHOICES = [
        ('1day', '1일'),
        ('2-3days', '2~3일'),
        ('4-6days', '4~6일'),
        ('7-15days', '7일~15일'),
        ('over15days', '15일 이상'),
    ]
    
    # 7. 동행자 선택지
    COMPANION_CHOICES = [
        ('alone', '혼자'),
        ('family', '가족'),
        ('friends', '친구'),
        ('lover', '연인'),
        ('colleagues', '직장 동료'),
        ('club', '동호회'),
        ('other', '기타'),
    ]
    
    # 8. 총 비용 선택지
    COST_CHOICES = [
        ('under10', '10만 원 이하'),
        ('10-30', '10만~30만 원'),
        ('30-50', '30만~50만 원'),
        ('50-100', '50만~100만 원'),
        ('100-200', '100만~200만 원'),
        ('over200', '200만 원 이상'),
    ]
    
    # 9. 만족도 선택지
    SATISFACTION_CHOICES = [
        (5, '매우 만족'),
        (4, '만족'),
        (3, '보통'),
        (2, '불만족'),
        (1, '매우 불만족'),
    ]
    
    # 10. 다음 휴가 희망 활동 선택지 (3번과 동일)
    NEXT_VACATION_CHOICES = [
        ('beach', '바다/섬에서 물놀이'),
        ('outdoor', '산·계곡에서 아웃도어 활동'),
        ('culture', '전시·공연·축제 같은 문화 체험'),
        ('city', '도시 관광 및 쇼핑'),
        ('healing', '휴양·힐링 (스파, 리조트, 펜션 등)'),
        ('food', '맛집 탐방, 지역 특산물 체험'),
        ('visit', '친척·지인 방문'),
        ('other', '기타'),
    ]
    
    # 위치 구분 선택지
    LOCATION_TYPE_CHOICES = [
        ('domestic', '국내'),
        ('overseas', '해외'),
    ]
    
    # ===== 실제 데이터베이스 필드들 =====
    
    # 작성자 정보
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='작성자'
    )
    
    # 1. 연령대 (사용자 모델에서 가져올 수도 있지만 설문 시점의 데이터 보존을 위해 별도 저장)
    age_group = models.CharField(
        max_length=3,
        choices=AGE_CHOICES,
        verbose_name='연령대'
    )
    
    # 2. 성별
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        verbose_name='성별'
    )
    
    # 3. 휴가 유형
    vacation_type = models.CharField(
        max_length=20,
        choices=VACATION_TYPE_CHOICES,
        verbose_name='휴가 유형'
    )
    
    # 4. 휴가 장소 (국내/해외 구분)
    location_type = models.CharField(
        max_length=10,
        choices=LOCATION_TYPE_CHOICES,
        verbose_name='위치 구분'
    )
    
    # 4-1. 국내 지역 (location_type이 'domestic'일 때만 사용)
    domestic_location = models.CharField(
        max_length=20,
        choices=DOMESTIC_LOCATION_CHOICES,
        blank=True,
        null=True,
        verbose_name='국내 지역'
    )
    
    # 4-2. 해외 지역 (location_type이 'overseas'일 때만 사용)
    overseas_location = models.CharField(
        max_length=20,
        choices=OVERSEAS_LOCATION_CHOICES,
        blank=True,
        null=True,
        verbose_name='해외 지역'
    )
    
    # 5. 교통수단
    transportation = models.CharField(
        max_length=20,
        choices=TRANSPORTATION_CHOICES,
        verbose_name='주요 교통수단'
    )
    
    # 6. 휴가 기간
    duration = models.CharField(
        max_length=15,
        choices=DURATION_CHOICES,
        verbose_name='휴가 기간'
    )
    
    # 7. 동행자
    companion = models.CharField(
        max_length=20,
        choices=COMPANION_CHOICES,
        verbose_name='동행자'
    )
    
    # 8. 총 비용
    cost = models.CharField(
        max_length=15,
        choices=COST_CHOICES,
        verbose_name='총 비용'
    )
    
    # 9. 만족도
    satisfaction = models.IntegerField(
        choices=SATISFACTION_CHOICES,
        verbose_name='만족도'
    )
    
    # 10. 다음 휴가 희망 활동
    next_vacation_type = models.CharField(
        max_length=20,
        choices=NEXT_VACATION_CHOICES,
        verbose_name='다음 휴가 희망 활동'
    )
    
    # 설문 작성 시간
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='작성일시'
    )
    
    def __str__(self):
        return f"{self.user.username}의 여름휴가 설문 ({self.created_at.strftime('%Y-%m-%d')})"
    
    def get_location_display(self):
        """
        국내/해외에 따라 적절한 지역명을 반환
        """
        if self.location_type == 'domestic':
            return f"국내 - {self.get_domestic_location_display()}"
        else:
            return f"해외 - {self.get_overseas_location_display()}"
    
    def get_satisfaction_stars(self):
        """
        만족도를 별표로 표시
        """
        return '⭐' * self.satisfaction
    
    class Meta:
        verbose_name = '여름휴가 설문조사'
        verbose_name_plural = '여름휴가 설문조사들'
        ordering = ['-created_at']
        
        # 한 사용자가 중복 설문 작성 방지 (선택사항)
        # unique_together = [['user']]