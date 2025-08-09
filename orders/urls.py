from django.urls import path
from orders import views
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView
# )

urlpatterns = [
    path('create/', views.create_order , name='create_order'),
    path('list/', views.list_orders, name='list_orders'),
    path('detail/<int:pk>/', views.get_order, name='get_order'),
    path('totalamount/', views.total_amount_userwise, name='total_amount_userwise'),
    # path('total_confirmed/', views.total_confirmed_order_amount, name='total_confirmed_order_amount'),
]
