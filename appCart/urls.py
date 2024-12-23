
from django.urls import path
from . import views
from . import views

urlpatterns = [

 # =====appApi cart urls starts from here=======#
    path("course/cart/<cart_id>/", views.CartView.as_view()),
    path("course/create_cart/", views.CartCreateView.as_view()),
    path("course/delete_cart/<cart_id>/<item_id>/", views.CartItemDeleteView.as_view()),
    path("course/static_cart/<cart_id>/", views.CartStaticView.as_view()),
    path("course/order/create_order/", views.OrderCreateView.as_view()),
    path("course/order/checkout_order/<order_id>/", views.CheckoutView.as_view()),
    path("course/order/coupon/", views.CouponApplyView.as_view()),
    path("payment/stripe_checkout/<order_id>/", views.StripeCheckoutView.as_view()),
    path("payment/success/", views.PaymentSuccessView.as_view()),

]
