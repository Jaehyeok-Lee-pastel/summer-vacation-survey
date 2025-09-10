# surveys/management/commands/train_ml_model.py
from django.core.management.base import BaseCommand
from surveys.ml_service import get_ml_service
from django.conf import settings
import os

class Command(BaseCommand):
    help = '머신러닝 모델을 학습시킵니다'
    
    def handle(self, *args, **options):
        csv_path = getattr(settings, 'SURVEY_CSV_PATH', 'data_analysis/survey_data.csv')
        
        if not os.path.exists(csv_path):
            self.stdout.write(
                self.style.ERROR(f'CSV 파일을 찾을 수 없습니다: {csv_path}')
            )
            self.stdout.write('먼저 다음 명령어를 실행하세요:')
            self.stdout.write('python manage.py export_survey_csv')
            return
        
        self.stdout.write('머신러닝 모델 학습을 시작합니다...')
        
        ml_service = get_ml_service()
        success = ml_service.train_model(csv_path)
        
        if success:
            self.stdout.write(self.style.SUCCESS('모델 학습이 완료되었습니다!'))
        else:
            self.stdout.write(self.style.ERROR('모델 학습에 실패했습니다.'))