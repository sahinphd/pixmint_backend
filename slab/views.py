from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Slab
from .serializers import SlabSerializer

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
