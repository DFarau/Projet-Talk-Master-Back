from rest_framework import serializers
from .models import User, Room, Talk
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User._meta.get_field('role').choices, default='user')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
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

class TalkSerializer(serializers.ModelSerializer):
    speaker_details = UserSerializer(source='speaker', read_only=True)
    room_details = RoomSerializer(source='room', read_only=True)
    organizer_details = UserSerializer(source='organizer', read_only=True)

    class Meta:
        model = Talk
        fields = [
            'id', 'title', 'description', 'start', 'end', 'startdate',
            'level', 'status', 'speaker', 'speaker_details', 'speakerName',
            'organizer', 'organizer_details', 'room', 'room_details', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'speakerName', 'speaker_details', 'room_details', 'organizer_details']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Pour les requêtes GET, nous voulons les détails complets
        representation.pop('speaker', None)  # Supprime l'ID simple pour éviter la duplication
        representation.pop('room', None)     # Supprime l'ID simple pour éviter la duplication
        representation.pop('organizer', None)  # Supprime l'ID simple pour éviter la duplication
        
        # Renomme les champs détaillés pour simplifier le JSON
        if 'speaker_details' in representation:
            representation['speaker'] = representation.pop('speaker_details')
        if 'room_details' in representation:
            representation['room'] = representation.pop('room_details')
        if 'organizer_details' in representation:
            representation['organizer'] = representation.pop('organizer_details')
        
        return representation



