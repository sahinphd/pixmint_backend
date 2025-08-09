# orders/models.py
from django.db import models
from django.utils import timezone
from UserFunctions.models import User  # Import your user model

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

class OrderHistory(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(blank=True)
    order_id = models.CharField(max_length=100, unique=True, blank=True)
    payment_id = models.CharField(max_length=100,  blank=True, default="")
    order_time = models.DateTimeField(default=timezone.now, blank=True)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_currency = models.CharField(max_length=10, blank=True)
    pay_currency = models.CharField(max_length=10, blank=True, default="")
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, blank=True)
    order_log = models.CharField(max_length=255, blank=True, default="")
    payment_address = models.CharField(max_length=255, blank=True, default="")
    api_log = models.CharField(max_length=255, blank=True, default="")

    def save(self, *args, **kwargs):
        if not self.order_id:
            date_str = self.order_time.strftime('%d%m%y')
            usercode = getattr(self, 'usercode', None)  # Fetch usercode from the instance
            if not usercode:  # If usercode is not provided, raise an exception
                raise ValueError("Can't find proper usercode for generating order_id.")
            self.order_id = f"PIX{usercode}-{self.user_id}-{date_str}{self.id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_id}"
