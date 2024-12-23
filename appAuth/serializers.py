from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from . import models
from appAuth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token["full_name"] = user.full_name
#         token["email"] = user.email
#         token["username"] = user.username

#         # token["is_admin"] = user.is_admin
#         token["is_active"] = user.is_admin

#         return token


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "full_name",
            "email",
            "password",
            "confirm_password",
        ]

    def save(self):
        username = self.validated_data["username"]
        full_name = self.validated_data["full_name"]
        email = self.validated_data["email"]

        password = self.validated_data["password"]
        confirm_password = self.validated_data["confirm_password"]

        if password != confirm_password:
            raise serializers.ValidationError({"error": "Password doesn't match"})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "Email already exists"})

        user = User(
            email=email,
            full_name=full_name,
            username=username,
        )
        user.set_password(password)
        user.is_active = False
        user.save()

        return user




class OTPCodeSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=10)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password = serializers.CharField(max_length=68, write_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "full_name", "access_token", "refresh_token"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")
        user = authenticate(request, email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credential.")
        if not user.is_active:
            raise AuthenticationFailed("Email is not active")
        tokens = user.tokens()
        return {
            "email": user.email,
            "full_name": user.full_name,
            "access_token": str(tokens.get("access")),
            "refresh_token": str(tokens.get("refresh")),
        }


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {"bad_token": ("Token is expired or invalid")}

    def validate(self, attrs):
        self.token = attrs.get("refresh_token")

        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail("bad_token")
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = "__all__"
