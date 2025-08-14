# from datetime import datetime, date
# from decimal import Decimal
# from django.db.models import Q, Sum
# from .models import EarningHistory, User, UserSlab, Slab

# def insert_earning(user, earning_type, amount, earning_from, reason, earning_date=None):
#     if earning_date is None:
#         earning_date = date.today()
#     # Check if already paid
#     exists = EarningHistory.objects.filter(
#         user_id=user.id,
#         earning_type=earning_type,
#         datetime__date=earning_date,
#         earning_from=earning_from
#     ).exists()
#     if exists:
#         return False  # Already paid
#     EarningHistory.objects.create(
#         user=user,
#         earning_type=earning_type,
#         earning_amount=Decimal(amount),
#         currency='INR',  # Use your default or dynamic
#         earning_from=earning_from,
#         reason=reason,
#         datetime=datetime.now()  # Or earning_date as start of day
#     )
#     return True

# def get_user_slab(user):
#     try:
#         user_slab = UserSlab.objects.get(user=user)
#         return user_slab.slab
#     except UserSlab.DoesNotExist:
#         return None

# def daily_earning_for_user(user, principal_amount, earning_date=None, remarks=''):
#     slab = get_user_slab(user)
#     if not slab or slab.slab_percentage is None:
#         return None
#     percent = Decimal(slab.slab_percentage) / 100
#     daily_earning = Decimal(principal_amount) * percent
#     res = insert_earning(
#         user=user,
#         earning_type='Direct',
#         amount=daily_earning,
#         earning_from='Self Invest',
#         reason=remarks or f'Daily earning for {earning_date or date.today()}',
#         earning_date=earning_date
#     )
#     return daily_earning if res else None

# def descendants_by_level(user, levels=3):
#     result = {'A': [], 'B': [], 'C': []}
#     levelA = User.objects.filter(refarcode=user.usercode)
#     result['A'] = list(levelA)
#     levelB, levelC = [], []
#     for a in levelA:
#         Busers = User.objects.filter(refarcode=a.usercode)
#         levelB.extend(Busers)
#         for b in Busers:
#             Cusers = User.objects.filter(refarcode=b.usercode)
#             levelC.extend(Cusers)
#     result['B'] = list(levelB)
#     result['C'] = list(levelC)
#     return result

# def calculate_and_insert_team_earning(parent_user, principal_lookup, generation_label, percent=12, earning_date=None, remarks=''):
#     # principal_lookup: dict {user.id: principal_amount}
#     gens = descendants_by_level(parent_user)[generation_label]
#     total_earning = Decimal('0')
#     for u in gens:
#         principal = principal_lookup.get(u.id, Decimal('0'))
#         slab = get_user_slab(u)
#         if slab:
#             percent_ = Decimal(slab.slab_percentage) / 100
#             daily_earning = Decimal(principal) * percent_
#             total_earning += daily_earning
#     bonus = total_earning * (Decimal(percent) / 100)
#     return insert_earning(
#         user=parent_user,
#         earning_type=f"Child{generation_label}",
#         amount=bonus,
#         earning_from=f'Level{generation_label}',
#         reason=remarks or f'Team benefit {generation_label} for {earning_date or date.today()}',
#         earning_date=earning_date
#     )
