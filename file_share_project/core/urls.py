from django.urls import path
from .views import RegisterClient, RegisterOPSUser, VerifyEmail, FileUploadView, DownloadFile, ListFiles

urlpatterns = [
    path('register/', RegisterClient.as_view(), name='register_client'),  # for CLIENT users only
    path('register-ops/', RegisterOPSUser.as_view(), name='register_ops'),  # for OPS users only
    path('verify-email/<str:signed_id>/', VerifyEmail.as_view(), name='verify_email'),
    path('upload/', FileUploadView.as_view(), name='upload_file'),
    path('download/<str:signed_id>/', DownloadFile.as_view(), name='download_file'),
    path('files/', ListFiles.as_view(), name='list_files'),
]
