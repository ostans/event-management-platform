from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer

User = get_user_model()


class RegisterApiView(generics.CreateAPIView):

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = CustomTokenObtainPairSerializer.get_token(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "phone_number": user.phone_number,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_staff": user.is_staff,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class CustomLoginApiView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


class LogoutApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
        except TokenError:
            return Response({"detail": "Invalid token."}, status=400)

        if request.user.id != token["user_id"]:
            return Response({"detail": "You can only logout your own session."}, status=403)

        try:
            token.blacklist()
        except AttributeError:
            return Response(
                {"detail": "Blacklisting tokens is not enabled. Please enable it in settings.py"}, status=500
            )
        return Response({"detail": "Successfully logged out."}, status=200)
