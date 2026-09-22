from datetime import timedelta

from django.contrib.auth import login, logout
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.permissions import IsOwner

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer


class RegisterApiView(generics.CreateAPIView):

    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        login(self.request, user)
        return user


class CustomLoginApiView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


class LogoutApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token_user_id = token["user_id"]

            if request.user.id != token_user_id:
                return Response({"detail": "You can only logout your own session."}, status=403)

            token.blacklist()
            logout(request)
            return Response({"detail": "Successfully logged out."}, status=200)
        except Exception:
            return Response({"detail": "Invalid token."}, status=400)
