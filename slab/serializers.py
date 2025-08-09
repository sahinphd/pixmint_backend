from rest_framework import serializers
from .models import Slab

class SlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slab
        fields = ['id', 'slab_name', 'slab_percentage', 'activate_status']
