# 📁 summer_vacation_recommender.py
# 여름 휴가 추천 시스템 - 머신러닝 결과 기반 구현

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import pickle
import os
from datetime import datetime

class SummerVacationRecommender:
    def __init__(self):
        self.full_encoded_df = None
        self.features_encoded = None
        self.original_df = None
        self.feature_columns = None
        
        # 📋 머신러닝 결과에서 사용된 핵심 특징 5가지
        self.selected_features = [
            '연령대',                    
            '성별',                      
            '함께한_사람',               
            '휴가_장소_국내_해외',       
            '가장_최근_여름_휴가'        
        ]
        
        # 🎯 머신러닝 결과에서 나온 추천 데이터만 사용
        # 실제 결과에 나타난 휴가 유형과 지역 정보
        self.vacation_results = {
            '해수욕, 물놀이 (바다/섬 여행)': {
                '동아시아': ['동아시아 바다/섬 여행지'],
                '아프리카': ['아프리카 바다/섬 여행지']
            },
            '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)': {
                '북미': ['북미 아웃도어 활동지']
            },
            '맛집 투어 (맛집 탐방, 지역 특산물 체험)': {
                '동남아시아': ['동남아시아 맛집 투어']
            },
            '도시 관광 (쇼핑, 카페, 시내 구경)': {
                '동아시아': ['동아시아 도시 관광지']
            },
            '휴양·힐링 (스파, 리조트, 펜션 휴식)': {
                '동남아시아': ['동남아시아 휴양지'],
                '아프리카': ['아프리카 휴양지']
            },
            '친척·지인 방문': {
                '북미': ['북미 지역']
            }
        }
    
    def load_and_preprocess_data(self, csv_path):
        """
        📊 1단계: CSV 파일 로드 및 전처리
        """
        print(f"📂 데이터 로딩: {csv_path}")
        
        # CSV 파일 존재 여부 확인
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"❌ 파일을 찾을 수 없습니다: {csv_path}")
        
        # 데이터 로드
        self.original_df = pd.read_csv(csv_path)
        print(f"✅ 데이터 로드 완료")
        print(f"📊 데이터 크기: {self.original_df.shape[0]}행 {self.original_df.shape[1]}열")
        print(f"📋 컬럼: {self.original_df.columns.tolist()}")
        
        # 결측값 확인 및 처리
        missing_data = self.original_df.isnull().sum()
        if missing_data.any():
            print(f"⚠️ 결측값 발견:")
            for col, count in missing_data[missing_data > 0].items():
                print(f"   {col}: {count}개")
                # 결측값을 '기타'로 처리
                self.original_df[col] = self.original_df[col].fillna('기타')
        
        # 🔄 전체 데이터 원-핫 인코딩 (기준 템플릿)
        print("🔄 전체 데이터 원-핫 인코딩 중...")
        self.full_encoded_df = pd.get_dummies(self.original_df)
        print(f"✅ 인코딩 완료: {len(self.full_encoded_df.columns)}개 특성")
        
        # 🎯 선택된 특징만으로 인코딩
        print(f"🎯 핵심 특징 선택: {self.selected_features}")
        
        # 실제 존재하는 특징만 필터링
        available_features = [feat for feat in self.selected_features 
                             if feat in self.original_df.columns]
        
        if len(available_features) != len(self.selected_features):
            missing_features = set(self.selected_features) - set(available_features)
            print(f"⚠️ 누락된 특징: {missing_features}")
            self.selected_features = available_features
            print(f"🔧 사용할 특징: {self.selected_features}")
        
        # 선택된 특징만으로 데이터프레임 생성
        features_df = self.original_df[self.selected_features]
        self.features_encoded = pd.get_dummies(features_df)
        self.feature_columns = self.features_encoded.columns.tolist()
        
        print(f"✅ 특징 인코딩 완료: {len(self.features_encoded.columns)}개 특성")
        print(f"📊 인코딩된 특징 예시: {self.feature_columns[:5]}")
        
        return self.original_df
    
    def find_similar_users(self, new_user_data, top_k=5):
        """
        🎯 2단계: 새로운 사용자와 유사한 고객 찾기 (코사인 유사도)
        """
        print("🔍 유사한 고객 검색 중...")
        
        if self.features_encoded is None:
            raise ValueError("❌ 데이터가 로드되지 않았습니다. load_and_preprocess_data()를 먼저 실행하세요.")
        
        # 새로운 사용자 데이터를 데이터프레임으로 변환
        new_user_df = pd.DataFrame([new_user_data])
        print(f"👤 새로운 사용자 데이터:")
        for key, value in new_user_data.items():
            print(f"   {key}: {value}")
        
        # 전체 컬럼 기준으로 원-핫 인코딩
        new_user_encoded = pd.get_dummies(new_user_df).reindex(
            columns=self.full_encoded_df.columns, fill_value=0
        )
        
        # 선택된 특징만 추출
        cols_to_keep = [col for col in self.full_encoded_df.columns 
                       if col in self.features_encoded.columns]
        
        new_user_features = new_user_encoded[cols_to_keep]
        
        # 특성 벡터 차원 맞추기
        new_user_features = new_user_features.reindex(
            columns=self.features_encoded.columns, fill_value=0
        )
        
        print(f"🔄 사용자 데이터 인코딩 완료: {new_user_features.shape}")
        
        # 🎯 코사인 유사도 계산
        print("🧮 코사인 유사도 계산 중...")
        similarity_scores = cosine_similarity(new_user_features, self.features_encoded)
        
        # 유사도 점수로 정렬 (높은 순)
        top_indices = similarity_scores[0].argsort()[::-1][:top_k]
        
        print(f"✅ 상위 {top_k}명 유사 고객 발견!")
        
        # 결과 정리
        similar_users = []
        for i, index in enumerate(top_indices):
            similarity_score = similarity_scores[0][index]
            user_info = self.original_df.iloc[index].to_dict()
            
            similar_users.append({
                'rank': i + 1,
                'similarity_score': round(similarity_score, 2),
                'user_data': user_info
            })
        
        return similar_users
    
    def get_recommendations(self, similar_users, exclude_low_satisfaction=True):
        """
        🎁 3단계: 추천 생성 (만족도 낮은 정보 제외)
        """
        print("🎁 추천 결과 생성 중...")
        
        recommendations = []
        
        for user in similar_users:
            user_data = user['user_data']
            
            # 만족도 낮은 고객 제외 (머신러닝 결과 방식 적용)
            if exclude_low_satisfaction:
                satisfaction = user_data.get('만족도', '')
                if satisfaction in ['불만족', '매우 불만족']:
                    print(f"⚠️ {user['rank']}위 고객 제외 (만족도: {satisfaction})")
                    continue
            
            # 추천 정보 정리 (머신러닝 결과 형식 그대로)
            recommendation = {
                'rank': user['rank'],
                'similarity_score': user['similarity_score'],
                'age_group': user_data.get('연령대', '정보 없음'),
                'gender': user_data.get('성별', '정보 없음'),
                'recent_vacation': user_data.get('가장_최근_여름_휴가', '정보 없음'),
                'location_type': user_data.get('휴가_장소_국내_해외', '정보 없음'),
                'location': user_data.get('휴가_장소', '정보 없음'),
                'transportation': user_data.get('주요_교통수단', '정보 없음'),
                'duration': user_data.get('휴가_기간', '정보 없음'),
                'companion': user_data.get('함께한_사람', '정보 없음'),
                'budget': user_data.get('총_비용', '정보 없음'),
                'satisfaction': user_data.get('만족도', '정보 없음'),
                'next_preference': user_data.get('다음_휴가_경험', '정보 없음')
            }
            
            recommendations.append(recommendation)
        
        print(f"✅ {len(recommendations)}개 추천 생성 완료!")
        return recommendations
    
    def save_model(self, model_dir='./ml_models/'):
        """
        💾 모델 및 데이터 저장 (Django에서 사용하도록)
        """
        print(f"💾 모델 저장 중... 경로: {model_dir}")
        
        # 저장 디렉토리 생성
        os.makedirs(model_dir, exist_ok=True)
        
        # 1. 인코딩된 특징 데이터 저장
        features_path = os.path.join(model_dir, 'features_encoded.pkl')
        joblib.dump(self.features_encoded, features_path)
        print(f"✅ 특징 데이터 저장: {features_path}")
        
        # 2. 전체 인코딩 템플릿 저장
        template_path = os.path.join(model_dir, 'encoding_template.pkl')
        joblib.dump(self.full_encoded_df.columns.tolist(), template_path)
        print(f"✅ 인코딩 템플릿 저장: {template_path}")
        
        # 3. 원본 데이터 저장
        original_path = os.path.join(model_dir, 'original_data.pkl')
        joblib.dump(self.original_df, original_path)
        print(f"✅ 원본 데이터 저장: {original_path}")
        
        # 4. 선택된 특징 저장
        selected_features_path = os.path.join(model_dir, 'selected_features.pkl')
        joblib.dump(self.selected_features, selected_features_path)
        print(f"✅ 선택된 특징 저장: {selected_features_path}")
        
        # 5. 휴가 결과 데이터 저장 (머신러닝 결과 기반)
        vacation_results_path = os.path.join(model_dir, 'vacation_results.pkl')
        joblib.dump(self.vacation_results, vacation_results_path)
        print(f"✅ 휴가 결과 데이터 저장: {vacation_results_path}")
        
        # 6. 메타데이터 저장
        metadata = {
            'model_type': 'CosineSimilarityRecommender',
            'algorithm': 'Cosine Similarity',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'selected_features': self.selected_features,
            'total_users': len(self.original_df) if self.original_df is not None else 0,
            'total_features': len(self.features_encoded.columns) if self.features_encoded is not None else 0,
            'data_columns': self.original_df.columns.tolist() if self.original_df is not None else [],
            'vacation_types': list(self.vacation_results.keys())
        }
        
        metadata_path = os.path.join(model_dir, 'metadata.pkl')
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✅ 메타데이터 저장: {metadata_path}")
        
        print(f"🎉 모든 파일 저장 완료!")
        print(f"📁 저장된 파일들:")
        for file in os.listdir(model_dir):
            file_path = os.path.join(model_dir, file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"   📄 {file} ({file_size:.1f} KB)")
    
    def print_recommendations(self, recommendations):
        """
        📋 추천 결과를 머신러닝 결과 형식으로 출력
        """
        print("\n" + "="*60)
        print("--- 가장 유사한 고객 정보 ---")
        print("="*60)
        
        for rec in recommendations:
            print(f"\n[{rec['rank']}위 고객 정보]")
            print(f"유사도 점수: {rec['similarity_score']}")
            print(f"  - 연령대: {rec['age_group']}")
            print(f"  - 성별: {rec['gender']}")
            print(f"  - 가장_최근_여름_휴가: {rec['recent_vacation']}")
            print(f"  - 휴가_장소_국내_해외: {rec['location_type']}")
            print(f"  - 휴가_장소: {rec['location']}")
            print(f"  - 주요_교통수단: {rec['transportation']}")
            print(f"  - 휴가_기간: {rec['duration']}")
            print(f"  - 함께한_사람: {rec['companion']}")
            print(f"  - 총_비용: {rec['budget']}")
            print(f"  - 만족도: {rec['satisfaction']}")
            print(f"  - 다음_희망_휴가: {rec['next_preference']}")

# =============================================================================
# 🚀 실행 코드 (데이터 분석가가 실행할 부분)
# =============================================================================

if __name__ == "__main__":
    print("🎯 여름 휴가 추천 시스템 - 머신러닝 결과 기반!")
    print("=" * 60)
    
    # 1️⃣ 추천 시스템 초기화
    recommender = SummerVacationRecommender()
    
    # 2️⃣ CSV 파일 경로 설정 (실제 파일 경로로 변경)
    csv_file_path = 'survey_data.csv'  # 👈 실제 파일 경로로 변경
    
    try:
        # 3️⃣ 데이터 로드 및 전처리
        df = recommender.load_and_preprocess_data(csv_file_path)
        
        # 4️⃣ 새로운 고객 데이터 (백엔드에서 실제 사용자 데이터로 교체 예정)
        # 머신러닝 결과에 나온 형식과 동일하게 설정
        new_user_data = {
            '연령대': '20대',
            '성별': '여성',
            '가장_최근_여름_휴가': '해수욕, 물놀이 (바다/섬 여행)',
            '휴가_장소_국내_해외': '해외',
            '휴가_장소': '동아시아',
            '주요_교통수단': '항공편',
            '휴가_기간': '4~6일',
            '함께한_사람': '가족',
            '총_비용': '30만~50만 원',
            '만족도': '매우 만족',
            '다음_휴가_경험': '도시 관광 (쇼핑, 카페, 시내 구경)'
        }
        
        # 5️⃣ 유사한 고객 찾기 (상위 5명)
        similar_users = recommender.find_similar_users(new_user_data, top_k=5)
        
        # 6️⃣ 추천 생성 (만족도 낮은 고객 제외)
        recommendations = recommender.get_recommendations(
            similar_users, exclude_low_satisfaction=True
        )
        
        # 7️⃣ 머신러닝 결과 형식으로 출력
        recommender.print_recommendations(recommendations)
        
        # 8️⃣ 모델 저장 (Django에서 사용할 수 있도록)
        recommender.save_model('./ml_models/')
        
        print("\n🎉 모든 작업 완료!")
        print("📦 Django 프로젝트에서 사용할 파일들이 ml_models/ 폴더에 저장되었습니다.")
        print("🚀 이제 백엔드 개발팀이 이 시스템을 사용할 수 있습니다!")
        
    except FileNotFoundError as e:
        print(f"❌ 파일 오류: {e}")
        print("💡 해결방법:")
        print("   1. CSV 파일 경로를 확인하세요")
        print("   2. 파일명이 'survey_data.csv'인지 확인하세요")
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        print("💡 오류를 개발팀과 공유해주세요!")
        import traceback
        traceback.print_exc()