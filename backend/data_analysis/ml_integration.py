# data_analysis/ml_integration.py
import joblib
import pickle
import pandas as pd
import os
from django.conf import settings
from sklearn.metrics.pairwise import cosine_similarity

class DjangoMLRecommender:
    def __init__(self):
        # 모델 경로를 data_analysis/ml_models/로 설정
        self.model_dir = os.path.join(settings.BASE_DIR, 'data_analysis', 'ml_models')
        self.features_encoded = None
        self.original_df = None
        self.destinations = None
        self.encoding_template = None
        self.selected_features = None
        self.is_loaded = self.load_model()
    
    def load_model(self):
        """ML 모델 파일들 로드"""
        try:
            # 필요한 파일들 로드
            self.features_encoded = joblib.load(os.path.join(self.model_dir, 'features_encoded.pkl'))
            self.original_df = joblib.load(os.path.join(self.model_dir, 'original_data.pkl'))
            self.destinations = joblib.load(os.path.join(self.model_dir, 'destinations.pkl'))
            self.encoding_template = joblib.load(os.path.join(self.model_dir, 'encoding_template.pkl'))
            self.selected_features = joblib.load(os.path.join(self.model_dir, 'selected_features.pkl'))
            
            print(f"ML 모델 로드 성공! 경로: {self.model_dir}")
            return True
        except Exception as e:
            print(f"ML 모델 로드 실패: {e}")
            return False
    
    def get_recommendation_for_user(self, survey):
        """Django Survey 객체로부터 추천 생성"""
        if not self.is_loaded:
            return self._fallback_recommendation()
        
        try:
            # Django Survey를 ML 형식으로 변환
            user_data = self._convert_survey_to_ml_format(survey)
            
            # 유사 사용자 찾기
            similar_users = self._find_similar_users(user_data)
            
            # 추천 생성
            recommendations = self._generate_recommendations(similar_users)
            
            return {
                'status': 'success',
                'recommendations': recommendations,
                'user_profile': user_data
            }
        except Exception as e:
            print(f"추천 생성 오류: {e}")
            return self._fallback_recommendation()
    
    def _convert_survey_to_ml_format(self, survey):
        """Django Survey를 ML 형식으로 변환"""
        # Django 모델의 휴가 유형을 ML 형식으로 매핑
        vacation_mapping = {
            '해수욕, 물놀이': '해수욕, 물놀이 (바다/섬 여행)',
            '등산, 캠핑': '등산, 캠핑 등 아웃도어 활동 (산/계곡 여행)',
            '맛집 투어': '맛집 투어 (맛집 탐방, 지역 특산물 체험)',
            '도시 관광': '도시 관광 (쇼핑, 카페, 시내 구경)',
            '휴양·힐링': '휴양·힐링 (스파, 리조트, 펜션 휴식)',
            '문화생활': '문화생활 (박물관, 유적지, 공연 관람)',
            '친척·지인 방문': '친척·지인 방문',
            '기타': '기타'
        }
        
        # 만족도 숫자를 텍스트로 변환
        satisfaction_mapping = {
            1: '매우 불만족', 2: '불만족', 3: '보통', 4: '만족', 5: '매우 만족'
        }
        
        # 휴가 장소 결정
        vacation_place = (survey.domestic_location if survey.location_type == '국내' 
                         else survey.overseas_location) or '기타'
        
        return {
            '연령대': survey.age_group,
            '성별': survey.gender,
            '가장_최근_여름_휴가': vacation_mapping.get(survey.vacation_type, survey.vacation_type),
            '휴가_장소_국내_해외': survey.location_type,
            '휴가_장소': vacation_place,
            '주요_교통수단': survey.transportation,
            '휴가_기간': survey.duration,
            '함께한_사람': survey.companion,
            '총_비용': survey.cost,
            '만족도': satisfaction_mapping.get(survey.satisfaction, '보통'),
            '다음_휴가_경험': vacation_mapping.get(survey.next_vacation_type, survey.next_vacation_type)
        }
    
    def _find_similar_users(self, user_data, top_k=5):
        """유사 사용자 찾기"""
        # 사용자 데이터를 DataFrame으로 변환
        new_user_df = pd.DataFrame([user_data])
        
        # 원-핫 인코딩
        new_user_encoded = pd.get_dummies(new_user_df).reindex(
            columns=self.encoding_template, fill_value=0
        )
        
        # 선택된 특징만 추출
        cols_to_keep = [col for col in self.encoding_template 
                       if any(feat in col for feat in self.selected_features)]
        
        new_user_features = new_user_encoded[cols_to_keep]
        new_user_features = new_user_features.reindex(
            columns=self.features_encoded.columns, fill_value=0
        )
        
        # 코사인 유사도 계산
        similarity_scores = cosine_similarity(new_user_features, self.features_encoded)
        top_indices = similarity_scores[0].argsort()[::-1][:top_k]
        
        similar_users = []
        for i, index in enumerate(top_indices):
            similarity_score = similarity_scores[0][index]
            user_info = self.original_df.iloc[index].to_dict()
            
            similar_users.append({
                'rank': i + 1,
                'similarity_score': float(similarity_score),
                'user_data': user_info
            })
        
        return similar_users
    
    
    def _generate_recommendations(self, similar_users):
        """추천 생성"""
        recommendations = []
        
        for user in similar_users:
            user_data = user['user_data']
            
            # 만족도 낮은 사용자 제외
            satisfaction = user_data.get('만족도', '')
            if satisfaction in ['불만족', '매우 불만족']:
                continue
            
            next_vacation = user_data.get('다음_휴가_경험', '기타')
            location_type = user_data.get('휴가_장소_국내_해외', '국내')
            
            # 추천 목적지
            destinations = self._get_destinations_for_type(next_vacation, location_type)
            
            recommendation = {
                'similarity_score': round(user['similarity_score'], 2),
                'vacation_type': next_vacation,
                'location_type': location_type,
                'recommended_destinations': destinations,
                'reference_data': {
                    'transportation': user_data.get('주요_교통수단', ''),
                    'duration': user_data.get('휴가_기간', ''),
                    'companion': user_data.get('함께한_사람', ''),
                    'budget': user_data.get('총_비용', ''),
                    'satisfaction': satisfaction
                }
            }
            
            recommendations.append(recommendation)
        
        return recommendations[:3]  # 상위 3개만
    
    def _get_destinations_for_type(self, vacation_type, location_type):
        """휴가 유형에 맞는 목적지 반환"""
        destinations_info = self.destinations.get(vacation_type, {})
        
        if location_type in destinations_info:
            return destinations_info[location_type][:3]
        else:
            if location_type == '국내':
                return ['서울', '부산', '제주']
            else:
                return ['동아시아', '동남아시아', '서유럽']
    
    def _fallback_recommendation(self):
        """ML 실패 시 기본 추천"""
        return {
            'status': 'fallback',
            'message': 'ML 모델을 사용할 수 없어 기본 추천을 제공합니다.',
            'recommendations': [{
                'similarity_score': 0.7,
                'vacation_type': '해수욕, 물놀이 (바다/섬 여행)',
                'location_type': '국내',
                'recommended_destinations': ['부산', '제주', '강원']
            }]
        }

# 전역 인스턴스
ml_recommender = DjangoMLRecommender()