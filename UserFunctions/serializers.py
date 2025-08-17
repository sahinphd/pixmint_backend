from rest_framework import serializers
from .models import User
from datetime import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from slab.models import Slab
from slab.models import UserSlab

class SlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slab
        fields = ['id', 'slab_name', 'slab_percentage', 'max_amount', 'activate_status']
        def get_slabs(self, obj):
            user_slabs = UserSlab.objects.filter(user=obj)
            return SlabSerializer([us.slab for us in user_slabs], many=True).data
    
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
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to response
        data['id'] = self.user.id
        data['userid'] = self.user.userid
        data['name'] = self.user.name
        data['usercode'] = self.user.usercode
        data['refarcode'] = self.user.refarcode
        data['email'] = self.user.email
        
        # Fetch slab_name from UserSlab model
        user_slab = UserSlab.objects.filter(user=self.user).first()
        data['slab_name'] = user_slab.slab.slab_name if user_slab else None

        return data