from django.urls import path
from .views import *

urlpatterns = [
    path("recent-vacation-ratio/", recent_vacation_by_age_activity, name="recent_vacation_by_age_ratio"),
    path("recent-vacation-ratio_all/", vacation_by_age_activity_all, name="vacation_by_age_activity_all"),
    path('vacation_male_only/', vacation_by_male_only, name='vacation_male_only'),
    path('vacation_female_only/', vacation_by_female_only, name='vacation_female_only'),
    path('companion_by_age/', companion_by_age_activity, name='companion_by_age'),
    path('next_vacation_by_age/', next_vacation_by_age_activity, name='next_vacation_by_age'),
    path('ml-recommendation/', get_ml_recommendation_api, name='ml_recommendation_api'),
]

