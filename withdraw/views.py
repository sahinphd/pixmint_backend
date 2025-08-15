# from datetime import timezone
from decimal import Decimal
from gettext import translation
from multiprocessing import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Withdraw
from wallet.utils import update_wallet_balance
# from .serializers import WithdrawSerializer
from django.conf import settings
from django.db.models import Sum
import mysql.connector
from datetime import datetime



# # Create Withdraw
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def withdraw_create(request):
#     serializer = WithdrawSerializer(data=request.data, context={'request': request})
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # List Withdrawals
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def withdraw_list(request):
#     withdrawals = Withdraw.objects.filter(user=request.user).order_by('-withdraw_date')
#     serializer = WithdrawSerializer(withdrawals, many=True)
#     return Response(serializer.data)


# @api_view(['POST'])  # Changed to POST so payload can have JSON
# @permission_classes([IsAuthenticated])
# def withdraw_list(request):
#     user_id = request.data.get('user_id')  # Get from JSON body
#     if not user_id:
#         return Response({"error": "user_id is required"}, status=400)

#     withdrawals = Withdraw.objects.filter(user_id=user_id).order_by('-withdraw_date')
#     serializer = WithdrawSerializer(withdrawals, many=True)
#     return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_create_raw_sql(request):
    user = request.user
    user_id = request.data.get('user_id')
    withdraw_amount = request.data.get('withdraw_amount')
    remarks = request.data.get('remarks')

    try:
        withdraw_amount = Decimal(withdraw_amount)
    except (TypeError, ValueError):
        return Response({"error": "Invalid withdraw_amount"}, status=status.HTTP_400_BAD_REQUEST)

    if withdraw_amount <= 0:
        return Response({"error": "Withdrawal amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

    if withdraw_amount > 15:
        return Response({"error": "Maximum withdrawal amount is $15"}, status=status.HTTP_400_BAD_REQUEST)

    # with connection.cursor() as cursor:
    # Fetch wallet balance safely
    config = settings.MYSQL_CONNECTOR_CONFIG

    try:

        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute(f"SELECT wallet_balance FROM wallet_wallet WHERE user_id = {user_id}")
        row = cursor.fetchone()
    except mysql.connector.Error as err:
        return Response({'error': str(err)}, status=500)
    finally:
        cursor.close()
        conn.close()
        
    if row is None:
        return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
    wallet_balance = row[0]
    if withdraw_amount >= wallet_balance:
        return Response({"error": "Cannot withdraw full or more than wallet balance"}, status=status.HTTP_400_BAD_REQUEST)
    # predicted_balance = wallet_balance - withdraw_amount
    predicted_balance = update_wallet_balance(user_id)
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print(f"predicted_balance: {predicted_balance}")
        insert_withdraw_withdraw = f"""
            INSERT INTO withdraw_withdraw (user_id, withdraw_amount, total_amount, withdraw_date, order_status, remarks)
            VALUES ({user_id},{withdraw_amount}, {predicted_balance}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', 'waiting', '{remarks}')
            """
        print(f"insert_withdraw_withdraw: {insert_withdraw_withdraw}")
        cursor.execute(insert_withdraw_withdraw)
        print("execute")
        
        # Directly update wallet balance (optional if using update_wallet_balance function)
        cursor.execute(f"""
            UPDATE wallet_wallet 
            SET wallet_balance = {predicted_balance}
            WHERE user_id = {user_id}
            """)
        conn.commit()
        return Response({
        "message": "Withdraw created",
        "withdraw_amount": str(withdraw_amount),
        "predicted_balance": str(predicted_balance),
                }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": "Database error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()
    
#withdraw history
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_list_raw_sql(request):
    user_id = request.data.get('user_id')
    withdraw_sql = f"""
                    SELECT withdraw_amount, total_amount, withdraw_date, order_status, remarks FROM withdraw_withdraw WHERE user_id = {user_id}
                    """
    config = settings.MYSQL_CONNECTOR_CONFIG
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(withdraw_sql)
        rows = cursor.fetchall()
        return Response(rows, status=200)
    except Exception as e:
        return Response({"error": "Database error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        cursor.close()
        conn.close()
    
