from rest_framework import serializers
from .models import OrderHistory

# class OrderHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderHistory
#         # fields = '__all__'
#         fields = [
#             'user_id',
#              'order_id', 'payment_id', 
#             'order_time', 
#             'pay_currency',  'order_log', 
#             'payment_address', 'api_log'
#         ]
class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHistory
        fields = [
            'user_id',
            'order_id', 'payment_id',
            'order_time',
            'order_amount',            # include this
            'order_currency',          # include this
            'order_status',            # include this
            'pay_currency',
            'order_log',
            'payment_address',
            'api_log'
        ]
        read_only_fields = ['usercode', 'order_id', 'order_time']
        
        def validate(self, attrs):
            if 'price_amount' in attrs:
                # attrs['user_id'] = attrs.pop('user_id'),
                attrs['order_amount'] = attrs.pop('price_amount'),
                attrs['order_currency'] = attrs.pop('pay_currency')
            return attrs