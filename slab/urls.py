from django.urls import path
from . import views

urlpatterns = [
    # path('daily-earning/', views.daily_earning_view),
    # path('team-earning/', views.team_earning_view),
    path('earning_list_by_user/', views.earning_list_by_user),
]
