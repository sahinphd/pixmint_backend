from django.db import models
from django.conf import settings  # ✅ Needed for AUTH_USER_MODEL reference


class Slab(models.Model):
    slab_name = models.CharField(max_length=100)           # Name of the slab
    slab_percentage = models.FloatField()                  # Percentage value for the slab
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field
    activate_status = models.BooleanField(default=True)    # Status to activate or deactivate the slab

    def __str__(self):
        return self.slab_name


class UserSlab(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slab = models.ForeignKey(Slab, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.slab.slab_name}"


class EarningHistory(models.Model):
    EARNING_TYPE_CHOICES = [
        ('Direct', 'Direct'),
        ('ChildA', 'Child A'),
        ('ChildB', 'Child B'),
        ('ChildC', 'Child C'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE_CHOICES)
    earning_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10)
    earning_from = models.CharField(max_length=255)  # Source of earning
    reason = models.TextField()  # Description/reason
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.earning_type} - {self.earning_amount} {self.currency}"
