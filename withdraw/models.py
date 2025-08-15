from django.db import models
from django.conf import settings  # for AUTH_USER_MODEL

ORDER_STATUS_CHOICES = [
    ('waiting', 'Waiting'),
    ('confirming', 'Confirming'),
    ('confirmed', 'Confirmed'),
    ('sending', 'Sending'),
    ('partially_paid', 'Partially Paid'),
    ('finished', 'Finished'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
    ('expired', 'Expired'),
]

class Withdraw(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    withdraw_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    withdraw_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, blank=True)

    def __str__(self):
        return f"{self.user} withdrew {self.withdraw_amount}"
