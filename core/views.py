from rest_framework import generics
from rest_framework.views import APIView
from .models import User, Room, Talk
from .serializers import UserSerializer, RoomSerializer, TalkSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
import logging
logger = logging.getLogger(__name__)
import datetime


class HelloWorldView(APIView):
    def get(self, request):
        return Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)

class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data["access"]
            refresh = response.data["refresh"]
            role = response.data["role"]

            logger.error(response.data)
            res = Response({"message": "Login successful", "role" : role}, status=200)
            res.set_cookie("access_token", access, httponly=True, secure=True, samesite="Lax", max_age=1800)
            res.set_cookie("refresh_token", refresh, httponly=True, secure=True, samesite="Lax", max_age=7*24*60*60)
            return res

        return response
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token not found'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Révoquer le token de rafraîchissement
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Supprimer les cookies
            response = Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')

            return response
        except Exception:
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({'access': access_token}, status=status.HTTP_200_OK)

            # Set new access_token in HTTP-only cookie
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='Lax',
                max_age=30 * 60  # 30 minutes
            )

            return response

        except TokenError as e:
            return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# Vue pour lister et créer des utilisateurs
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# VUES CRUD POUR LES SALLES (ROOMS)

# Vue pour lister et créer des salles
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

# Vue pour récupérer, mettre à jour ou supprimer une salle spécifique
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    def get_object(self):
        return get_object_or_404(Room, id=self.kwargs['pk'])





# VUES CRUD POUR LES TALKS

# Vue pour lister et créer des talks
class TalkListCreateView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'speakerName', 'level']
    ordering_fields = ['start', 'end', 'created_at', 'level', 'status']
    
    def get_queryset(self):
        queryset = Talk.objects.all()
        
        # Filtres par paramètres de requête
        room_id = self.request.query_params.get('room')
        speaker_id = self.request.query_params.get('speaker')
        organizer_id = self.request.query_params.get('organizer')
        status = self.request.query_params.get('status')
        level = self.request.query_params.get('level')
        start_date = self.request.query_params.get('start_date')
        
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if speaker_id:
            queryset = queryset.filter(speaker_id=speaker_id)
        if organizer_id:
            queryset = queryset.filter(organizer_id=organizer_id)
        if status:
            queryset = queryset.filter(status=status)
        if level:
            queryset = queryset.filter(level=level)
        if start_date:
            queryset = queryset.filter(startdate=start_date)
            
        return queryset
    
    def perform_create(self, serializer):
        speaker_id = self.request.data.get('speaker')
        room_id = self.request.data.get('room')
        
        speaker = None
        if speaker_id:
            speaker = get_object_or_404(User, id=speaker_id, role='speaker')
        
        room = None
        if room_id:
            room = get_object_or_404(Room, id=room_id)
        
        # Si l'utilisateur authentifié a le rôle d'organisateur, il devient l'organisateur du talk
        if self.request.user.is_authenticated and self.request.user.role == 'organizer':
            serializer.save(speaker=speaker, room=room, organizer=self.request.user)
        else:
            serializer.save(speaker=speaker, room=room)

# Vue pour récupérer, mettre à jour ou supprimer un talk spécifique
class TalkDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer
    
    def get_object(self):
        return get_object_or_404(Talk, id=self.kwargs['pk'])
    
    def perform_update(self, serializer):
        speaker_id = self.request.data.get('speaker')
        room_id = self.request.data.get('room')
        
        speaker = None
        if speaker_id:
            speaker = get_object_or_404(User, id=speaker_id, role='speaker')
        
        room = None
        if room_id:
            room = get_object_or_404(Room, id=room_id)
        
        serializer.save(speaker=speaker, room=room)

# Vue pour récupérer les talks par conférencier
class TalksBySpeakerView(generics.ListAPIView):
    serializer_class = TalkSerializer
    
    def get_queryset(self):
        speaker_id = self.kwargs['speaker_id']
        return Talk.objects.filter(speaker_id=speaker_id)

# Vue pour récupérer les talks par organisateur
class TalksByOrganizerView(generics.ListAPIView):
    serializer_class = TalkSerializer
    
    def get_queryset(self):
        organizer_id = self.kwargs['organizer_id']
        return Talk.objects.filter(organizer_id=organizer_id)

# Vue pour récupérer les talks par jour
class TalksByDateView(generics.ListAPIView):
    serializer_class = TalkSerializer
    
    def get_queryset(self):
        date_str = self.kwargs['date']
        return Talk.objects.filter(startdate=date_str)

# Vue pour récupérer les talks par salle
class TalksByRoomView(generics.ListAPIView):
    serializer_class = TalkSerializer
    
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return Talk.objects.filter(room_id=room_id)


class TalkListView(generics.ListAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        room_id = self.request.query_params.get('room_id')

        if room_id:
            queryset = queryset.filter(room__id=room_id)
       

        return queryset


