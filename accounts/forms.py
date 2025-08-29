# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# CustomUser 모델을 동적으로 가져옵니다
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """
    Django 기본 회원가입 폼을 확장한 커스텀 회원가입 폼
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='이름',
        help_text='실명을 입력해주세요',
        widget=forms.TextInput(attrs={
            'placeholder': '이름을 입력하세요',
            'class': 'form-control'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label='이메일',
        help_text='@naver.com 형식으로 입력하세요',
        widget=forms.EmailInput(attrs={
            'placeholder': '이메일을 입력하세요',
            'class': 'form-control'
        })
    )
    
    age = forms.IntegerField(
        min_value=10,
        max_value=100,
        required=True,
        label='나이',
        help_text='나이를 입력하세요 (10-100세)',
        widget=forms.NumberInput(attrs={
            'placeholder': '나이를 입력하세요',
            'min': '10',
            'max': '100',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User  # get_user_model()로 가져온 User 사용
        fields = ('username', 'first_name', 'email', 'age', 'password1', 'password2')
        
        labels = {
            'username': '아이디',
            'password1': '비밀번호',
            'password2': '비밀번호 확인',
        }
        
        help_texts = {
            'username': '영문, 숫자, @/./+/-/_ 문자만 사용 가능합니다.',
        }
        
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': '아이디를 입력하세요',
                'class': 'form-control'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': '비밀번호를 입력하세요',
                'class': 'form-control'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': '비밀번호를 다시 입력하세요',
                'class': 'form-control'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            import re
            if not re.match(r'^([a-zA-Z0-9._%+-]+)@naver\.com$', email):
                raise forms.ValidationError('이메일은 @naver.com 형식이어야 합니다.')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            import re
            if not re.match(r'^[가-힣]+$', first_name):
                raise forms.ValidationError('이름은 한글만 입력 가능합니다.')
        return first_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.email = self.cleaned_data['email']
        user.age = self.cleaned_data['age']
        
        # 나이를 기반으로 age_group 자동 설정
        age = self.cleaned_data['age']
        if age < 20:
            user.age_group = '10s'
        elif age < 30:
            user.age_group = '20s'
        elif age < 40:
            user.age_group = '30s'
        elif age < 50:
            user.age_group = '40s'
        elif age < 60:
            user.age_group = '50s'
        else:
            user.age_group = '60s'
        
        if commit:
            user.save()
        
        return user