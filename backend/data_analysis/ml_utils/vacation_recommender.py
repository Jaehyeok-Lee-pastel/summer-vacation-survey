# 📁 django_compatible_recommender.py
# Django CSV 데이터 구조에 맞춘 코사인 유사도 기반 여름 휴가 추천 시스템

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import pickle
import os
from datetime import datetime

class DjangoCompatibleRecommender:
    def __init__(self):
        self.full_encoded_df = None
        self.features_encoded = None
        self.original_df = None
        self.feature_columns = None
        
        # Django CSV 구조에 맞춘 핵심 특징 선택
        self.selected_features = [
            '연령대', '성별', '함께한_사람', 
            '휴가_장소_국내_해외', '가장_최근_여름_휴가'
        ]
        
        # Django 모델 선택지에 맞춘 추천 목적지 데이터베이스
        self.destinations = {
            '해수욕, 물놀이 (바다/섬 여행)': {
                '국내': ['부산', '제주', '강원', '경남'],
                '해외': ['동아시아', '동남아시아', '오세아니아']
            },
            '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)': {
                '국내': ['강원', '경북', '전북', '충북'],
                '해외': ['북미', '유럽', '오세아니아']
            },
            '도시 관광 (쇼핑, 카페, 시내 구경)': {
                '국내': ['서울', '부산', '대구', '인천'],
                '해외': ['동아시아', '서유럽', '북미']
            },
            '휴양·힐링 (스파, 리조트, 펜션 휴식)': {
                '국내': ['제주', '강원', '경남', '전남'],
                '해외': ['동남아시아', '오세아니아', '서유럽']
            },
            '맛집 투어 (맛집 탐방, 지역 특산물 체험)': {
                '국내': ['전북', '경북', '전남', '충남'],
                '해외': ['동아시아', '동남아시아', '서유럽']
            },
            '문화생활 (박물관, 유적지, 공연 관람)': {
                '국내': ['경북', '전북', '충남', '서울'],
                '해외': ['서유럽', '동아시아', '북미']
            },
            '친척·지인 방문': {
                '국내': ['서울', '부산', '대구', '광주'],
                '해외': ['동아시아', '북미', '서유럽']
            }
        }
    
    def load_and_preprocess_data(self, csv_path):
        """Django에서 생성된 CSV 파일 로드 및 전처리"""
        print(f"📂 Django CSV 데이터 로딩: {csv_path}")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
        
        # 데이터 로드
        self.original_df = pd.read_csv(csv_path)
        print(f"✅ 데이터 로드 완료")
        print(f"📊 데이터 크기: {self.original_df.shape[0]}행 {self.original_df.shape[1]}열")
        print(f"📋 컬럼: {self.original_df.columns.tolist()}")
        
        # Django 데이터 품질 확인
        print("\n📋 Django 데이터 미리보기:")
        for col in ['연령대', '성별', '가장_최근_여름_휴가', '휴가_장소']:
            if col in self.original_df.columns:
                unique_vals = self.original_df[col].unique()[:5]
                print(f"  {col}: {unique_vals}")
        
        # 결측값 처리
        missing_data = self.original_df.isnull().sum()
        if missing_data.any():
            print(f"⚠️ 결측값 발견:")
            for col, count in missing_data[missing_data > 0].items():
                print(f"   {col}: {count}개")
                self.original_df[col] = self.original_df[col].fillna('기타')
        
        # 전체 데이터 원-핫 인코딩
        print("🔄 Django 데이터 원-핫 인코딩 중...")
        self.full_encoded_df = pd.get_dummies(self.original_df)
        print(f"✅ 인코딩 완료: {len(self.full_encoded_df.columns)}개 특성")
        
        # 핵심 특징 선택
        print(f"🎯 핵심 특징 선택: {self.selected_features}")
        
        available_features = [feat for feat in self.selected_features 
                             if feat in self.original_df.columns]
        
        if len(available_features) != len(self.selected_features):
            missing_features = set(self.selected_features) - set(available_features)
            print(f"⚠️ 누락된 특징: {missing_features}")
            self.selected_features = available_features
        
        # 선택된 특징으로 인코딩
        features_df = self.original_df[self.selected_features]
        self.features_encoded = pd.get_dummies(features_df)
        self.feature_columns = self.features_encoded.columns.tolist()
        
        print(f"✅ 특징 인코딩 완료: {len(self.features_encoded.columns)}개 특성")
        
        return self.original_df
    
    def django_survey_to_ml_format(self, survey_data):
        """Django Survey 모델 데이터를 ML 형식으로 변환"""
        # Django 모델에서 받은 데이터를 ML 시스템 형식으로 변환
        if hasattr(survey_data, 'age_group'):  # Django 모델 객체인 경우
            return {
                '연령대': survey_data.age_group,
                '성별': survey_data.gender,
                '가장_최근_여름_휴가': self._map_vacation_type(survey_data.vacation_type),
                '휴가_장소_국내_해외': survey_data.location_type,
                '휴가_장소': self._get_vacation_place(survey_data),
                '주요_교통수단': survey_data.transportation,
                '휴가_기간': survey_data.duration,
                '함께한_사람': survey_data.companion,
                '총_비용': survey_data.cost,
                '만족도': self._map_satisfaction(survey_data.satisfaction),
                '다음_휴가_경험': self._map_vacation_type(survey_data.next_vacation_type)
            }
        else:  # 이미 딕셔너리 형태인 경우
            return survey_data
    
    def _map_vacation_type(self, django_type):
        """Django 휴가 유형을 ML 형식으로 매핑"""
        mapping = {
            '해수욕, 물놀이': '해수욕, 물놀이 (바다/섬 여행)',
            '등산, 캠핑': '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)',
            '맛집 투어': '맛집 투어 (맛집 탐방, 지역 특산물 체험)',
            '도시 관광': '도시 관광 (쇼핑, 카페, 시내 구경)',
            '휴양·힐링': '휴양·힐링 (스파, 리조트, 펜션 휴식)',
            '문화생활': '문화생활 (박물관, 유적지, 공연 관람)',
            '친척·지인 방문': '친척·지인 방문',
            '기타': '기타'
        }
        return mapping.get(django_type, django_type)
    
    def _get_vacation_place(self, survey_data):
        """Django 모델에서 휴가 장소 추출"""
        if survey_data.location_type == '국내':
            return survey_data.domestic_location or '서울'
        else:
            return survey_data.overseas_location or '동아시아'
    
    def _map_satisfaction(self, satisfaction_int):
        """Django 만족도 숫자를 텍스트로 변환"""
        mapping = {1: '매우 불만족', 2: '불만족', 3: '보통', 4: '만족', 5: '매우 만족'}
        return mapping.get(satisfaction_int, '보통')
    
    def find_similar_users(self, new_user_data, top_k=5):
        """새로운 사용자와 유사한 고객 찾기"""
        print("🔍 Django 사용자와 유사한 고객 검색 중...")
        
        if self.features_encoded is None:
            raise ValueError("❌ 데이터가 로드되지 않았습니다.")
        
        # Django 데이터를 ML 형식으로 변환
        ml_user_data = self.django_survey_to_ml_format(new_user_data)
        
        print(f"👤 변환된 사용자 데이터:")
        for key, value in ml_user_data.items():
            if key in self.selected_features:
                print(f"   {key}: {value}")
        
        # 새로운 사용자 데이터를 DataFrame으로 변환
        new_user_df = pd.DataFrame([ml_user_data])
        
        # 원-핫 인코딩 (기존 템플릿에 맞춤)
        new_user_encoded = pd.get_dummies(new_user_df).reindex(
            columns=self.full_encoded_df.columns, fill_value=0
        )
        
        # 선택된 특징만 추출
        cols_to_keep = [col for col in self.full_encoded_df.columns 
                       if col in self.features_encoded.columns]
        
        new_user_features = new_user_encoded[cols_to_keep]
        new_user_features = new_user_features.reindex(
            columns=self.features_encoded.columns, fill_value=0
        )
        
        print(f"🔄 사용자 데이터 인코딩 완료: {new_user_features.shape}")
        
        # 코사인 유사도 계산
        print("🧮 코사인 유사도 계산 중...")
        similarity_scores = cosine_similarity(new_user_features, self.features_encoded)
        
        # 상위 유사 사용자 선택
        top_indices = similarity_scores[0].argsort()[::-1][:top_k]
        
        print(f"✅ 상위 {top_k}명 유사 고객 발견!")
        
        similar_users = []
        for i, index in enumerate(top_indices):
            similarity_score = similarity_scores[0][index]
            user_info = self.original_df.iloc[index].to_dict()
            
            similar_users.append({
                'rank': i + 1,
                'similarity_score': round(float(similarity_score), 3),
                'user_data': user_info
            })
            
            print(f"  {i+1}위: 유사도 {similarity_score:.3f}")
        
        return similar_users
    
    def get_recommendations(self, similar_users, exclude_low_satisfaction=True):
        """Django 구조에 맞춘 추천 생성"""
        print("🎁 Django 추천 결과 생성 중...")
        
        recommendations = []
        
        for user in similar_users:
            user_data = user['user_data']
            
            # 만족도 낮은 고객 제외
            if exclude_low_satisfaction:
                satisfaction = user_data.get('만족도', '')
                if satisfaction in ['불만족', '매우 불만족']:
                    print(f"⚠️ {user['rank']}위 고객 제외 (만족도: {satisfaction})")
                    continue
            
            # 다음 희망 휴가
            next_vacation = user_data.get('다음_휴가_경험', '기타')
            location_type = user_data.get('휴가_장소_국내_해외', '국내')
            
            # 추천 목적지 생성
            recommended_destinations = self._get_recommended_destinations(
                next_vacation, location_type
            )
            
            recommendation = {
                'rank': user['rank'],
                'similarity_score': user['similarity_score'],
                'vacation_type': next_vacation,
                'location_type': location_type,
                'current_location': user_data.get('휴가_장소', '정보 없음'),
                'transportation': user_data.get('주요_교통수단', '정보 없음'),
                'duration': user_data.get('휴가_기간', '정보 없음'),
                'companion': user_data.get('함께한_사람', '정보 없음'),
                'budget': user_data.get('총_비용', '정보 없음'),
                'satisfaction': user_data.get('만족도', '정보 없음'),
                'recommended_destinations': recommended_destinations
            }
            
            recommendations.append(recommendation)
        
        print(f"✅ {len(recommendations)}개 Django 추천 생성 완료!")
        return recommendations
    
    def _get_recommended_destinations(self, vacation_type, location_type):
        """휴가 유형과 국내/해외에 따른 추천 목적지"""
        destinations_info = self.destinations.get(vacation_type, {})
        
        if location_type in destinations_info:
            return destinations_info[location_type][:3]  # 상위 3개
        else:
            # 기본 추천
            if location_type == '국내':
                return ['서울', '부산', '제주']
            else:
                return ['동아시아', '동남아시아', '서유럽']
    
    def save_django_model(self, model_dir='./ml_models/'):
        """Django 프로젝트용 모델 저장"""
        print(f"💾 Django 호환 모델 저장 중... 경로: {model_dir}")
        
        os.makedirs(model_dir, exist_ok=True)
        
        # 저장할 파일들
        save_data = {
            'features_encoded.pkl': self.features_encoded,
            'encoding_template.pkl': self.full_encoded_df.columns.tolist(),
            'original_data.pkl': self.original_df,
            'selected_features.pkl': self.selected_features,
            'destinations.pkl': self.destinations
        }
        
        for filename, data in save_data.items():
            filepath = os.path.join(model_dir, filename)
            joblib.dump(data, filepath)
            print(f"✅ {filename} 저장 완료")
        
        # Django 메타데이터
        metadata = {
            'model_type': 'DjangoCompatibleRecommender',
            'algorithm': 'Cosine Similarity',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'selected_features': self.selected_features,
            'total_users': len(self.original_df),
            'total_features': len(self.features_encoded.columns),
            'django_compatible': True,
            'data_source': 'Django Survey Model'
        }
        
        with open(os.path.join(model_dir, 'metadata.pkl'), 'wb') as f:
            pickle.dump(metadata, f)
        
        print(f"✅ Django 메타데이터 저장 완료")
        print(f"🎉 Django 호환 모델 저장 완료!")
        
        return model_dir
    
    def print_django_recommendations(self, recommendations):
        """Django 친화적인 추천 결과 출력"""
        print("\n" + "="*60)
        print("🎯 Django 여름 휴가 추천 결과")
        print("="*60)
        
        for rec in recommendations:
            print(f"\n[{rec['rank']}위 추천] (유사도: {rec['similarity_score']})")
            print(f"  🏖️  추천 휴가: {rec['vacation_type']}")
            print(f"  🌍 지역 구분: {rec['location_type']}")
            print(f"  📍 참고 장소: {rec['current_location']}")
            print(f"  🚗 교통수단: {rec['transportation']}")
            print(f"  ⏰ 기간: {rec['duration']}")
            print(f"  👥 동행: {rec['companion']}")
            print(f"  💰 예산: {rec['budget']}")
            print(f"  😊 만족도: {rec['satisfaction']}")
            print(f"  🎯 추천 목적지: {', '.join(rec['recommended_destinations'])}")

# =============================================================================
# 🚀 Django 프로젝트용 실행 코드
# =============================================================================

if __name__ == "__main__":
    print("🎯 Django 호환 여름 휴가 추천 시스템 시작!")
    print("=" * 60)
    
    # 추천 시스템 초기화
    recommender = DjangoCompatibleRecommender()
    
    # Django에서 생성한 CSV 파일 경로
    csv_file_path = '../../data/ml_survey_data_20250905_102157.csv'  # 실제 경로로 변경
    
    try:
        # 데이터 로드
        df = recommender.load_and_preprocess_data(csv_file_path)
        
        # 테스트 사용자 (Django Survey 모델 형식)
        test_user_data = {
            '연령대': '20대',
            '성별': '여성',
            '가장_최근_여름_휴가': '해수욕, 물놀이 (바다/섬 여행)',
            '휴가_장소_국내_해외': '국내',
            '휴가_장소': '제주',
            '주요_교통수단': '항공편',
            '휴가_기간': '2~3일',
            '함께한_사람': '친구',
            '총_비용': '10만~30만 원',
            '만족도': '매우 만족',
            '다음_휴가_경험': '도시 관광 (쇼핑, 카페, 시내 구경)'
        }
        
        # 유사 사용자 찾기
        similar_users = recommender.find_similar_users(test_user_data, top_k=5)
        
        # 추천 생성
        recommendations = recommender.get_recommendations(
            similar_users, exclude_low_satisfaction=True
        )
        
        # 결과 출력
        recommender.print_django_recommendations(recommendations)
        
        # Django용 모델 저장
        model_dir = recommender.save_django_model('../ml_models/')
        
        print(f"\n🎉 Django 호환 시스템 준비 완료!")
        print(f"📦 저장 위치: {model_dir}")
        print("🚀 이제 Django 백엔드에서 이 모델을 사용할 수 있습니다!")
        
    except FileNotFoundError as e:
        print(f"❌ 파일 오류: {e}")
        print("💡 해결방법:")
        print("   1. Django에서 generate_ml_compatible_csv()를 실행하여 CSV를 생성하세요")
        print("   2. csv_file_path를 생성된 파일 경로로 수정하세요")
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()