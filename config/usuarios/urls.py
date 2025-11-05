from django.urls import path
from .views import UserRegistrationView, UserLoginView, UploadVerificationDocumentsView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('token/', UserLoginView.as_view(), name='user-login'),
    path('verification/upload-documents/', UploadVerificationDocumentsView.as_view(), name='upload-verification-documents'),
]
