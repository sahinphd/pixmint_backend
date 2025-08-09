from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer, UserDetailSerializer,MyTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    data = {
        "id": user.id,
        "userid": user.userid,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active
    }
    return Response(data)

@api_view(['GET'])
def get_user_detail_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserDetailSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(["POST"])
def user_hierarchy_by_userid(request):
    """
    Given a user's id, return up to 3 levels of descendants.
    Labels:
        A = Child
        B = Grandchild
        C = Great-grandchild
    """
    user_id = request.data.get("user_id")
    if not user_id:
        return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Lookup usercode from user_id
    try:
        parent = User.objects.get(id=user_id)
        parent_usercode = parent.usercode
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    output = []

    # Level A (Children)
    children = User.objects.filter(refarcode=parent_usercode)
    for child in children:
        output.append({
            "label": "A",
            "id": child.id,
            "userid": child.userid,
            "name": child.name,
            "email": child.email,
            "usercode": child.usercode,
            "refarcode": child.refarcode
        })

        # Level B (Grandchildren)
        grandchildren = User.objects.filter(refarcode=child.usercode)
        for grandchild in grandchildren:
            output.append({
                "label": "B",
                "id": grandchild.id,
                "userid": grandchild.userid,
                "name": grandchild.name,
                "email": grandchild.email,
                "usercode": grandchild.usercode,
                "refarcode": grandchild.refarcode
            })

            # Level C (Great-grandchildren)
            great_grands = User.objects.filter(refarcode=grandchild.usercode)
            for great_grand in great_grands:
                output.append({
                    "label": "C",
                    "id": great_grand.id,
                    "userid": great_grand.userid,
                    "name": great_grand.name,
                    "email": great_grand.email,
                    "usercode": great_grand.usercode,
                    "refarcode": great_grand.refarcode
                })

    return Response(output, status=status.HTTP_200_OK)
