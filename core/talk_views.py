from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .models import User, Room, Talk
from .serializers import UserSerializer, RoomSerializer, TalkSerializer
from .permissions import IsOrganizer, IsSpeaker, IsOrganizerOrReadOnly, IsSpeakerOrReadOnly

# VUES CRUD POUR LES SALLES (ROOMS)

# Vue pour lister et créer des salles
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    permission_classes = [IsOrganizerOrReadOnly]

# Vue pour récupérer, mettre à jour ou supprimer une salle spécifique
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsOrganizerOrReadOnly]
    
    def get_object(self):
        return get_object_or_404(Room, id=self.kwargs['pk'])

# VUES CRUD POUR LES TALKS

# Vue pour lister et créer des talks
class TalkListCreateView(generics.ListCreateAPIView):
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer
    permission_classes = [IsOrganizerOrReadOnly]
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
    permission_classes = [IsSpeakerOrReadOnly]
    
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
