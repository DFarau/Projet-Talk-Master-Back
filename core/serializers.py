from rest_framework import serializers
from .models import User, Room, TimeSlot, Talk, Favorite


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