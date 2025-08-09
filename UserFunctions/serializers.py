from rest_framework import serializers
from .models import User
from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'userid', 'name', 'email', 'password','usercode', 'refarcode', 'is_active']
        extra_kwargs = {'password': {'write_only': True}, 'usercode': {'read_only': True}}

    def create(self, validated_data):
        userid = validated_data['userid']
        name = validated_data['name']
        email = validated_data['email']
        password = validated_data['password']
        refarcode = validated_data.get('refarcode')

        user = User.objects.create_user(
            userid=userid,
            name=name,
            email=email,
            password=password,
            refarcode=refarcode
        )


        today_str = datetime.now().strftime('%m%d%y')
        user.usercode = f"{today_str}{user.id}"
        user.save(update_fields=["usercode"])

        return user
    
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'userid', 'name', 'email', 'usercode', 'refarcode', 'is_active']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['userid'] = user.userid
        token['name'] = user.name
        token['usercode'] = user.usercode
        token['refarcode'] = user.refarcode
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to response
        data['id'] = self.user.id
        data['userid'] = self.user.userid
        data['name'] = self.user.name
        data['usercode'] = self.user.usercode
        data['refarcode'] = self.user.refarcode

        return data