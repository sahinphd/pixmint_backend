from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import TransactionLog
from django.db.models import Sum

from .serializers import TransactionLogSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transaction_log_create(request):
    # data = request.data.copy()
    # data['userID'] = request.user.id  # ✅ set userID manually

    # serializer = TransactionLogSerializer(data=data)
    # if serializer.is_valid():
    #     serializer.save()  
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = request.data.copy()
    data['userID'] = request.user.id if request.user.is_authenticated else 1  # adjust for real auth

    serializer = TransactionLogSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def total_amount_by_user_id(request):
    user_id = request.data.get("userID")

    if not user_id:
        return Response({"error": "userID is required in the request body."}, status=status.HTTP_400_BAD_REQUEST)

    total = TransactionLog.objects.filter(userID=user_id).aggregate(total_amount=Sum('price_amount'))

    if total["total_amount"] is None:
        return Response({"message": f"No transactions found for userID {user_id}."}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "userID": user_id,
        "total_amount": total["total_amount"]
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    user_id = request.user.id
    transactions = TransactionLog.objects.filter(userID=user_id).order_by('-time')
    serializer = TransactionLogSerializer(transactions, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
