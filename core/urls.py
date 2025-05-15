from django.urls import path
from .views import (
    UserListCreateView,
    CookieTokenObtainPairView,
    TokenRefreshView,
    RegisterView,
    HelloWorldView,
    LogoutView

)
from .talk_views import (
    RoomListCreateView,
    RoomDetailView,
    TalkListCreateView,
    TalkDetailView,
    TalksBySpeakerView,
    TalksByOrganizerView,
    TalksByDateView,
    TalksByRoomView,
)

urlpatterns = [
    # Vues d'authentification
    path("login/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name='token_logout'),
    
    # Vues utilisateurs
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    
    # Vues salles
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', RoomDetailView.as_view(), name='room-detail'),
    
    # Vues talks
    path('talks/', TalkListCreateView.as_view(), name='talk-list-create'),
    path('talks/<uuid:pk>/', TalkDetailView.as_view(), name='talk-detail'),
    path('talks/speaker/<uuid:speaker_id>/', TalksBySpeakerView.as_view(), name='talks-by-speaker'),
    path('talks/organizer/<uuid:organizer_id>/', TalksByOrganizerView.as_view(), name='talks-by-organizer'),
    path('talks/date/<str:date>/', TalksByDateView.as_view(), name='talks-by-date'),
    path('talks/room/<int:room_id>/', TalksByRoomView.as_view(), name='talks-by-room'),
    
    # Autres vues
    path('hello/', HelloWorldView.as_view(), name='hello-world'),
]