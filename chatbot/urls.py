from django.urls import path
from . import views

urlpatterns = [
    path('upload-pdf/', views.PDFUploadView.as_view(), name='upload_pdf'),
    path('ask-question/', views.ChatbotAPIView.as_view(), name='ask_question'),
    path('ask-query/', views.ChatbotTeachersAPIView.as_view(), name='ask_query'),
]
