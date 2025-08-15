# from rest_framework import serializers
# from .models import Withdraw
# from wallet.models import Wallet
# from wallet.utils import update_wallet_balance

# class WithdrawSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Withdraw
#         fields = '__all__'
#         read_only_fields = ['id', 'total_amount', 'withdraw_date', 'user', 'order_status']

#     def create(self, validated_data):
#         user = self.context['request'].user

#         # Get current wallet
#         wallet = Wallet.objects.get(user=user)

#         amount = validated_data['withdraw_amount']
#         if amount >= wallet.wallet_balance:
#             raise serializers.ValidationError("You cannot withdraw the full or more than available amount.")
#         if amount >= 15:
#             raise serializers.ValidationError("You cannot withdraw more then 15 doller.")
#         # Predict balance after withdrawal
#         predicted_balance = wallet.wallet_balance - amount
#         validated_data['user'] = user
#         validated_data['total_amount'] = predicted_balance

#         # Save withdrawal record first with correct total_amount
#         withdraw = super().create(validated_data)

#         # Now update wallet balance from OrderHistory
#         update_wallet_balance(user.id)

#         return withdraw
