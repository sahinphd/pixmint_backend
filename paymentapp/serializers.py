from rest_framework import serializers
from .models import TransactionLog



class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        fields = '__all__'
        read_only_fields = ( 'time', 'request_id', 'orderID')  # optional: 'id' and 'time' are auto-generated
        
