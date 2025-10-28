from django.urls import path
from .views import UserRegistrationView, UserLoginView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('token/', UserLoginView.as_view(), name='user-login'),
]
