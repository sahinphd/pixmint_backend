from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Slab
from .serializers import SlabSerializer
from django.conf import settings
import mysql.connector
import json

# Add new Slab
@api_view(['POST'])
def add_slab(request):
    serializer = SlabSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Slab created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Show all Slabs
@api_view(['GET'])
def show_slabs(request):
    slabs = Slab.objects.all()
    serializer = SlabSerializer(slabs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def self_calculation(userID):
    query = f"""
            SELECT 
    SUM(o.order_amount) AS total_confirmed_amount,
    s.slab_name,
    s.slab_percentage,
    (SUM(o.order_amount) * s.slab_percentage / 100) AS calculated_value
        FROM orders_orderhistory o
        JOIN slab_userslab su ON o.user_id = su.user_id
        JOIN slab_slab s ON su.slab_id = s.id
        WHERE o.order_status = 'confirmed'
          AND o.user_id = {userID}
        GROUP BY s.slab_name, s.slab_percentage;

        """
    config = settings.MYSQL_CONNECTOR_CONFIG
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(query)
        print(f"Executing query:  {query}")

        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result
        
    except mysql.connector.Error as err:
        return Response({'error': str(err)}, status=500)
    

# @api_view(['POST'])
# def daily_income(request):
#     data = request.data.copy()
#     raw_user_id = data.get('user_id')
#     Result = self_calculation(raw_user_id)

@api_view(['POST'])
def earning_list_by_user(request):
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "userID is required"}, status=status.HTTP_400_BAD_REQUEST)

    # earnings = Slab.objects.filter(user_id=user_id).order_by('-datetime')
    # serializer = Slab(earnings, many=True)
    # return Response(serializer.data)
    config = settings.MYSQL_CONNECTOR_CONFIG

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT datetime, earning_amount, currency, earning_from, reason, earning_type  FROM slab_earninghistory 
                   WHERE user_id = %s

        """, (user_id,) )
    # results = cursor.fetchall()
    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows and map with column names
    results = cursor.fetchall()
    data = [dict(zip(columns, row)) for row in results]

    cursor.close()
    conn.close()
    
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def total_earning_by_user(request):
    # user_id = request.query_params.get('userID', None)  # Get from URL query params ?userID=123
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "userID is required"}, status=status.HTTP_400_BAD_REQUEST)
    config = settings.MYSQL_CONNECTOR_CONFIG

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("""
    SELECT sum(earning_amount) AS total_earning_amount  FROM slab_earninghistory 
                   WHERE user_id = %s

        """, (user_id,) )
    # results = cursor.fetchall()
    # Get column names
    columns = [desc[0] for desc in cursor.description]

    # Fetch all rows and map with column names
    results = cursor.fetchall()
    data = [dict(zip(columns, row)) for row in results]

    cursor.close()
    conn.close()
    
    return Response(data, status=status.HTTP_200_OK)