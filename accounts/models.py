from django.db import models

# Create your models here.
# 사용자 인증 시스템 구현을 위한 모델 생성
# 커스텀 사용자 모델

# Django에서 제공하는 기본 사용자 모델을 가져옵니다
from django.contrib.auth.models import AbstractUser
# 데이터베이스 필드를 정의하기 위해 models를 가져옵니다
from django.db import models

class CustomUser(AbstractUser):
    """
    Django 기본 사용자 모델을 확장한 커스텀 사용자 모델
    기본 필드들 (username, email, password 등)은 AbstractUser에서 상속받고
    우리 프로젝트에 필요한 추가 필드들만 정의합니다
    """
    
    # 나이대 선택지를 튜플로 정의
    # ('저장될값', '화면에보여질값') 형태로 구성
    AGE_CHOICES = [
        ('10s', '10대'),    # 데이터베이스에는 '10s'로 저장, 화면에는 '10대'로 표시
        ('20s', '20대'),
        ('30s', '30대'),
        ('40s', '40대'),
        ('50s', '50대'),   # 50대 추가
        ('60s', '60대 이상'), # 60대 추가
    ]    
    
    # 나이 필드 추가
    age = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='나이'
    )
    
    # 나이대 필드 정의
    age_group = models.CharField(
        max_length=3,           # 최대 3글자까지 저장 ('10s', '20s' 등)
        choices=AGE_CHOICES,    # 위에서 정의한 선택지만 선택 가능
        null=True,              # 추가
        blank=True,             # 추가
        verbose_name='나이대'    # 관리자 페이지에서 보여질 필드명
    )
    
    # 계정 생성 시간을 자동으로 저장하는 필드
    created_at = models.DateTimeField(
        auto_now_add=True,      # 객체가 처음 생성될 때만 현재 시간 자동 저장
        verbose_name='가입일'
    )
    
    def __str__(self):
        """
        이 객체를 문자열로 표현할 때 사용되는 메서드
        관리자 페이지나 디버깅 시 사용자를 구분하기 쉽게 해줍니다
        """
        return f"{self.username} ({self.get_age_group_display()})"
        # get_age_group_display()는 Django가 자동으로 만들어주는 메서드
        # '10s' → '10대'로 변환해서 보여줍니다
    
    class Meta:
        """
        모델의 메타데이터를 정의하는 클래스
        """
        verbose_name = '사용자'        # 관리자 페이지에서 단수형으로 표시될 이름
        verbose_name_plural = '사용자들'  # 관리자 페이지에서 복수형으로 표시될 이름