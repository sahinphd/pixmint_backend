from django.urls import path
# from .views import withdraw_create, withdraw_list, withdraw_create_raw_sql
from .views import   withdraw_create_raw_sql,withdraw_list_raw_sql

urlpatterns = [
    path('withdraw_amount/', withdraw_create_raw_sql, name='withdraw-create'),
    # path('withdraw_amount/', withdraw_create_raw_sql, name='withdraw'),
    path('history/', withdraw_list_raw_sql, name='withdraw-list'),
]
