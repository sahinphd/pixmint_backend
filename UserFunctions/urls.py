from django.urls import path
from .views import (register_user, 
                    get_profile, 
                    get_user_detail_by_id, 
                    MyTokenObtainPairView,
                    user_hierarchy_by_userid,
                    change_password,
                    email_verify,verify_otp)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('register/', register_user, name='register'),
    path('profile/', get_profile, name='profile'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('userdetail/<int:user_id>/', get_user_detail_by_id, name='get_user_detail_by_id'),
    path('hierarchy_by_userid/', user_hierarchy_by_userid, name='get_user_detail_by_id'),
    path('change_password/', change_password, name='get_user_detail_by_id'),
    path('email_verify/', email_verify, name='get_user_detail_by_id'),
    path('verify_otp/', verify_otp, name='verify_otp'),
]
