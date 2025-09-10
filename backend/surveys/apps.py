# surveys/apps.py (ML 서비스 자동 초기화)
from django.apps import AppConfig

class SurveysConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'surveys'
    
    def ready(self):
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            return
            
        try:
            from .ml_service import initialize_ml_service
            
            print("=" * 50)
            print("Django 서버 시작: ML 서비스 초기화 중...")
            print("=" * 50)
            
            initialize_ml_service()
            
            print("=" * 50)
            print("ML 서비스 초기화 완료!")
            print("=" * 50)
            
        except Exception as e:
            print("=" * 50)
            print(f"⚠️ ML 서비스 초기화 실패: {e}")
            print("추천 기능은 사용할 수 없지만 다른 기능은 정상 작동합니다.")
            print("=" * 50)