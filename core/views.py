from rest_framework import generics
from .models import User, Room, TimeSlot, Talk, Favorite
from .serializers import UserSerializer, RoomSerializer, TimeSlotSerializer, TalkSerializer, FavoriteSerializer


# Vue pour lister et créer des utilisateurs
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# Vue pour lister et créer des salles
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


# Vue pour lister et créer des créneaux horaires
class TimeSlotListCreateView(generics.ListCreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


# Vue pour lister et créer des présentations/conférences
class TalkListCreateView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer


# Vue pour lister et créer des favoris
class FavoriteListCreateView(generics.ListCreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer