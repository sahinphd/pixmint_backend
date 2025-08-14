from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserRegisterSerializer, UserDetailSerializer,MyTokenObtainPairSerializer
from django.core.cache import cache

from django.core.mail import send_mail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
import random


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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Allows an authenticated user to change their password.
    Requires: old_password, new_password, confirm_password
    """
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')

    # Check all required fields
    if not old_password or not new_password or not confirm_password:
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate old password
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure new passwords match
    if new_password != confirm_password:
        return Response({"error": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)

    # Prevent same password reuse
    if old_password == new_password:
        return Response({"error": "New password cannot be same as old password."}, status=status.HTTP_400_BAD_REQUEST)

    # Set and save new password
    user.set_password(new_password)
    user.save()

    return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)



def send_otp_email(recipient_email, otp):
    # otp = generate_otp()

    sender_email = 'Support@pixmintai.com'  # Hostinger email
    password = 'PHtE6r1eFujrjmV99kUB4qLtRc+jYY8tq+syLQQSuYwRCvVQF01So4x6mz+1/kgsVaEUQv+Zzog847qftLqDd23qN24aWWqyqK3sx/VYSPOZsbq6x00ct1sZfkLZVI7tcNJu3SbfvJI='
    smtp_server = 'smtp.zeptomail.in'
    smtp_port = 465  # SSL

    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}. It is valid for 10 minutes."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(e)
        print(f"Failed to send email: {e}")
        raise e
    finally:
        if server:
            server.quit()
    print("OTP SEND")
    return otp


def generate_otp():
    return str(random.randint(100000, 999999))

OTP_EXPIRY_MINUTES = 10

@api_view(['POST'])
def email_verify(request):
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    otp = generate_otp()

    # Save OTP + student data in cache
    cache.set(f"user_email_{email}", {
        "otp": otp
    }, timeout=OTP_EXPIRY_MINUTES * 60)

    send_otp_email(email, otp)

    return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def verify_otp(request):
    email = request.data.get("email")
    input_otp = request.data.get("otp")

    if not email or not input_otp:
        return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

    cached = cache.get(f"user_email_{email}")

    if not cached:
        return Response({"error": "OTP expired or not requested."}, status=status.HTTP_400_BAD_REQUEST)

    if cached["otp"] != input_otp:
        return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)


    try:
        

        # Clear the OTP cache after success
        cache.delete(f"student_otp_{email}")

        return Response({"message": "Otp Verifyied"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Database error: {e}")
        return Response({"error": "Failed to register student."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
