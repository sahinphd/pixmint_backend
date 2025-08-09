from django.db import models
from datetime import datetime

class TransactionLog(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-increment primary key
    userID = models.IntegerField()
    request_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    orderID = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    price_currency = models.CharField(max_length=10)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded')
        ]
    )
    pay_address = models.TextField()
    price_amount = models.DecimalField(max_digits=20, decimal_places=8)
    pay_currency = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        # If no request_id, generate it BEFORE saving the first time
        if not self.request_id:
            now = datetime.now()
            month_year = now.strftime("%m%Y")

            # Use a temporary save to get the ID if not set yet
            if not self.id:
                super().save(*args, **kwargs)  # Save to get id
            
            self.request_id = f"REQ{month_year}{self.id}"

        if not self.orderID:
            now = datetime.now()
            date_str = now.strftime("%d%m%y")
            self.orderID = f"{self.userID}_{date_str}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.orderID} by UserID {self.userID}"
