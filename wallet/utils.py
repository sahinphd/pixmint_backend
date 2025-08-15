from django.db.models import Sum
from .models import Wallet
from withdraw.models import Withdraw
from orders.models import OrderHistory  # Use your existing order model

# def update_wallet_balance(user_id):
#     # Calculate the total of confirmed orders
#     total_confirmed = OrderHistory.objects.filter(
#         user_id=user_id,
#         order_status='confirmed'
#     ).aggregate(total=Sum('order_amount'))['total'] or 0

#     # Create or update wallet entry
#     wallet, created = Wallet.objects.get_or_create(user_id=user_id)
#     wallet.wallet_balance = total_confirmed
#     wallet.save()


def update_wallet_balance(user_id):
    # Step 1: Sum of confirmed orders
    total_confirmed = OrderHistory.objects.filter(
        user_id=user_id,
        order_status='confirmed'
    ).aggregate(total=Sum('order_amount'))['total'] or 0

    # Step 2: Sum of all withdrawals
    total_withdrawn = Withdraw.objects.filter(
        user_id=user_id
    ).aggregate(total=Sum('withdraw_amount'))['total'] or 0

    # Step 3: Calculate available balance
    available_balance = total_confirmed - total_withdrawn
    if available_balance < 0:
        available_balance = 0  # just in case

    # Step 4: Update or create wallet
    wallet, created = Wallet.objects.get_or_create(user_id=user_id)
    wallet.wallet_balance = available_balance
    wallet.save()

    # return wallet
    return available_balance

