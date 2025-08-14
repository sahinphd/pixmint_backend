from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Slab
from .serializers import SlabSerializer
from django.conf import settings
import mysql.connector

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
    

@api_view(['POST'])
def daily_income(request):
    data = request.data.copy()
    raw_user_id = data.get('user_id')
    Result = self_calculation(raw_user_id)

