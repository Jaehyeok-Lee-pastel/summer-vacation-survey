# surveys/management/commands/create_test_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from surveys.models import Survey
import random

class Command(BaseCommand):
    help = '연령대별 특성을 반영한 테스트 설문 데이터 생성'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터를 모두 삭제하고 새로 생성'
        )
    
    def weighted_choice(self, choices, weights):
        """가중치를 적용한 랜덤 선택"""
        return random.choices(choices, weights=weights, k=1)[0]
    
    def get_age_specific_preferences(self, age_group):
        """연령대별 선호도 가중치 반환"""
        
        vacation_types = ['해수욕, 물놀이', '등산, 캠핑', '문화생활', '도시 관광', 
                         '휴양·힐링', '맛집 투어', '친척·지인 방문', '기타']
        
        if age_group in ['10대', '20대', '30대']:
            # 젊은 층: 물놀이, 도시관광 높음, 등산 낮음
            vacation_weights = [25, 5, 15, 25, 10, 15, 3, 2]  # 물놀이, 도시관광 25% 등산 5%
            location_weights = [60, 40]  # 국내 60%, 해외 40%
        else:  # 40대 이상
            # 중장년층: 등산, 휴양힐링 높음
            vacation_weights = [15, 30, 20, 10, 20, 3, 1, 1]  # 등산 30%, 휴양힐링 20%
            location_weights = [75, 25]  # 국내 75%, 해외 25%
        
        # 동행자 가중치
        companions = ['혼자', '가족', '친구', '연인', '직장 동료', '동호회', '기타']
        
        if age_group == '10대':
            # 10대: 가족여행 비율 높음
            companion_weights = [5, 50, 30, 10, 1, 2, 2]  # 가족 50%
        elif age_group in ['20대', '30대']:
            # 20-30대: 친구, 연인 비율 높음
            companion_weights = [10, 20, 35, 25, 5, 3, 2]  # 친구 35%, 연인 25%
        else:  # 40대 이상
            # 40대 이상: 가족, 동호회 비율 높음
            companion_weights = [15, 40, 15, 15, 5, 8, 2]  # 가족 40%, 동호회 8%
        
        return {
            'vacation_types': vacation_types,
            'vacation_weights': vacation_weights,
            'location_weights': location_weights,
            'companions': companions,
            'companion_weights': companion_weights
        }
    
    def handle(self, *args, **options):
        if options['clear']:
            Survey.objects.all().delete()
            self.stdout.write('기존 설문 데이터를 모두 삭제했습니다.')
        
        # 테스트 사용자 생성
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # 공통 선택지
        age_groups = ['10대', '20대', '30대', '40대', '50대', '60대 이상']
        genders = ['남성', '여성']
        location_types = ['국내', '해외']
        
        domestic_locations = [
            '서울', '부산', '대구', '대전', '광주', '울산', '인천', '세종',
            '강원', '경북', '경남', '전북', '전남', '충북', '충남', '제주'
        ]
        
        overseas_locations = [
            '동아시아', '동남아시아', '서유럽', '동유럽', '북미', 
            '남미', '중동', '오세아니아', '아프리카'
        ]
        
        transportations = ['자동차', '버스', '기차', '항공편', '배', '도보']
        durations = ['1일', '2~3일', '4~6일', '7~15일', '15일 이상']
        costs = [
            '10만 원 이하', '10만~30만 원', '30만~50만 원', 
            '50만~100만 원', '100만~200만 원', '200만 원 이상'
        ]
        
        total_created = 0
        
        for age_group in age_groups:
            self.stdout.write(f'{age_group} 데이터 생성 중...')
            
            # 연령대별 선호도 가져오기
            prefs = self.get_age_specific_preferences(age_group)
            
            for i in range(100):
                # 가중치 적용한 선택
                gender = random.choice(genders)
                vacation_type = self.weighted_choice(prefs['vacation_types'], prefs['vacation_weights'])
                location_type = self.weighted_choice(location_types, prefs['location_weights'])
                companion = self.weighted_choice(prefs['companions'], prefs['companion_weights'])
                
                # 국내/해외에 따른 지역 선택
                if location_type == '국내':
                    domestic_location = random.choice(domestic_locations)
                    overseas_location = None
                    # 국내는 자동차, 기차 비율 높게
                    transportation = self.weighted_choice(
                        transportations, [40, 20, 25, 10, 3, 2]
                    )
                else:
                    domestic_location = None
                    overseas_location = random.choice(overseas_locations)
                    # 해외는 항공편 비율 높게
                    transportation = self.weighted_choice(
                        transportations, [5, 5, 5, 80, 3, 2]
                    )
                
                # 연령대별 기간 선호도
                if age_group in ['10대', '20대']:
                    # 젊은 층: 짧은 기간 선호
                    duration = self.weighted_choice(durations, [5, 40, 35, 15, 5])
                else:
                    # 중장년층: 긴 기간도 가능
                    duration = self.weighted_choice(durations, [5, 25, 30, 25, 15])
                
                # 연령대별 비용 분포
                if age_group in ['10대', '20대']:
                    # 젊은 층: 저예산
                    cost = self.weighted_choice(costs, [15, 35, 25, 15, 7, 3])
                elif age_group in ['30대', '40대']:
                    # 중년층: 중간~고예산
                    cost = self.weighted_choice(costs, [5, 20, 25, 30, 15, 5])
                else:
                    # 50대 이상: 고예산 가능
                    cost = self.weighted_choice(costs, [5, 15, 20, 25, 20, 15])
                
                # 만족도 (연령대별 약간의 차이)
                if age_group in ['10대', '20대', '30대']:
                    satisfaction = self.weighted_choice([1,2,3,4,5], [2, 5, 15, 45, 33])  # 젊은 층 만족도 높음
                else:
                    satisfaction = self.weighted_choice([1,2,3,4,5], [3, 8, 20, 40, 29])  # 중장년층 약간 보수적
                
                # 다음 휴가 계획 (현재와 비슷하거나 발전된 형태)
                next_vacation_type = self.weighted_choice(prefs['vacation_types'], prefs['vacation_weights'])
                
                # 설문 데이터 생성
                Survey.objects.create(
                    user=test_user,
                    age_group=age_group,
                    gender=gender,
                    vacation_type=vacation_type,
                    location_type=location_type,
                    domestic_location=domestic_location,
                    overseas_location=overseas_location,
                    transportation=transportation,
                    duration=duration,
                    companion=companion,
                    cost=cost,
                    satisfaction=satisfaction,
                    next_vacation_type=next_vacation_type
                )
                
                total_created += 1
            
            self.stdout.write(f'{age_group} 100개 완료')
        
        self.stdout.write(
            self.style.SUCCESS(f'총 {total_created}개 현실적인 테스트 데이터 생성 완료!')
        )
        
        # 생성된 데이터 분석
        self.print_data_analysis()
    
    def print_data_analysis(self):
        """생성된 데이터 분석 결과 출력"""
        self.stdout.write('\n=== 생성된 데이터 분석 ===')
        
        # 연령대별 데이터 수
        age_groups = ['10대', '20대', '30대', '40대', '50대', '60대 이상']
        for age_group in age_groups:
            count = Survey.objects.filter(age_group=age_group).count()
            self.stdout.write(f'{age_group}: {count}개')
        
        # 전체 국내/해외 비율
        total = Survey.objects.count()
        domestic = Survey.objects.filter(location_type='국내').count()
        overseas = Survey.objects.filter(location_type='해외').count()
        self.stdout.write(f'\n전체 지역 분포:')
        self.stdout.write(f'  국내: {domestic}개 ({domestic/total*100:.1f}%)')
        self.stdout.write(f'  해외: {overseas}개 ({overseas/total*100:.1f}%)')
        
        # 젊은 층 vs 중장년층 휴가 유형 분포
        young = Survey.objects.filter(age_group__in=['10대', '20대', '30대'])
        old = Survey.objects.filter(age_group__in=['40대', '50대', '60대 이상'])
        
        self.stdout.write(f'\n젊은 층(10-30대) 휴가 유형:')
        young_vacation_types = young.values_list('vacation_type', flat=True)
        for vtype in ['해수욕, 물놀이', '도시 관광', '등산, 캠핑']:
            count = list(young_vacation_types).count(vtype)
            self.stdout.write(f'  {vtype}: {count}개 ({count/young.count()*100:.1f}%)')
        
        self.stdout.write(f'\n중장년층(40대+) 휴가 유형:')
        old_vacation_types = old.values_list('vacation_type', flat=True)
        for vtype in ['등산, 캠핑', '휴양·힐링', '해수욕, 물놀이']:
            count = list(old_vacation_types).count(vtype)
            self.stdout.write(f'  {vtype}: {count}개 ({count/old.count()*100:.1f}%)')
        
        # 10대 가족여행 비율
        teen_family = Survey.objects.filter(age_group='10대', companion='가족').count()
        teen_total = Survey.objects.filter(age_group='10대').count()
        self.stdout.write(f'\n10대 가족여행 비율: {teen_family}개 ({teen_family/teen_total*100:.1f}%)')