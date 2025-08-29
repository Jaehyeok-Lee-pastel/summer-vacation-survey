# surveys/forms.py (새 파일)

from django import forms
from .models import Survey

class SurveyForm(forms.ModelForm):
    """
    설문조사 입력을 위한 폼
    ModelForm을 사용해서 Survey 모델과 자동으로 연결
    """
    
    class Meta:
        model = Survey
        # user와 created_at는 자동으로 설정되므로 제외
        fields = [
            'age_group',
            'gender', 
            'vacation_type',
            'location_type',
            'domestic_location',
            'overseas_location',
            'transportation',
            'duration',
            'companion',
            'cost',
            'satisfaction',
            'next_vacation_type'
        ]
        
        # 각 필드의 한글 라벨 설정
        labels = {
            'age_group': '1. 귀하의 연령대는?',
            'gender': '2. 귀하의 성별은?',
            'vacation_type': '3. 가장 최근에 갔던 여름 휴가는 무엇인가요?',
            'location_type': '4. 여름 휴가를 보낸 장소는 어디였나요?',
            'domestic_location': '   → 국내 지역을 선택해주세요',
            'overseas_location': '   → 해외 지역을 선택해주세요',
            'transportation': '5. 주요 교통수단은 무엇이었나요?',
            'duration': '6. 여름휴가 기간은 며칠이었나요?',
            'companion': '7. 휴가를 함께한 사람은 누구였나요?',
            'cost': '8. 이번 휴가에서 지출한 총 비용은 어느 정도였나요?',
            'satisfaction': '9. 이번 휴가에 대한 만족도는 어떠셨나요?',
            'next_vacation_type': '10. 다음 여름휴가에서는 어떤 경험을 가장 하고 싶으신가요?'
        }
        
        # 각 필드의 입력 위젯 설정
        widgets = {
            'age_group': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'vacation_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'location_type': forms.Select(attrs={
                'class': 'form-control location-type',
                'required': True
            }),
            'domestic_location': forms.Select(attrs={
                'class': 'form-control domestic-location',
                'style': 'display: none;'  # 처음에는 숨김
            }),
            'overseas_location': forms.Select(attrs={
                'class': 'form-control overseas-location', 
                'style': 'display: none;'  # 처음에는 숨김
            }),
            'transportation': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'duration': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'companion': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'cost': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'satisfaction': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'next_vacation_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        폼 초기화 시 실행되는 메서드
        빈 선택지를 추가하고 필드를 조건부로 설정
        """
        super().__init__(*args, **kwargs)
        
        # 모든 선택 필드에 "선택해주세요" 옵션 추가
        choice_fields = [
            'age_group', 'gender', 'vacation_type', 'location_type',
            'transportation', 'duration', 'companion', 'cost', 
            'satisfaction', 'next_vacation_type'
        ]
        
        for field_name in choice_fields:
            if field_name in self.fields:
                # 기존 choices에 빈 선택지 추가
                choices = [('', '선택해주세요')] + list(self.fields[field_name].choices)
                self.fields[field_name].choices = choices
        
        # 위치 관련 필드 설정
        # domestic_location과 overseas_location은 선택사항으로 설정
        self.fields['domestic_location'].required = False
        self.fields['overseas_location'].required = False
        
        # 빈 선택지 추가
        domestic_choices = [('', '국내 지역을 선택해주세요')] + list(self.fields['domestic_location'].choices)
        overseas_choices = [('', '해외 지역을 선택해주세요')] + list(self.fields['overseas_location'].choices)
        
        self.fields['domestic_location'].choices = domestic_choices
        self.fields['overseas_location'].choices = overseas_choices
    
    def clean(self):
        """
        폼 전체의 유효성 검증을 수행하는 메서드
        """
        cleaned_data = super().clean()
        location_type = cleaned_data.get('location_type')
        domestic_location = cleaned_data.get('domestic_location')
        overseas_location = cleaned_data.get('overseas_location')
        
        # 국내를 선택했는데 국내 지역을 선택하지 않은 경우
        if location_type == 'domestic' and not domestic_location:
            self.add_error('domestic_location', '국내 지역을 선택해주세요.')
        
        # 해외를 선택했는데 해외 지역을 선택하지 않은 경우
        if location_type == 'overseas' and not overseas_location:
            self.add_error('overseas_location', '해외 지역을 선택해주세요.')
        
        return cleaned_data