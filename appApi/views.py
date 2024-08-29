# ======import from Django buildin
from django.shortcuts import render, redirect
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import random
import stripe
import stripe.error
import requests

# =======import from custom app=============#
from appAuth.models import User, Profile
from . import models
from . import serializers
from backend import settings


# ======Stripe and paypal=======
stripe.api_key = settings.STRIPE_SECRET_KEY
PAYPAL_CLIENT_ID = settings.PAYPAL_CLIENT_ID
PAYPAL_SECRET_KEY = settings.PAYPAL_SECRET_KEY


# ======Views start from here======#


# =========Views for appUserAuth===========#
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = serializers.RegisterSerializer


def generate_randon_otp(length=8):
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
            user.otp = generate_randon_otp()
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


# ====Views for appApi


# ====Coure View
class CategoryView(generics.ListAPIView):
    queryset = models.Category.objects.filter(active=True)
    serializer_class = serializers.CategorySerializer
    permission_classes = [AllowAny]


class CourseView(generics.ListAPIView):
    queryset = models.Course.objects.filter(
        platform_status="PUBLISHED", teacher_course_status="PUBLISHED"
    )
    serializer_class = serializers.CourseSerializer
    permission_classes = [AllowAny]


class CourseDetailsView(generics.RetrieveAPIView):
    queryset = models.Course.objects.filter(
        platform_status="PUBLISHED", teacher_course_status="PUBLISHED"
    )
    serializer_class = serializers.CourseSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs["slug"]
        course = models.Course.objects.get(
            slug=slug, platform_status="PUBLISHED", teacher_course_status="PUBLISHED"
        )
        return course


# ==========Cart View==============#
class CartCreateView(generics.CreateAPIView):
    queryset = models.Cart.objects.all()
    serializer_class = serializers.CartSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        course_id = request.data["course_id"]
        user_id = request.data["user_id"]
        price = request.data["price"]
        country = request.data["country"]
        cart_id = request.data["cart_id"]

        course = models.Course.objects.filter(id=course_id).first()

        if user_id != "undefined":
            user = User.objects.filter(id=user_id).first()
        else:
            user = None

        try:
            country_name = models.Country.objects.filter(name=country).first()
            country = country_name.name
        except:
            country_name = None
            country = "Bangladesh"

        if country_name:
            tax_rate = float(country_name.tax_rate / 100)

        else:
            tax_rate = 0

        cart = models.Cart.objects.filter(cart_id=cart_id, course=course).first()

        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart.cart_id = cart_id
            cart.total = Decimal(price) + Decimal(cart.tax)
            cart.save()
            return Response(
                {"message": "Cart Updated Successfully"}, status=status.HTTP_200_OK
            )
        else:
            cart = models.Cart()
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax)
            cart.save()
            return Response(
                {"message": "Cart Created Successfully"}, status=status.HTTP_201_CREATED
            )


class CartView(generics.ListAPIView):
    serializer_class = serializers.CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        cart_id = self.kwargs["cart_id"]
        queryset = models.Cart.objects.filter(cart_id=cart_id)
        return queryset


class CartItemDeleteView(generics.DestroyAPIView):
    serializer_class = serializers.CartSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        cart_id = self.kwargs["cart_id"]
        item_id = self.kwargs["item_id"]
        cart_item = models.Cart.objects.filter(cart_id=cart_id, id=item_id).first()
        return cart_item


class CartStaticView(generics.RetrieveAPIView):
    serializer_class = serializers.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = "cart_id"

    def get_queryset(self):
        cart_id = self.kwargs["cart_id"]
        queryset = models.Cart.objects.filter(cart_id=cart_id)
        return queryset

    def get(self, request, *args, **kwargs):
        cart_items = self.get_queryset()

        total_price = 0.00
        total_tax = 0.00
        sub_total = 0.00

        for cart_item in cart_items:
            total_price += float(self.calculate_price(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            sub_total += round(float(self.calculate_total(cart_item)), 2)

        data = {"price": total_price, "tax": total_tax, "total": sub_total}
        print("data", data)
        return Response(data)

    def calculate_price(self, cart_item):
        return cart_item.price

    def calculate_tax(self, cart_item):
        return cart_item.tax

    def calculate_total(self, cart_item):
        return cart_item.total


class OrderCreateView(generics.CreateAPIView):
    serializer_class = serializers.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = models.CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        full_name = request.data["full_name"]
        email = request.data["email"]
        country = request.data["country"]
        cart_id = request.data["cart_id"]
        user_id = request.data["user_id"]

        if user_id != 0:
            user =User.objects.get(id=user_id)
        else:
            user = None

        cart_items = models.Cart.objects.filter(cart_id=cart_id)

        total_price = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        sub_total = Decimal(0.00)

        order = models.CartOrder.objects.create(
            full_name=full_name, email=email, country=country, student=user
        )

        for cart_item in cart_items:
            models.CartOrderItem.objects.create(
                order=order,
                course=cart_item.course,
                price=cart_item.price,
                tax=cart_item.tax,
                total=cart_item.total,
                initial_total=cart_item.total,
                teacher=cart_item.course.teacher,
            )
            total_price += Decimal(cart_item.price)
            total_tax += Decimal(cart_item.tax)
            total_initial_total += Decimal(cart_item.total)
            sub_total += Decimal(cart_item.total)

            order.teacher.add(cart_item.course.teacher)

        order.sub_total = total_price
        order.tax = total_tax
        order.initial_total = total_initial_total
        order.total = sub_total
        order.save()

        return Response(
            {"messages": "Order created successfully", "order_id": order.order_id},
            status=status.HTTP_201_CREATED,
        )


class CheckoutView(generics.RetrieveAPIView):
    serializer_class = serializers.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = models.CartOrder.objects.all()
    lookup_field = "order_id"


class CouponApplyView(generics.CreateAPIView):
    serializer_class = serializers.CouponSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        order_id = request.data["order_id"]
        code = request.data["code"]

        order = models.CartOrder.objects.get(order_id=order_id)
        print(order)
        coupon = models.Coupon.objects.get(code=code)
        print(coupon)

        if coupon:
            order_items = models.CartOrderItem.objects.filter(
                order=order
            )  # There should be a change, see the main source code

            print(order_items)
            for order_item in order_items:
                if not coupon in order_item.coupons.all():
                    print(order_item.total)
                    print(coupon.discount / 100)
                    discount = order_item.total * coupon.discount / 100

                    print(discount)

                    order_item.total -= discount
                    order_item.price -= discount
                    order_item.saved += discount

                    order_item.applied_coupon = True
                    order_item.coupons.add(coupon)

                    order.coupons.add(coupon)
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount

                    order_item.save()
                    order.save()

                    coupon.used_by.add(order.student)

                    return Response(
                        {"message": "Coupon found and activated", "icon": "success"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": "Coupon already applied", "icon": "warning"},
                        status=status.HTTP_200_OK,
                    )
        else:
            return Response(
                {"messages": "Coupon not found", "icon": "error"},
                status=status.HTTP_404_NOT_FOUND,
            )


class StripeCheckoutView(generics.CreateAPIView):
    serializer_class = serializers.CartOrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        order_id = self.kwargs["order_id"]
        order = models.CartOrder.objects.get(order_id=order_id)

        if not order:
            return Response(
                {"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": order.full_name,
                            },
                            "unit_amount": int(order.total * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                # success_url=settings.FRONTEND_SITE_URL
                success_url=settings.BACKEND_SITE_URL
                + "payment-success/"
                + order.order_id
                + "?session_id={CHECKOUT_SESSION_ID}",
                # cancel_url=settings.FRONTEND_SITE_URL + "payment-failed/",
                cancel_url=settings.BACKEND_SITE_URL + "payment-failed/",
            )

            print(checkout_session)

            order.stripe_session_id = checkout_session.id
            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response(
                {
                    "message": f"Something went wrong when trying to make payment. Error: {str(e)}"
                }
            )


def get_access_token(client_id, secret_key):
    token_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {"grant_type": "client_credentials"}
    auth = (client_id, secret_key)
    response = requests.post(token_url, data=data, auth=auth)

    if response.status_code == 200:
        # print("Access Token====", response.json()["access_token"])
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get access toke from paypal {response.status_code}")


class PaymentSuccessView(generics.CreateAPIView):
    serializer_class = serializers.CartOrderSerializer
    queryset = models.CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        order_id = request.data["order_id"]
        session_id = request.data["session_id"]
        paypal_order_id = request.data["paypal_order_id"]

        order = models.CartOrder.objects.get(order_id=order_id)
        order_items = models.CartOrderItem.objects.filter(order=order)

        if paypal_order_id != "null":
            payment_api_url = (
                f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}"
            )
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {get_access_token(PAYPAL_CLIENT_ID, PAYPAL_SECRET_KEY)}",
            }

            response = request.get(payment_api_url, headers=headers)

            if response.status_code == 200:
                paypal_order_data = request.json()
                paypal_payment_status = paypal_order_data["status"]
                if paypal_payment_status == "COMPLETED":
                    if order.payment_status == "Processing":
                        order.payment_status = "Paid"
                        order.save()

                        models.Notification.objects.create(
                            user=order.student,
                            order=order,
                            type="Course Enrollment completed",
                        )

                        for i in order_items:
                            models.Notification.objects.create(
                                teacher=i.teacher,
                                order=order,
                                order_item=i,
                                type="New Order",
                            )

                            models.EnrolledCourse.objects.create(
                                course=i.course,
                                user=order.student,
                                teacher=i.teacher,
                                order_item=i,
                            )
                        return Response({"message": "Payment Successfull"})
                    else:
                        return Response({"message": "Already Paid"})
                else:
                    return Response({"message": "Payment Failed"})
            else:
                return Response({"message": "Paypal error occured!"})

        if session_id != "null":
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                if order.payment_status == "PROCESSING":
                    order.payment_status = "PAID"

                    order.save()

                    models.Notification.objects.create(
                        user=order.student,
                        order=order,
                        type="Course Enrollment completed",
                    )
                    for i in order_items:
                        models.Notification.objects.create(
                            teacher=i.course.teacher,
                            order=order,
                            order_item=i,
                            type="New Order",
                        )

                        models.EnrolledCourse.objects.create(
                            course=i.course,
                            user=order.student,
                            teacher=i.teacher,
                            order_item=i,
                        )
                    return Response({"message":"Payment Successfull"})
                else:
                    return Response({"message":"Already Paid"})
            else:
                return Response({"message":"Payment Failed"})



class SearchCourseView(generics.ListAPIView):
    serializer_class = serializers.CourseSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        query = self.request.GET.get("query")
        return models.Course.objects.filter(
            title__icontains=query,
            platform_status="Published",
            teacher_course_status="Published",
        )


class ReviewView(generics.ListAPIView):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = [AllowAny]
