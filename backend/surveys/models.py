from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    AGE_CHOICES = [
        ('10대','10대'), ('20대','20대'), ('30대','30대'), ('40대','40대'), ('50대','50대'), ('60대 이상','60대 이상')
    ]
    GENDER_CHOICES = [('남성','남성'), ('여성','여성')]
    VACATION_CHOICES = [
        ('해수욕, 물놀이','해수욕, 물놀이'), ('등산, 캠핑','등산, 캠핑'), ('문화생활','문화생활'),
        ('도시 관광','도시 관광'), ('휴양·힐링','휴양·힐링'), ('맛집 투어','맛집 투어'),
        ('친척·지인 방문','친척·지인 방문'), ('기타','기타')
    ]
    LOCATION_CHOICES = [('국내','국내'), ('해외','해외')]
    TRANSPORT_CHOICES = [('자동차','자동차'), ('버스','버스'), ('기차','기차'), ('항공편','항공편'), ('배','배'), ('도보','도보')]
    DURATION_CHOICES = [('1일','1일'), ('2~3일','2~3일'), ('4~6일','4~6일'), ('7~15일','7~15일'), ('15일 이상','15일 이상')]
    COMPANION_CHOICES = [('혼자','혼자'), ('가족','가족'), ('친구','친구'), ('연인','연인'), ('직장 동료','직장 동료'), ('동호회','동호회'), ('기타','기타')]
    COST_CHOICES = [('10만 원 이하','10만 원 이하'), ('10만~30만 원','10만~30만 원'), ('30만~50만 원','30만~50만 원'), ('50만~100만 원','50만~100만 원'), ('100만~200만 원','100만~200만 원'), ('200만 원 이상','200만 원 이상')]

    age_group = models.CharField(max_length=10, choices=AGE_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    vacation_type = models.CharField(max_length=20, choices=VACATION_CHOICES)
    location_type = models.CharField(max_length=10, choices=LOCATION_CHOICES)
    domestic_location = models.CharField(max_length=20, blank=True, null=True)
    overseas_location = models.CharField(max_length=20, blank=True, null=True)
    transportation = models.CharField(max_length=20, choices=TRANSPORT_CHOICES)
    duration = models.CharField(max_length=15, choices=DURATION_CHOICES)
    companion = models.CharField(max_length=20, choices=COMPANION_CHOICES)
    cost = models.CharField(max_length=15, choices=COST_CHOICES)
    satisfaction = models.IntegerField()  # 1~5점
    next_vacation_type = models.CharField(max_length=20, choices=VACATION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.vacation_type}"
