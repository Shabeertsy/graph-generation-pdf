from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.LoginAPIView.as_view(),name='login'),
    path('change-password/',views.ChangePassword.as_view(),name='change-password'),
    path('student-registration/',views.StudentRegistrationAPIView.as_view(),name='student-registration'),
]
