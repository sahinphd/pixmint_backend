from django.db import models
from UserFunctions.models import User  # ⬅ direct import of your custom user model

class Slab(models.Model):
    slab_name = models.CharField(max_length=100)
    slab_percentage = models.FloatField()
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    activate_status = models.BooleanField(default=True)

    def __str__(self):
        return self.slab_name


class UserSlab(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ⬅ direct reference
    slab = models.ForeignKey(Slab, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.usercode} - {self.slab.slab_name}"


class EarningHistory(models.Model):
    EARNING_TYPE_CHOICES = [
        ('refaralbonus', 'Refaral Bonus'),
        ('direct', 'Direct'),
        ('childa', 'Child A'),
        ('childb', 'Child B'),
        ('childc', 'Child C'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ⬅ direct reference
    earning_type = models.CharField(max_length=20, choices=EARNING_TYPE_CHOICES)
    earning_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10)
    earning_from = models.CharField(max_length=255)
    reason = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.usercode} - {self.earning_type} - {self.earning_amount} {self.currency}"
