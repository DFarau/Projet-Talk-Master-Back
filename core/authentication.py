from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Récupérer le token JWT depuis les cookies
        raw_token = request.COOKIES.get('access_token')
        if not raw_token:
            return None  # Aucun token trouvé dans les cookies

        # Valider le token JWT
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        if not user.is_active:
            raise AuthenticationFailed('User is inactive or deleted.')

        return (user, validated_token)