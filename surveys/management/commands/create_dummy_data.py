# surveys/management/commands/create_dummy_data.py

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from surveys.models import Survey

User = get_user_model()

class Command(BaseCommand):
    help = '설문조사 더미 데이터 50개를 생성합니다'
    
    def handle(self, *args, **options):
        # 기존 설문 데이터 개수 확인
        existing_count = Survey.objects.count()
        self.stdout.write(f'현재 설문 데이터: {existing_count}개')
        
        # 더미 사용자들 생성 (설문 작성자용)
        dummy_users = []
        for i in range(20):  # 20명의 더미 사용자 생성
            username = f'user{i+1:02d}'
            email = f'user{i+1:02d}@test.com'
            
            # 이미 존재하는 사용자인지 확인
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'age_group': random.choice(['10s', '20s', '30s', '40s', '50s', '60s'])
                }
            )
            dummy_users.append(user)
            
            if created:
                user.set_password('testpass123')
                user.save()
        
        self.stdout.write(f'더미 사용자 {len(dummy_users)}명 준비 완료')
        
        # 현실적인 더미 데이터 생성
        dummy_data_list = []
        
        for i in range(50):
            # 랜덤하지만 현실적인 데이터 조합 생성
            age_group = random.choice(['10s', '20s', '30s', '40s', '50s', '60s'])
            
            # 나이대에 따른 경향성 반영
            if age_group in ['10s', '20s']:
                vacation_types = ['beach', 'outdoor', 'culture', 'city']
                companions = ['friends', 'family', 'lover']
                costs = ['under10', '10-30', '30-50']
            elif age_group in ['30s', '40s']:
                vacation_types = ['beach', 'healing', 'culture', 'visit']
                companions = ['family', 'lover', 'friends']
                costs = ['30-50', '50-100', '100-200']
            else:  # 50s, 60s
                vacation_types = ['healing', 'culture', 'visit', 'food']
                companions = ['family', 'lover', 'club']
                costs = ['50-100', '100-200', 'over200']
            
            # 국내/해외 비율 조정 (국내 70%, 해외 30%)
            location_type = random.choices(['domestic', 'overseas'], weights=[70, 30])[0]
            
            # 휴가 유형에 따른 만족도 경향성
            vacation_type = random.choice(vacation_types)
            if vacation_type in ['beach', 'healing']:
                satisfaction = random.choices([3, 4, 5], weights=[20, 40, 40])[0]
            elif vacation_type in ['culture', 'city']:
                satisfaction = random.choices([2, 3, 4, 5], weights=[10, 30, 40, 20])[0]
            else:
                satisfaction = random.choices([2, 3, 4, 5], weights=[15, 35, 35, 15])[0]
            
            # 비용에 따른 기간 조정
            cost = random.choice(costs)
            if cost in ['under10', '10-30']:
                duration = random.choice(['1day', '2-3days'])
            elif cost in ['30-50', '50-100']:
                duration = random.choice(['2-3days', '4-6days'])
            else:
                duration = random.choice(['4-6days', '7-15days', 'over15days'])
            
            dummy_data = {
                'user': random.choice(dummy_users),
                'age_group': age_group,
                'gender': random.choice(['male', 'female']),
                'vacation_type': vacation_type,
                'location_type': location_type,
                'domestic_location': random.choice([
                    'seoul', 'busan', 'jeju', 'gangwon', 'gyeongnam', 
                    'jeonnam', 'chungnam', 'gyeongbuk'
                ]) if location_type == 'domestic' else None,
                'overseas_location': random.choice([
                    'east_asia', 'southeast_asia', 'west_europe', 
                    'north_america', 'oceania'
                ]) if location_type == 'overseas' else None,
                'transportation': self.get_transportation_by_location(location_type),
                'duration': duration,
                'companion': random.choice(companions),
                'cost': cost,
                'satisfaction': satisfaction,
                'next_vacation_type': random.choice([
                    'beach', 'outdoor', 'culture', 'city', 
                    'healing', 'food', 'visit', 'other'
                ])
            }
            
            dummy_data_list.append(Survey(**dummy_data))
        
        # 데이터베이스에 벌크 생성
        Survey.objects.bulk_create(dummy_data_list)
        
        # 결과 출력
        final_count = Survey.objects.count()
        created_count = final_count - existing_count
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ 더미 데이터 {created_count}개 생성 완료! (총 {final_count}개)'
            )
        )
        
        # 간단한 통계 출력
        self.print_basic_stats()
    
    def get_transportation_by_location(self, location_type):
        """위치에 따른 현실적인 교통수단 선택"""
        if location_type == 'domestic':
            return random.choices(
                ['car', 'bus', 'train', 'airplane'],
                weights=[40, 25, 20, 15]
            )[0]
        else:  # overseas
            return random.choices(
                ['airplane', 'ship'],
                weights=[90, 10]
            )[0]
    
    def print_basic_stats(self):
        """생성된 데이터의 기본 통계 출력"""
        total = Survey.objects.count()
        by_age = Survey.objects.values('age_group').distinct().count()
        by_location = Survey.objects.filter(location_type='domestic').count()
        
        self.stdout.write('\n📊 생성된 데이터 통계:')
        self.stdout.write(f'   총 설문 수: {total}개')
        self.stdout.write(f'   연령대 종류: {by_age}개')
        self.stdout.write(f'   국내 여행: {by_location}개')
        self.stdout.write(f'   해외 여행: {total - by_location}개')
        self.stdout.write('\n🎯 이제 팀원 B가 데이터 분석을 시작할 수 있습니다!')