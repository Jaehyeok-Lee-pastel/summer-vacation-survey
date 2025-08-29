from django.contrib import admin

# surveys/admin.py

from django.contrib import admin
from .models import Survey

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    """
    설문조사를 관리자 페이지에서 관리하기 위한 설정
    """
    
    # 목록 화면에서 보여질 컬럼들
    list_display = [
        'user', 
        'age_group', 
        'gender',
        'vacation_type', 
        'get_location_display',
        'satisfaction',
        'cost',
        'created_at'
    ]
    
    # 목록을 필터링할 수 있는 사이드바 옵션들
    list_filter = [
        'age_group',
        'gender', 
        'vacation_type',
        'location_type',
        'satisfaction',
        'cost',
        'companion',
        'created_at'
    ]
    
    # 검색 가능한 필드들
    search_fields = [
        'user__username',
        'user__email'
    ]
    
    # 목록에서 편집 가능한 필드들
    list_editable = [
        'satisfaction'
    ]
    
    # 한 페이지당 보여질 항목 수
    list_per_page = 20
    
    # 최신 설문이 위에 오도록 정렬
    ordering = ['-created_at']
    
    # 상세 페이지에서 필드들을 그룹으로 묶어서 표시
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'age_group', 'gender')
        }),
        ('휴가 정보', {
            'fields': ('vacation_type', 'location_type', 'domestic_location', 'overseas_location')
        }),
        ('세부 사항', {
            'fields': ('transportation', 'duration', 'companion', 'cost')
        }),
        ('평가', {
            'fields': ('satisfaction', 'next_vacation_type')
        }),
    )
    
    # 읽기 전용 필드 (수정 불가)
    readonly_fields = ['created_at']
    
    def get_location_display(self, obj):
        """
        목록에서 위치를 보기 좋게 표시하는 메서드
        """
        return obj.get_location_display()
    get_location_display.short_description = '여행 위치'