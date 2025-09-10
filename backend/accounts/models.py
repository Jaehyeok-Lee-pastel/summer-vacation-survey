from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """사용자 추가 정보 저장"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(verbose_name='나이')  # 직접 입력 방식으로 변경
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.age}세'