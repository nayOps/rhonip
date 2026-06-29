from mission.views import Mission
from django.urls import path

app_name = 'mission'

urlpatterns = [
    path('mission/<int:pk>', Mission.as_view(), name='mission'),
]
