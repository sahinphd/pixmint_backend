from django.db import models
from UserFunctions.models import User  # Your custom user model

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # order_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user}'s wallet"
