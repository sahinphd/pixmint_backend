from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .utils import update_wallet_balance
from .serializers import WalletSerializer

@api_view(['POST'])
def update_and_get_wallet(request):
    print("update_and_get_wallet")
    # return Response("abc")
    try:
        # Extract user_id from payload
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Update wallet
        wallet = update_wallet_balance(user_id)

        # Serialize and return updated wallet data
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)

    
