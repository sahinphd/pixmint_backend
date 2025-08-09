from django.urls import path
from paymentapp import views
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView
# )

urlpatterns = [
    path('transactionLog/', views.transaction_log_create, name='TransactionLog_create'),
    path('totalamount/', views.total_amount_by_user_id, name='TransactionLog_total_amount'),
    path('paymenthistory/', views.payment_history, name='TransactionLog_payment_history'),
]
