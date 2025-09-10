# surveys/ml_service.py
# 머신러닝 서비스를 Django에서 쉽게 사용할 수 있도록 관리하는 모듈

import os
from django.conf import settings
from .vacation_recommender import VacationRecommendationService

# 전역 변수: 서버 전체에서 하나의 ML 서비스 인스턴스만 사용
# 이렇게 하면 메모리 효율적이고, 모델을 한 번만 로드하면 됩니다
vacation_service = None

def initialize_ml_service():
    """
    서버 시작 시 머신러닝 모델을 초기화하는 함수
    
    Returns:
        VacationRecommendationService: 초기화된 ML 서비스 객체
    """
    global vacation_service
    
    # 이미 초기화되었으면 다시 하지 않음 (중복 방지)
    if vacation_service is None:
        print("🤖 머신러닝 서비스 초기화 중...")
        
        # settings.py에서 설정한 모델 저장 경로 가져오기
        model_dir = getattr(settings, 'ML_MODEL_DIR', 
                           os.path.join(settings.BASE_DIR, 'ml_models'))
        
        # VacationRecommendationService 객체 생성
        vacation_service = VacationRecommendationService(model_dir=model_dir)
        
        # CSV 파일 경로 설정
        csv_path = getattr(settings, 'SURVEY_CSV_PATH',
                          os.path.join(settings.BASE_DIR, 'data', 'survey_data.csv'))
        
        # 기존에 학습된 모델이 있는지 확인하고 로드 시도
        if not vacation_service.load_pretrained_model():
            print("📚 기존 학습 모델이 없어서 새로 학습을 시도합니다...")
            
            # CSV 파일이 존재하는지 확인
            if os.path.exists(csv_path):
                print(f"📄 CSV 파일 발견: {csv_path}")
                # 새로 모델 학습
                success = vacation_service.train_model(csv_path)
                if success:
                    print("✅ 모델 학습 완료!")
                else:
                    print("❌ 모델 학습 실패!")
            else:
                print(f"⚠️ CSV 파일을 찾을 수 없습니다: {csv_path}")
                print("설문 데이터를 먼저 수집한 후 'python manage.py export_survey_csv' 명령어를 실행하세요")
        else:
            print("✅ 기존 학습 모델 로드 완료!")
    
    return vacation_service

def get_ml_service():
    """
    ML 서비스 인스턴스를 반환하는 함수
    다른 파일에서 이 함수를 호출하여 ML 서비스를 사용합니다
    
    Returns:
        VacationRecommendationService: ML 서비스 객체
    """
    global vacation_service
    
    # 아직 초기화되지 않았으면 초기화 실행
    if vacation_service is None:
        vacation_service = initialize_ml_service()
    
    return vacation_service

def is_ml_service_ready():
    """
    ML 서비스가 추천을 생성할 준비가 되었는지 확인하는 함수
    
    Returns:
        bool: 준비되었으면 True, 아니면 False
    """
    service = get_ml_service()
    return service is not None and service.is_trained