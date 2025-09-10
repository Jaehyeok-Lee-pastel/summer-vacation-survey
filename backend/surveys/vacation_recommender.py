# vacation_recommender.py
# 🤖 Django용 여름휴가 추천 머신러닝 모듈
# 데이터 분석팀에서 제공 - 백엔드 담당자용

# 필요한 라이브러리(기능 묶음)들을 불러옵니다.
# pandas: 데이터를 표(DataFrame) 형태로 다루는 데 사용하는 라이브러리
import pandas as pd
# numpy: 숫자 계산을 효율적으로 처리하는 라이브러리
import numpy as np
# sklearn.metrics.pairwise: '코사인 유사도'를 계산하는 기능을 제공하는 라이브러리
# 코사인 유사도(Cosine Similarity)란?
# 벡터(데이터를 숫자로 표현한 것)들이 얼마나 비슷한 방향을 가리키는지 측정하여
# 두 데이터가 얼마나 유사한지 판단하는 방법입니다. 값이 1에 가까울수록 매우 유사하다는 뜻입니다.
from sklearn.metrics.pairwise import cosine_similarity
# joblib: 파이썬 객체를 파일로 저장하고 불러오는 데 사용되는 라이브러리
# 머신러닝 모델을 학습시킨 후, 다시 학습하지 않고 빠르게 불러와 사용하기 위해 주로 쓰입니다.
import joblib
# json: 데이터를 딕셔너리 형태로 저장하고 불러올 때 사용하는 라이브러리
import json
# os: 파일이나 폴더 경로를 다루는 데 사용되는 라이브러리
import os
# datetime: 날짜와 시간을 다루는 라이브러리
from datetime import datetime
# collections: 자료구조를 더 효율적으로 다루기 위한 라이브러리
# defaultdict, Counter: 딕셔너리와 비슷한 기능으로, 값이 없을 때 기본값을 설정하거나
# 항목의 개수를 쉽게 세는 기능을 제공합니다.
from collections import defaultdict, Counter


class VacationRecommendationService:
    """
    🎯 여름휴가 추천 서비스 클래스
    
    이 클래스는 사용자의 설문조사 데이터를 바탕으로
    가장 잘 맞는 휴가지를 추천해주는 핵심 기능을 담당합니다.
    
    사용법:
    1. 초기 학습: `train_model(csv_path)` 함수를 호출하여 기존 데이터를 학습시킵니다.
    2. 실시간 추천: `get_recommendations(user_survey_data)` 함수를 호출하여 사용자에게 추천을 제공합니다.
    """
    
    def __init__(self, model_dir='./ml_models/'):
        # 클래스가 생성될 때 가장 먼저 실행되는 함수입니다.
        # 앞으로 모델 파일들을 저장하고 불러올 기본 폴더 경로를 지정합니다.
        self.model_dir = model_dir
        # 모델이 학습되었는지 여부를 나타내는 플래그(Flag) 변수입니다.
        self.is_trained = False
        
        # 머신러닝 모델이 사용하는 데이터와 패턴을 저장할 변수들입니다.
        # 이 변수들은 모델을 불러오거나 학습할 때 채워집니다.
        self.features_encoded = None
        self.full_encoded_df = None
        self.original_df = None
        # vacation_patterns, preference_patterns, cost_patterns는
        # 이전에 학습된 패턴들을 딕셔너리 형태로 저장하는 변수들입니다.
        self.vacation_patterns = None
        self.preference_patterns = None
        self.cost_patterns = None
        
        # 🔧 백엔드 담당자: 여기는 Django의 모델과 연동하는 부분입니다.
        # 이 모듈을 Django 프로젝트에 통합할 때,
        # SurveyResponse와 같은 Django 모델 객체를 연결하여 사용하면 편리합니다.
        # 예: self.survey_model = SurveyResponse.objects.all()
        
        
    def train_model(self, csv_path):
        """
        🎓 초기 학습 함수 (서버 시작 시 한 번만 실행)
        
        이 함수는 기존에 쌓여있는 설문조사 데이터를 가지고
        머신러닝 모델을 학습시키는 역할을 합니다.
        
        Args (매개변수):
            csv_path (str): 기존 설문조사 데이터가 담긴 CSV 파일의 경로
            
        Returns (반환 값):
            bool: 학습이 성공했으면 True, 실패했으면 False를 반환합니다.
        """
        print(f"🤖 머신러닝 모델 학습 시작...")
        
        try:
            # 1. 데이터를 불러와서 머신러닝이 이해할 수 있는 형태로 전처리합니다.
            self._load_training_data(csv_path)
            
            # 2. 전처리된 데이터를 바탕으로 다양한 패턴(규칙)을 학습합니다.
            # 어떤 연령대가 어떤 휴가를 선호하는지, 만족도가 높은 휴가는 어떤 특징이 있는지 등을 분석합니다.
            self._learn_patterns()
            
            # 3. 학습이 완료된 모델과 패턴들을 파일로 저장합니다.
            # 다음에 서버를 재시작할 때 이 파일들을 불러와서 바로 사용할 수 있습니다.
            self._save_trained_model()
            
            # 학습 성공 플래그를 True로 변경합니다.
            self.is_trained = True
            print("✅ 머신러닝 모델 학습 완료!")
            return True
            
        except Exception as e:
            # 학습 과정에서 오류가 발생하면, 오류 메시지를 출력하고 False를 반환합니다.
            print(f"❌ 모델 학습 실패: {e}")
            return False
    
    def load_pretrained_model(self):
        """
        📂 기존에 학습된 모델 로드 (서버 재시작 시 사용)
        """
        try:
            if not os.path.exists(self.model_dir):
                print("⚠️ 학습된 모델이 없습니다. 먼저 train_model()을 실행하세요.")
                return False
            
            # 기존 파일들 로드
            self.features_encoded = joblib.load(os.path.join(self.model_dir, 'features_encoded.pkl'))
            self.original_df = joblib.load(os.path.join(self.model_dir, 'original_data.pkl'))
            
            # ⭐ 중요: full_encoded_df 복원 (이 부분이 빠져있었음)
            if self.original_df is not None:
                self.original_df = self.original_df.fillna('기타')
                self.full_encoded_df = pd.get_dummies(self.original_df)
                print(f"✅ full_encoded_df 복원 완료: {self.full_encoded_df.shape}")
            
            # JSON 파일들 로드
            with open(os.path.join(self.model_dir, 'learned_vacation_patterns.json'), 'r', encoding='utf-8') as f:
                self.vacation_patterns = json.load(f)
            
            with open(os.path.join(self.model_dir, 'preference_patterns.json'), 'r', encoding='utf-8') as f:
                self.preference_patterns = json.load(f)
                
            with open(os.path.join(self.model_dir, 'cost_patterns.json'), 'r', encoding='utf-8') as f:
                self.cost_patterns = json.load(f)
            
            self.is_trained = True
            print("✅ 기존 학습된 모델 로드 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            return False
    
    def get_recommendations(self, user_survey_data):
        """
        🎯 실시간 추천 생성 함수 (Django View에서 호출)
        
        이 함수는 새로운 사용자의 설문조사 데이터를 받아서
        AI 기반의 휴가 추천을 생성하고 반환합니다.
        
        Args (매개변수):
            user_survey_data (dict): 웹 폼(Form) 등을 통해 전달받은 사용자의 설문조사 응답 데이터
            
        Returns (반환 값):
            dict: 추천 결과가 담긴 딕셔너리를 반환합니다.
            성공 여부, 추천 목록, 유사 사용자 정보, 비용 정보 등이 포함됩니다.
        """
        
        # 🔧 백엔드 담당자 TODO: Django에서 받은 데이터를 딕셔너리 형태로 변환하는 부분입니다.
        # 사용자가 폼에 입력한 데이터를 `request.POST.get()`으로 가져와서
        # 위의 예시처럼 딕셔너리 형태로 만들어주면 됩니다.
        
        # 모델이 학습되지 않았다면 오류 메시지를 반환합니다.
        if not self.is_trained:
            return {
                'success': False,
                'error': '모델이 학습되지 않았습니다. 관리자에게 문의하세요.',
                'recommendations': [],
                'similar_users': [],
                'cost_info': {}
            }
        
        try:
            print(f"🔍 사용자 추천 생성 중...")
            
            # 1. _find_similar_users() 함수를 호출하여 현재 사용자와 가장 비슷한
            # 성향을 가진 기존 사용자들을 찾습니다.
            similar_users = self._find_similar_users(user_survey_data)
            
            # 2. _generate_recommendations() 함수를 호출하여 유사 사용자들의
            # 데이터를 기반으로 추천 목록을 생성합니다.
            recommendations = self._generate_recommendations(user_survey_data, similar_users)
            
            # 3. _format_for_django() 함수를 호출하여 추천 결과를
            # Django의 템플릿(HTML)에서 쉽게 사용할 수 있도록 구조를 정리합니다.
            formatted_result = self._format_for_django(recommendations, similar_users)
            
            print(f"✅ 추천 생성 완료!")
            return formatted_result
            
        except Exception as e:
            # 추천 생성 과정에서 오류가 발생하면 오류 정보를 반환합니다.
            print(f"❌ 추천 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': [],
                'similar_users': [],
                'cost_info': {}
            }
    
    def update_model_with_new_data(self, new_survey_data):
        """
        🔄 새로운 설문 데이터로 모델 업데이트 (선택사항)
        
        새로운 사용자가 설문조사를 완료할 때마다
        모델에 최신 데이터를 반영하여 추천 정확도를 높이는 함수입니다.
        
        Args (매개변수):
            new_survey_data (dict): 새로 제출된 설문조사 응답 데이터
        """
        
        # 🔧 백엔드 담당자 TODO: Django의 모델과 연동하여 새로운 데이터를 가져오는 부분입니다.
        # Django의 모델을 사용하여 새로 추가된 설문 응답들을 가져와서
        # 이 함수를 호출하여 최신 데이터를 학습 데이터에 추가할 수 있습니다.
        
        try:
            # 새로운 데이터를 Pandas의 데이터프레임으로 변환합니다.
            if self.original_df is not None:
                new_df = pd.DataFrame([new_survey_data])
                # 기존 학습 데이터(original_df)에 새로운 데이터를 추가합니다.
                self.original_df = pd.concat([self.original_df, new_df], ignore_index=True)
                
                # 새로운 데이터가 추가되었으므로 패턴을 다시 학습하고 모델을 저장합니다.
                self._learn_patterns()
                self._save_trained_model()
                
                print("✅ 모델 업데이트 완료!")
                return True
        except Exception as e:
            print(f"❌ 모델 업데이트 실패: {e}")
            return False
    
    # ================================
    # 내부 머신러닝 함수들 (백엔드 담당자는 수정하지 마세요)
    # ================================
    
    def _load_training_data(self, csv_path):
        """기존 설문조사 데이터 로드 및 전처리"""
        self.original_df = pd.read_csv(csv_path)
        
        # 결측값(비어있는 값)을 '기타'로 채워 넣어 오류를 방지합니다.
        self.original_df = self.original_df.fillna('기타')
        
        # 원-핫 인코딩(One-Hot Encoding)
        # 문자열(예: '20대', '여성')을 머신러닝 모델이 이해할 수 있는
        # 숫자(0 또는 1)로 변환하는 작업입니다.
        # '연령대_20대'와 같은 새로운 열을 만들어 20대면 1, 아니면 0을 넣습니다.
        self.full_encoded_df = pd.get_dummies(self.original_df)
        
        # 유사도 계산에 사용할 특정 특징(Feature)들만 선택합니다.
        selected_features = ['연령대', '성별', '함께한_사람', '휴가_장소_국내_해외', '가장_최근_여름_휴가']
        available_features = [feat for feat in selected_features if feat in self.original_df.columns]
        
        features_df = self.original_df[available_features]
        # 선택된 특징들만 원-핫 인코딩하여 저장합니다.
        self.features_encoded = pd.get_dummies(features_df)
    
    def _learn_patterns(self):
        """머신러닝 패턴 학습"""
        # defaultdict: 딕셔너리의 키가 없을 때 오류 대신 기본값을 반환하는 유용한 기능입니다.
        # 여기서는 중첩된 딕셔너리를 쉽게 만들기 위해 사용됩니다.
        self.vacation_patterns = defaultdict(lambda: defaultdict(list))
        
        # 만족도(만족, 매우 만족, 보통)가 높은 데이터만 골라내서 학습에 사용합니다.
        # 불만족스러운 데이터는 추천에 방해가 될 수 있기 때문입니다.
        satisfied_data = self.original_df[
            self.original_df['만족도'].isin(['만족', '매우 만족', '보통'])
        ]
        
        for _, row in satisfied_data.iterrows():
            vacation_type = row.get('가장_최근_여름_휴가', '기타')
            location_type = row.get('휴가_장소_국내_해외', '기타')
            
            # 구체적인 지역 정보 우선 사용, 없으면 국내/해외로 대체
            location = row.get('휴가_장소') or row.get('domestic_location') or row.get('overseas_location') or location_type
            if not location or location == '기타':
                location = location_type  # 최소한 국내/해외는 표시
                
            satisfaction = row.get('만족도', '보통')
            
            self.vacation_patterns[vacation_type][location_type].append({
                'location': location,  # 이제 구체적인 지역명이 들어감
                'satisfaction': satisfaction,
                'cost': row.get('총_비용', '기타'),
                'duration': row.get('휴가_기간', '기타')
            })
        
        # 선호도 패턴 학습
        self.preference_patterns = defaultdict(lambda: defaultdict(Counter))
        # Counter: 리스트나 문자열 등에서 각 항목의 개수를 세어주는 클래스입니다.
        # 예를 들어, Counter(['사과', '바나나', '사과'])를 실행하면
        # {'사과': 2, '바나나': 1}과 같은 결과를 반환합니다.
        for _, row in satisfied_data.iterrows():
            age = row.get('연령대', '기타')
            vacation_type = row.get('가장_최근_여름_휴가', '기타')
            next_pref = row.get('다음_휴가_경험', '기타')
            
            self.preference_patterns[age]['next_preferences'][next_pref] += 1
        
        # 비용 패턴 학습
        self.cost_patterns = defaultdict(lambda: defaultdict(list))
        for _, row in satisfied_data.iterrows():
            vacation_type = row.get('가장_최근_여름_휴가', '기타')
            location_type = row.get('휴가_장소_국내_해외', '기타')
            cost = row.get('총_비용', '기타')
            
            self.cost_patterns[vacation_type][location_type].append(cost)
    
    def _find_similar_users(self, user_data, top_k=5):
        """코사인 유사도로 유사한 사용자 찾기"""
        user_df = pd.DataFrame([user_data])
        # 사용자의 데이터를 기존 학습 데이터와 같은 형태로 맞춥니다.
        # .reindex() 함수를 사용하여 없는 열은 0으로 채웁니다.
        user_encoded = pd.get_dummies(user_df).reindex(
            columns=self.full_encoded_df.columns, fill_value=0
        )
        
        # 특징 추출
        cols_to_keep = [col for col in self.full_encoded_df.columns 
                         if col in self.features_encoded.columns]
        user_features = user_encoded[cols_to_keep].reindex(
            columns=self.features_encoded.columns, fill_value=0
        )
        
        # 유사도 계산
        # scikit-learn의 `cosine_similarity` 함수를 사용하여
        # 현재 사용자와 기존 사용자들 간의 유사도 점수를 계산합니다.
        similarity_scores = cosine_similarity(user_features, self.features_encoded)
        # 유사도 점수가 높은 순서대로 상위 5개의 인덱스(위치)를 가져옵니다.
        top_indices = similarity_scores[0].argsort()[::-1][:top_k]
        
        similar_users = []
        for i, idx in enumerate(top_indices):
            similarity_score = similarity_scores[0][idx]
            user_info = self.original_df.iloc[idx].to_dict()
            
            # 만족도(만족, 매우 만족, 보통)가 높은 사용자들만 유사 사용자로 포함합니다.
            if user_info.get('만족도') in ['만족', '매우 만족', '보통']:
                similar_users.append({
                    'rank': i + 1,
                    'similarity_score': round(similarity_score, 2),
                    'user_data': user_info
                })
        
        return similar_users
    
    def _generate_recommendations(self, user_data, similar_users):
        """AI 추천 생성"""
        recommendations = []
        
        # 학습된 'vacation_patterns'을 기반으로 추천을 생성합니다.
        for vacation_type, location_data in self.vacation_patterns.items():
            for location_type, experiences in location_data.items():
                if len(experiences) >= 2:  # 최소 2명 이상 경험한 데이터만 사용합니다.
                    # 각 만족도 항목을 숫자로 변환하여 평균을 계산합니다.
                    satisfaction_scores = [self._satisfaction_to_score(exp['satisfaction']) 
                                           for exp in experiences]
                    avg_satisfaction = np.mean(satisfaction_scores)
                    
                    if avg_satisfaction >= 3.0:  # 만족도 평균이 '보통' 이상인 경우만 추천합니다.
                        # Counter().most_common(1): 가장 자주 등장한 항목을 찾습니다.
                        location_counts = Counter(exp['location'] for exp in experiences)
                        top_location = location_counts.most_common(1)[0]
                        print('top_location', top_location)
                        recommendations.append({
                            'vacation_type': vacation_type,
                            'location_type': location_type,
                            'recommended_location': top_location[0],
                            'avg_satisfaction': round(avg_satisfaction, 2),
                            'experience_count': len(experiences),
                            'confidence': min(len(experiences) / 10 * avg_satisfaction / 5, 1.0)
                        })
        
        # 만족도와 경험 수 기준으로 정렬하여 가장 좋은 추천을 상위에 놓습니다.
        recommendations.sort(key=lambda x: (x['avg_satisfaction'], x['experience_count']), reverse=True)
        
        return recommendations
    
    def _satisfaction_to_score(self, satisfaction):
        """만족도를 점수로 변환"""
        # '매우 만족'과 같은 문자열을 숫자로 바꿔주는 딕셔너리입니다.
        satisfaction_map = {
            '매우 불만족': 1, '불만족': 2, '보통': 3, '만족': 4, '매우 만족': 5
        }
        # 딕셔너리에 없는 값일 경우 기본값으로 3('보통')을 반환합니다.
        return satisfaction_map.get(satisfaction, 3)
    
    def _format_for_django(self, recommendations, similar_users):
        """Django 템플릿에서 사용하기 쉽도록 결과 포맷팅"""
        
        # 🔧 백엔드 담당자: 여기는 Django 템플릿에 데이터를 전달하기 전에
        # 보기 좋게 구조를 정리하는 부분입니다.
        # 예를 들어, 유사도 점수(0.85)를 퍼센트(85%)로 변환하거나,
        # 필요한 정보만 남기고 불필요한 정보는 제거하는 등의 작업을 할 수 있습니다.
        
        return {
            'success': True,
            'recommendations': recommendations[:5],  # 상위 5개 추천만 보여줍니다.
            'similar_users': [
                {
                    'rank': user['rank'],
                    # 유사도 점수(0.85)를 문자열("85%")로 변환합니다.
                    'similarity': f"{user['similarity_score']*100:.0f}%",
                    'vacation_type': user['user_data'].get('가장_최근_여름_휴가', '정보없음'),
                    'location': user['user_data'].get('휴가_장소', '정보없음'),
                    'satisfaction': user['user_data'].get('만족도', '정보없음'),
                    'cost': user['user_data'].get('총_비용', '정보없음')
                }
                for user in similar_users[:3]  # 유사 사용자 중 상위 3명만 보여줍니다.
            ],
            'cost_info': self._get_cost_recommendations(),
            'next_vacation_suggestions': self._get_next_vacation_suggestions()
        }
    
    def _get_cost_recommendations(self):
        """비용 추천 정보"""
        cost_info = {}
        for vacation_type, location_data in self.cost_patterns.items():
            cost_info[vacation_type] = {}
            for location_type, costs in location_data.items():
                if costs:
                    # Counter를 사용하여 가장 많이 등장한 비용을 찾습니다.
                    most_common_cost = Counter(costs).most_common(1)[0]
                    cost_info[vacation_type][location_type] = most_common_cost[0]
        return cost_info
    
    def _get_next_vacation_suggestions(self):
        """다음 휴가 제안"""
        suggestions = []
        for age_group, patterns in self.preference_patterns.items():
            next_prefs = patterns.get('next_preferences', {})
            # 각 연령대에서 가장 인기있는 다음 휴가 경험 3개를 찾습니다.
            for vacation_type, count in Counter(next_prefs).most_common(3):
                suggestions.append({
                    'vacation_type': vacation_type,
                    'target_age': age_group,
                    'popularity': count
                })
        return suggestions
    
    def _save_trained_model(self):
        """학습된 모델 저장"""
        os.makedirs(self.model_dir, exist_ok=True)
        
        joblib.dump(self.features_encoded, os.path.join(self.model_dir, 'features_encoded.pkl'))
        joblib.dump(self.original_df, os.path.join(self.model_dir, 'original_data.pkl'))
        
        # 다음 부분들을 제거하거나 주석 처리해야 함 (존재하지 않는 변수들)
        # if self.satisfaction_predictor:
        #     joblib.dump(self.satisfaction_predictor, os.path.join(self.model_dir, 'satisfaction_model.pkl'))
        # if self.user_clustering_model:
        #     joblib.dump(self.user_clustering_model, os.path.join(self.model_dir, 'clustering_model.pkl'))
        # if self.vacation_classifier:
        #     joblib.dump(self.vacation_classifier, os.path.join(self.model_dir, 'vacation_classifier.pkl'))
        # if self.collaborative_filter:
        #     joblib.dump(self.collaborative_filter, os.path.join(self.model_dir, 'collaborative_filter.pkl'))
        # if self.label_encoders:
        #     joblib.dump(self.label_encoders, os.path.join(self.model_dir, 'label_encoders.pkl'))
        
        # JSON 파일 저장 (이 부분은 유지)
        with open(os.path.join(self.model_dir, 'learned_vacation_patterns.json'), 'w', encoding='utf-8') as f:
            json.dump(dict(self.vacation_patterns), f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(self.model_dir, 'preference_patterns.json'), 'w', encoding='utf-8') as f:
            json.dump(dict(self.preference_patterns), f, ensure_ascii=False, indent=2)
            
        with open(os.path.join(self.model_dir, 'cost_patterns.json'), 'w', encoding='utf-8') as f:
            json.dump(dict(self.cost_patterns), f, ensure_ascii=False, indent=2)


# =============================================================================
# 🔧 백엔드 담당자용 Django 연동 가이드
# =============================================================================

"""
📋 Django views.py에서 사용 방법:

1. 먼저 서버 시작 시 모델 학습 (settings.py 또는 apps.py):
   
   # `vacation_recommender.py` 파일에서 `VacationRecommendationService` 클래스를 가져옵니다.
   from .vacation_recommender import VacationRecommendationService
   
   # 서버의 전역(Global) 변수로 클래스의 객체를 한 번만 만듭니다.
   # 이렇게 하면 서버가 실행되는 동안 모델을 메모리에 로드해두고 여러 사용자가 공유할 수 있습니다.
   vacation_service = VacationRecommendationService()
   
   # `train_model` 함수를 호출하여 CSV 파일 경로를 지정하고 초기 학습을 시작합니다.
   vacation_service.train_model('path/to/survey_data.csv')
   # 또는, 이미 학습된 모델이 있다면 아래 함수를 호출하여 파일을 불러옵니다.
   vacation_service.load_pretrained_model()

2. Django views.py에서 추천 생성:

   # 필요한 라이브러리와 위에서 만든 전역 인스턴스를 불러옵니다.
   from django.http import JsonResponse
   from django.shortcuts import render
   from .vacation_recommender import vacation_service  # 전역 인스턴스 import
   
   def get_vacation_recommendation(request):
       # HTTP 요청 방식이 POST일 때만 실행하도록 설정합니다.
       if request.method == 'POST':
           # 🔧 TODO: HTML 폼(Form) 데이터를 딕셔너리로 변환하는 부분입니다.
           # 사용자가 폼에 입력한 데이터를 `request.POST.get()`으로 하나씩 가져옵니다.
           # 이때 폼의 'name' 속성과 딕셔너리의 키 이름이 일치해야 합니다.
           user_data = {
               '연령대': request.POST.get('age_group'),
               '성별': request.POST.get('gender'),
               '가장_최근_여름_휴가': request.POST.get('recent_vacation'),
               '휴가_장소_국내_해외': request.POST.get('domestic_international'),
               '함께한_사람': request.POST.get('companion'),
               '총_비용': request.POST.get('total_cost'),
               # ... 기타 필드들을 추가하세요.
           }
           
           # AI 추천을 생성하는 핵심 함수를 호출하고 결과를 받습니다.
           result = vacation_service.get_recommendations(user_data)
           
           # 결과의 성공 여부에 따라 다른 화면을 보여줍니다.
           if result['success']:
               # 추천이 성공하면 'recommendation_result.html' 템플릿에 결과를 전달하여 렌더링(Rendering)합니다.
               return render(request, 'recommendation_result.html', {
                   'recommendations': result['recommendations'],
                   'similar_users': result['similar_users'],
                   'cost_info': result['cost_info']
               })
           else:
               # 추천에 실패하면 'error.html' 템플릿에 오류 메시지를 전달합니다.
               return render(request, 'error.html', {'error': result['error']})

3. Django models.py 연동 (선택사항):

   # 새로운 설문 데이터가 저장될 때마다 모델을 업데이트하는 예시입니다.
   def save_survey_response(request):
       # 사용자가 제출한 설문 데이터를 Django 모델에 저장합니다.
       survey = SurveyResponse.objects.create(
           age_group=request.POST.get('age_group'),
           gender=request.POST.get('gender'),
           # ... 필드들
       )
       
       # 머신러닝 모델에 새 데이터를 반영하기 위해
       # Django 모델 객체의 데이터를 딕셔너리로 변환합니다.
       survey_data = {
           '연령대': survey.age_group,
           '성별': survey.gender,
           # ... 필드 매핑
       }
       # `update_model_with_new_data` 함수를 호출하여 모델을 업데이트합니다.
       vacation_service.update_model_with_new_data(survey_data)

4. 필요한 패키지 설치:
   # 이 모듈을 실행하기 위해 필요한 라이브러리들을 설치하는 명령어입니다.
   pip install pandas scikit-learn numpy joblib

⚠️ 주의사항:
- CSV 파일의 컬럼(Column) 이름이 코드에 사용된 한글 이름('연령대', '성별' 등)과 정확히 일치해야 합니다.
- 서버 메모리에 모델을 로드하므로 서버를 재시작하면 모델을 다시 로드해야 합니다.
- 데이터가 매우 많을 경우(대용량)에는 Redis나 데이터베이스 캐싱(Caching) 같은
  성능 최적화 기술을 추가로 고려하는 것이 좋습니다.
"""