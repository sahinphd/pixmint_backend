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
    # Check for different possible field names for amount
    price_amount = data.get('price_amount') or data.get('order_amount') or data.get('amount')
    # Check for different possible field names for currency  
    currency = data.get('pay_currency') or data.get('order_currency') or data.get('currency')

    if not raw_user_id:
        return Response({'error': 'user_id is required'}, status=400)
    
    if not price_amount:
        return Response({
            'error': 'amount field is required', 
            'received_fields': list(data.keys()),
            'note': 'Please send price_amount, order_amount, or amount field'
        }, status=400)
    
    if not currency:
        return Response({
            'error': 'currency field is required',
            'received_fields': list(data.keys()),
            'note': 'Please send pay_currency, order_currency, or currency field'
        }, status=400)

    try:
        user_id_int = int(raw_user_id)
        price_amount = float(price_amount)  # Ensure price_amount is a valid number
    except (ValueError, TypeError):
        return Response({'error': 'user_id must be an integer and amount must be a valid number'}, status=400)

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
        
        # Use parameterized query to avoid SQL injection and handle None values properly
        insert_query = """
        INSERT INTO `orders_orderhistory`
        (`user_id`, `order_id`, `order_time`, `order_amount`, `order_currency`, `order_status`)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        insert_values = (
            user_id_int, 
            order_id, 
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            price_amount, 
            currency, 
            'waiting'
        )

        print(f"Insert query: {insert_query}")
        print(f"Insert values: {insert_values}")
        try:
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            cursor.execute(insert_query, insert_values)
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
        payment_data = {
            "price_amount": price_amount,
            "price_currency": f"{settings.ORDER_CURRENCY}",
            "pay_currency": f"{currency.upper()}",  # Convert to uppercase for payment API
            "ipn_callback_url": f"{settings.IPN_URL}",
            "order_id": f"{order_id}",
            "order_description": "MY Order"
        }
        print(f"Data to be sent: {payment_data}")
        try:
            response = requests.post(paymentUrl, headers=headers, json=payment_data)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 201:
                payment_response = response.json()
                filtered_data = {
                "payment_id": payment_response.get("payment_id"),
                "payment_status": payment_response.get("payment_status"),
                "pay_address": payment_response.get("pay_address"),
                "price_amount": payment_response.get("price_amount"),
                "price_currency": payment_response.get("price_currency"),
                "pay_currency": payment_response.get("pay_currency"),
                "order_id": payment_response.get("order_id")
            }
                # Optionally, you can log or manipulate the payment_data
                print(f"Response: {payment_response}")
                return Response(filtered_data, status=status.HTTP_200_OK)
            else:
                try:
                    error_response = response.json()
                    return Response({
                        'error': 'Failed to create payment',
                        'status_code': response.status_code,
                        'payment_api_error': error_response
                    }, status=response.status_code)
                except:
                    return Response({
                        'error': 'Failed to create payment',
                        'status_code': response.status_code,
                        'payment_api_response': response.text
                    }, status=response.status_code)

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

        user_totals = {user_id: total_amount for user_id, total_amount in results}
        return Response(user_totals, status=status.HTTP_200_OK)

    except mysql.connector.Error as err:
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def total_confirmed_order_amount(request):
    result = OrderHistory.objects.filter(order_status='confirmed').aggregate(total_amount=Sum('order_amount'))
    total_amount = result['total_amount'] or 0  # fallback to 0 if no records
    return Response({'total_confirmed_order_amount': total_amount})
