from django.urls import path
from . import views


urlpatterns = [
    path('certificate-upload/', views.CertificateUploadView.as_view(), name='certificate-upload'),
    path('certificate-list/', views.CertificateListView.as_view(), name='certificate-list'),
    path('certificate-detail/<uuid:uuid>/', views.CertificateDetailView.as_view(), name='certificate-detail'),
    path('certificate-delete/', views.CertificateDeleteView.as_view(), name='certificate-delete'),  
    path('upload-activity-certificates/', views.UploadActivityCertificates.as_view(), name='upload-activity-certificates'),
    path('listStudents/',views.ListCertificateView.as_view(),name='liststudents'),
    path('certificate-gradecard/',views.GetCertificate_gradecard.as_view(),name='certificate-gradecard'),
    path('add-marks/',views.MarkAdd.as_view(),name='add-marks'),
    path('list-activity-certificates/',views.ActivityCertificatesListView.as_view(),name='list-activity-certificates'),
    path('activity-certificate-detail/',views.ActivityCertificateDetailView.as_view(),name='activity-certificate-detai'),
    path('academic-graph/',views.AcademicGraph.as_view(),name='academic-graph'),
    path('certificate-bulk/',views.CertificateBulkUploadView.as_view(),name='certificate-bulk'),
    path('activity-mark-list/',views.ActivityCertificatesListView.as_view()),

]
