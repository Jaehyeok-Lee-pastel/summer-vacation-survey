# surveys/management/commands/export_survey_csv.py
from django.core.management.base import BaseCommand
from django.conf import settings
from surveys.models import Survey
import pandas as pd
import os

class Command(BaseCommand):
    help = '설문 응답 데이터를 CSV 파일로 내보냅니다'
    
    def handle(self, *args, **options):
        # 설문 응답 데이터 조회
        surveys = Survey.objects.all().values(
            'age_group', 'gender', 'vacation_type', 'location_type',
            'domestic_location', 'overseas_location',  # 이 두 줄 추가
            'transportation', 'duration', 'companion', 'cost', 
            'satisfaction', 'next_vacation_type'
        )
        
        if not surveys:
            self.stdout.write(self.style.WARNING('내보낼 설문 데이터가 없습니다.'))
            return
            
        # DataFrame 생성 및 컬럼명 변경
        df = pd.DataFrame(surveys)
        # 구체적인 지역 정보 컬럼 생성
        df['휴가_장소'] = df.apply(lambda row: 
            row['domestic_location'] if row['location_type'] == '국내' and row['domestic_location'] 
            else row['overseas_location'] if row['location_type'] == '해외' and row['overseas_location']
            else row['location_type'], axis=1
        )
        column_mapping = {
            'age_group': '연령대',
            'gender': '성별', 
            'vacation_type': '가장_최근_여름_휴가',
            'location_type': '휴가_장소_국내_해외',
            'transportation': '주요_교통수단',
            'duration': '휴가_기간',
            'companion': '함께한_사람',
            'cost': '총_비용',
            'satisfaction': '만족도',
            'next_vacation_type': '다음_휴가_경험'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 만족도를 문자열로 변환
        satisfaction_map = {1: '매우 불만족', 2: '불만족', 3: '보통', 4: '만족', 5: '매우 만족'}
        df['만족도'] = df['만족도'].map(satisfaction_map)
        
        # CSV 저장
        output_path = getattr(settings, 'SURVEY_CSV_PATH', 'data_analysis/survey_data.csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        self.stdout.write(
            self.style.SUCCESS(f'설문 데이터 {len(df)}개가 {output_path}에 저장되었습니다.')
        )