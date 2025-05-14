from rest_framework import generics
from rest_framework.views import APIView
from .models import User, Room, TimeSlot, Talk, Favorite
from .serializers import UserSerializer, RoomSerializer, TimeSlotSerializer, TalkSerializer, FavoriteSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import datetime


class CookieTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data["access"]
            refresh = response.data["refresh"]
            role = response.data["role"]

            res = Response({"message": "Login successful", "role": role}, status=200)
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

        except Exception as e:
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