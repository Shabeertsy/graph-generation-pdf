from django.urls import path
from . import views


urlpatterns = [
    path('image-upload/', views.CertificateUploadView.as_view(), name='certificate-upload'),
]