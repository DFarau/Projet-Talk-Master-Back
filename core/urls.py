from django.urls import path
from .views import (
    UserListCreateView,
    RoomListCreateView,
    TimeSlotListCreateView,
    TalkListCreateView,
    FavoriteListCreateView,
    CookieTokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('rooms/', RoomListCreateView.as_view(), name='room-list-create'),
    path('timeslots/', TimeSlotListCreateView.as_view(), name='timeslot-list-create'),
    path('talks/', TalkListCreateView.as_view(), name='talk-list-create'),
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path("login/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
]