from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path("api/auth/register/", views.RegisterApiView.as_view(), name="register"),
    path("api/auth/login/", views.CustomLoginApiView.as_view(), name="login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", views.LogoutApiView.as_view(), name="logout"),
]
