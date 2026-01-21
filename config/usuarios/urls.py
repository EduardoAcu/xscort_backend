from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    UploadVerificationDocumentsView,
    RequestModelVerificationView,
    VerificationStatusView,
    TokenRefreshCookieView,
    LatestTermsView,
    LatestPrivacyView,
    UserMeView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('token/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshCookieView.as_view(), name='token-refresh'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    # Recovery
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    # Aliases usadas por el frontend
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password-alias'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password-alias'),
    path('request-model-verification/', RequestModelVerificationView.as_view(), name='request-model-verification'),
    path('verification/upload-documents/', UploadVerificationDocumentsView.as_view(), name='upload-verification-documents'),
    path('verification/status/', VerificationStatusView.as_view(), name='verification-status'),
    path('me/', UserMeView.as_view(), name='user-me'),
    path('legal/terms/latest/', LatestTermsView.as_view(), name='latest-terms'),
    path('legal/privacy/latest/', LatestPrivacyView.as_view(), name='latest-privacy'),
]
