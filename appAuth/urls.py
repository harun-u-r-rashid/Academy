from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    # path("user/token/", views.MyTokenObtainPairView.as_view(), name="user_token"),
    # path("user/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="user_register"),
    path("verify/", views.VerifyUserView.as_view(), name="user_verify"),
    path("login/", views.LoginView.as_view(), name="user_login"),
    path("logout/", views.LogoutView.as_view(), name="user_logout"),
    path("password_reset_email/<str:email>/", views.PasswordResetView.as_view()),
    path(
        "password_change/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    # path("change_password/", views.ChangePassword.as_view()),
]
