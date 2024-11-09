from django.urls import path
from . import views

urlpatterns = [
    path('user-detail/<int:pk>/', views.UserDetailView.as_view(), name="user_detail"),
    path('user-update/<int:pk>/', views.UserUpdateView.as_view(), name="user_update"),
    path("subscribe-register/", views.SubscribeRegisterView.as_view(), name="subscribe_register"),
    path("subscribe-cancel/", views.SubscribeCancelView.as_view(), name="subscribe_cancel"),
    path("subscribe-payment/", views.SubscribePaymentView.as_view(), name="subscribe_payment"),
]