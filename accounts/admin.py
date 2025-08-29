from django.contrib import admin

# Django에서 제공하는 관리자 기능을 가져옵니다
from django.contrib import admin
# Django에서 제공하는 기본 사용자 관리 클래스를 가져옵니다
from django.contrib.auth.admin import UserAdmin
# 우리가 만든 CustomUser 모델을 가져옵니다
from .models import CustomUser

# @admin.register 데코레이터를 사용해서 CustomUser 모델을 관리자 페이지에 등록
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    CustomUser 모델을 관리자 페이지에서 어떻게 보여줄지 설정하는 클래스
    UserAdmin을 상속받아서 Django의 기본 사용자 관리 기능을 그대로 사용하면서
    우리가 추가한 필드(age_group)도 함께 관리할 수 있게 만듭니다
    """
    
    # 관리자 페이지의 사용자 목록에서 보여질 컬럼들을 지정
    list_display = ('username', 'email', 'age_group', 'is_staff', 'created_at')
    # 각 컬럼의 의미:
    # - username: 사용자명
    # - email: 이메일 주소
    # - age_group: 나이대 (우리가 추가한 필드!)
    # - is_staff: 관리자 권한 여부
    # - created_at: 가입일 (우리가 추가한 필드!)
    
    # 사용자 목록을 필터링할 수 있는 사이드바 옵션들
    list_filter = ('age_group', 'is_staff', 'is_active', 'created_at')
    # 각 필터의 의미:
    # - age_group: 나이대별로 필터링
    # - is_staff: 관리자/일반사용자로 필터링
    # - is_active: 활성/비활성 사용자로 필터링
    # - created_at: 가입일별로 필터링
    
    # 기존 사용자를 수정할 때 보여질 폼의 구성
    # UserAdmin.fieldsets은 Django 기본 필드들의 구성이고
    # 우리는 여기에 추가 정보 섹션을 더합니다
    fieldsets = UserAdmin.fieldsets + (
        # 새로운 섹션 추가: '추가 정보'라는 제목으로
        ('추가 정보', {
            'fields': ('age_group',)  # 이 섹션에는 age_group 필드만 포함
        }),
    )
    
    # 새 사용자를 추가할 때 보여질 폼의 구성
    # UserAdmin.add_fieldsets은 Django 기본 사용자 추가 폼이고
    # 우리는 여기에도 추가 정보 섹션을 더합니다
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('age_group',)  # 새 사용자 생성 시에도 나이대 선택 가능
        }),
    )
