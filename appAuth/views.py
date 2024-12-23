from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from django.contrib.auth.hashers import check_password

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import random
from . import serializers
from .models import User, OneTimePassword
from .utils import send_code_to_activate_user_account


from backend import settings


# class MyTokenObtainPairView(TokenObtainPairView):
#     serializer_class = serializers.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = serializers.RegisterSerializer

    def post(self, request):
        print(request.data)
        user = request.data

        serializer = serializers.RegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data = serializer.data

            send_code_to_activate_user_account(user_data["email"])
            return Response(
                {
                    "data": user_data,
                    "message": "A passcode has been sent to your email",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserView(APIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.OTPCodeSerializer

    def post(self, request):
        serializer = serializers.OTPCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_code = serializer.validated_data.get("otp")

        try:
            user_code = OneTimePassword.objects.get(code=otp_code)
            user = user_code.user
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response(
                    {"message": "Email verified successfully."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Code is not valid"}, status=status.HTTP_204_NO_CONTENT
            )
        except OneTimePassword.DoesNotExist:
            return Response(
                {"message": "Passcode not provided.."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LoginView(APIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    serializer_class = serializers.LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.data
        return Response(status=status.HTTP_200_OK)


def generate_random_otp(length=8):
    otp = "".join([str(random.randint(0, 9)) for _ in range(length)])
    return otp


class PasswordResetView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        email = self.kwargs["email"]
        user = User.objects.filter(email=email).first()

        if user is not None:
            print(user)
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)
            user.refresh_token = refresh_token
            user.otp = generate_random_otp()
            user.save()
            

      
            # link = f"http://localhost:5173/new_password/?otp={user.otp}&uuidb64={uuidb64}&=refresh_token{refresh_token}"
            link = f"https://academy-platfrom-u6f9.onrender.com/new_password/?otp={user.otp}&uuidb64={uuidb64}&=refresh_token{refresh_token}"

            print(link)

            context = {"link": link, "username": user.username}

            subject = "Password reset email"
            text_body = render_to_string("password_reset.txt", context)
            html_body = render_to_string("password_reset.html", context)

            message = EmailMultiAlternatives(
                subject=subject,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
                body=text_body,
            )

            message.attach_alternative(html_body, "text/html")
            message.send()
        return user


class PasswordChangeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        otp = request.data["otp"]
        uuidb64 = request.data["uuidb64"]
        password = request.data["password"]

        user = User.objects.get(id=uuidb64, otp=otp)

        if user:
            user.set_password(password)
            user.save()

            return Response(
                {"message": "Password Changed Successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "User doesn't exist"}, status=status.HTTP_404_NOT_FOUND
            )


class ChangePassword(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user_id = request.data["user_id"]
        old_password = request.data["old_password"]
        new_password = request.data["new_password"]

        user = User.objects.get(id=user_id)

        if user is not None:
            if check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "Password changed successfully.", "item": "success"}
                )
            else:
                return Response(
                    {"message": "Old password is incorrect.", "item": "warning"}
                )
        else:
            return Response({"message": "User doesn't exist.", "item": "error"})
