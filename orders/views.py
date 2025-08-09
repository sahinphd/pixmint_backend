# orders/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import OrderHistory
from .serializers import OrderHistorySerializer
# import mysql.connector
from django.conf import settings
from django.db.models import Sum
import mysql.connector
from datetime import datetime
import requests

constantstring = "PIX"

@api_view(['POST'])
def create_order(request):
    data = request.data.copy()
    print(f"Data:: {data}")
    print(f"Data:: {data.get('user_id')}")
    raw_user_id = data.get('user_id')
    price_amount = data.get('price_amount')
    currency = data.get('pay_currency')

    if not raw_user_id:
        return Response({'error': 'user_id is required'}, status=400)

    try:
        user_id_int = int(raw_user_id)
    except ValueError:
        return Response({'error': 'user_id must be an integer'}, status=400)

    # Secure query using mysql.connector
    config = settings.MYSQL_CONNECTOR_CONFIG
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT usercode FROM UserFunctions_user WHERE id = %s", (user_id_int,))
        print(f"Executing query: SELECT userid FROM UserFunctions_user WHERE id = {user_id_int}")

        result = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        return Response({'error': str(err)}, status=500)

    if result:
        user_code = result[0]
        data['user_id'] = user_id_int
        data['usercode'] = user_code  # Pass user_id as usercode
        
        print(f"to_serializer data {data}")
        order_id = f"{constantstring}{user_code}-{user_id_int}{datetime.now().strftime('%Y%m%d%H%M%S')}"
        insert_query = f"""
INSERT INTO `orders_orderhistory`
(`user_id`, `order_id`,  `order_time`, `order_amount`, `order_currency`, 
`order_status`)
VALUES ({user_id_int}, '{order_id}', '{datetime.now().strftime('%Y-%m-%d')}', 
{price_amount}, '{currency}', 'waiting');

"""
#         insert_query = f"""
# INSERT INTO `spaceaius`.`orders_orderhistory`
# (`user_id`, `order_id`,  `order_time`, `order_amount`, `order_currency`, 
# `order_status`)
# VALUES ({user_id_int}, '{order_id}',  '{datetime.now().strftime('%Y-%m-%d')}', 
# {price_amount},'{currency}' , "waiting");
# """
        print(f"Insert query: {insert_query}")
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(insert_query)
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            return Response({'error': str(err)}, status=500)
        
        paymentUrl = f"{settings.BASE_PAYMENT_URL}/v1/payment"


        headers = {
            'x-api-key': f'{settings.PAYMENT_API_KEY}',  # Replace with your actual API key
            'Content-Type': 'application/json'
        }

        # Set the payload (data)
        data = {
            "price_amount": price_amount,
            "price_currency": f"{settings.ORDER_CURRENCY}",
            "pay_currency": f"{currency}",
            "ipn_callback_url": f"{settings.IPN_URL}",
            "order_id": f"{order_id}",
            "order_description": "MY Order"
        }
        print(f"Data to be sent: {data}")
        try:
            response = requests.post(paymentUrl, headers=headers, json=data)
            print(f"Response status code: {response.json()}")
            if response.status_code == 201:
                payment_data = response.json()
                filtered_data = {
                "payment_id": payment_data.get("payment_id"),
                "payment_status": payment_data.get("payment_status"),
                "pay_address": payment_data.get("pay_address"),
                "price_amount": payment_data.get("price_amount"),
                "price_currency": payment_data.get("price_currency"),
                "pay_currency": payment_data.get("pay_currency"),
                "order_id": payment_data.get("order_id")
            }
                # Optionally, you can log or manipulate the payment_data
                print(f"Response: {payment_data}")
                return Response(filtered_data, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to create payment'}, status=response.status_code)

        except requests.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # return Response("HI", status=status.HTTP_400_BAD_REQUEST)
        # serializer = OrderHistorySerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': f"User with id {user_id_int} does not exist."}, status=404)

@api_view(['GET'])
def get_order(request, pk):
    try:
        order = OrderHistory.objects.get(pk=pk)
    except OrderHistory.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderHistorySerializer(order)
    return Response(serializer.data)

@api_view(['GET'])
def list_orders(request):
    orders = OrderHistory.objects.all()
    serializer = OrderHistorySerializer(orders, many=True)
    return Response(serializer.data)

# total_amount userwise on Confirmed orders
@api_view(['POST'])   
def total_amount_userwise(request):
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        config = settings.MYSQL_CONNECTOR_CONFIG
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, SUM(order_amount) AS total_amount
            FROM orders_orderhistory
            WHERE order_status = 'confirmed'
            AND user_id = %s
        """, (user_id,) )
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        print(f"Results: {results[0][1]}")
        # total_amount = results[0] if results[0] is not None else 0
        return Response({'total_amount': results[0][1]}, status=status.HTTP_200_OK)

        # user_totals = {user_id: total_amount for user_id, total_amount in results}
        # total_amount = result[0] if result[0] is not None else 0
        # return Response({'total_amount': total_amount in results}, 
        # return Response(user_totals, status=status.HTTP_200_OK)

    except mysql.connector.Error as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# @api_view(['GET'])
# def total_confirmed_order_amount(request):
#     result = OrderHistory.objects.filter(order_status='confirmed').aggregate(total_amount=Sum('order_amount'))
#     total_amount = result['total_amount'] or 0  # fallback to 0 if no records
#     return Response({'total_confirmed_order_amount': total_amount})
