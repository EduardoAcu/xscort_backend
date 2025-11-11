from django.urls import path
from .views import UserRegistrationView, UserLoginView, UploadVerificationDocumentsView, RequestModelVerificationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('token/', UserLoginView.as_view(), name='user-login'),
    path('request-model-verification/', RequestModelVerificationView.as_view(), name='request-model-verification'),
    path('verification/upload-documents/', UploadVerificationDocumentsView.as_view(), name='upload-verification-documents'),
]
