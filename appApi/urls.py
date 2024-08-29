from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('user/token/', views.MyTokenObtainPairView.as_view(), name="user_token"),
    path('user/token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('user/register/', views.RegisterView.as_view(), name="user_register"),
    path('user/password_reset_email/<email>/', views.PasswordResetView.as_view()),
    path('user/password_change/', views.PasswordChangeView.as_view(), name='password_change'),
   

    # =====appApi course urls starts from here=======#
    path('course/category/', views.CategoryView.as_view()),
    path('course/course_list/', views.CourseView.as_view()),
    path('course/course_details/<slug>/', views.CourseDetailsView.as_view()),


    # =====appApi cart urls starts from here=======#
    path('course/cart/<cart_id>/', views.CartView.as_view()),
    path('course/create_cart/', views.CartCreateView.as_view()),
    path('course/delete_cart/<cart_id>/<item_id>/', views.CartItemDeleteView.as_view()),
    path('course/static_cart/<cart_id>/', views.CartStaticView.as_view()),
    path('course/order/create_order/', views.OrderCreateView.as_view()),
    path('course/order/checkout_order/<order_id>/', views.CheckoutView.as_view()),
    path('course/order/coupon/', views.CouponApplyView.as_view()),
    path('payment/stripe_checkout/<order_id>/', views.StripeCheckoutView.as_view()),
    path('payment/success/', views.PaymentSuccessView.as_view()),
    path('course/search/', views.SearchCourseView.as_view()),
    path('course/review/', views.ReviewView.as_view()),
    

]

