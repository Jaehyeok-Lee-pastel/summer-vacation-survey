from django.core.management.base import BaseCommand
from surveys.models import Survey

class Command(BaseCommand):
    help = 'ML 시스템 데이터 준비'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-only', 
            action='store_true',
            help='매핑 테스트만 실행'
        )
        
    def handle(self, *args, **options):
        self.stdout.write('ML 시스템 데이터 준비 시작!')
        
        # 현재 데이터 상태 확인
        total_surveys = Survey.objects.count()
        self.stdout.write(f'총 설문 응답: {total_surveys}개')
        
        if total_surveys == 0:
            self.stdout.write('설문 데이터가 없습니다.')
            return
        
        # 매핑 테스트
        try:
            from surveys.utils import test_ml_mapping
            if test_ml_mapping():
                self.stdout.write('매핑 테스트 통과!')
            else:
                self.stdout.write('매핑 테스트 실패!')
                return
        except ImportError as e:
            self.stdout.write(f'임포트 오류: {e}')
            return
        
        # 테스트만 실행
        if options['test_only']:
            self.stdout.write('테스트 완료!')
            return
        
        # CSV 생성
        try:
            from surveys.utils import generate_ml_compatible_csv
            csv_path = generate_ml_compatible_csv()
            if csv_path:
                self.stdout.write(f'CSV 생성 성공: {csv_path}')
            else:
                self.stdout.write('CSV 생성 실패!')
        except Exception as e:
            self.stdout.write(f'오류 발생: {e}')
        
        self.stdout.write('작업 완료!')