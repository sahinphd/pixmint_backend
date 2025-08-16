from rest_framework import serializers
from .models import Slab, EarningHistory

class SlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slab
        fields = ['id', 'slab_name', 'slab_percentage', 'max_amount', 'activate_status']



class EarningHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EarningHistory
        fields = [
            'id',
            'user',
            'earning_type',
            'earning_amount',
            'currency',
            'earning_from',
            'reason',
            'datetime',
        ]
        read_only_fields = ['id', 'datetime']  # auto-generated, should not be edited
