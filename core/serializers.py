from rest_framework import serializers
from .models import User, Room, TimeSlot, Talk, Favorite
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token['role'] = user.role  # rôle dans le token (pas obligatoire ici si tu ne l’utilises pas côté front)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role  # renvoyer le rôle côté frontend
        return data
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES, default='user')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password2', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data['role']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']
        read_only_fields = ['id']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start', 'end']
        read_only_fields = ['id']


class TalkSerializer(serializers.ModelSerializer):
    speaker = UserSerializer(read_only=True)  # Nested serializer for speaker
    room = RoomSerializer(read_only=True)
    timeslot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = Talk
        fields = [
            'id', 'title', 'description', 'duration', 'level', 'status',
            'speaker', 'room', 'timeslot', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested serializer for user
    talk = TalkSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'talk', 'created_at']
        read_only_fields = ['id', 'created_at']