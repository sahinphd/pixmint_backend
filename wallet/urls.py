from django.urls import path
from .views import update_and_get_wallet

urlpatterns = [
    path('update/', update_and_get_wallet, name='update_and_get_wallet'),
]
