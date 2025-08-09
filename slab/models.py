from django.db import models

class Slab(models.Model):
    slab_name = models.CharField(max_length=100)          # Name of the slab
    slab_percentage = models.FloatField()                  # Percentage value for the slab
    activate_status = models.BooleanField(default=True)   # Status to activate or deactivate the slab

    def __str__(self):
        return self.slab_name
