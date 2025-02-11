from django.db import models
from authentication.models import Profile,BaseClass
from authentication.models import Student




class Certificate(BaseClass):
    student=models.ForeignKey(Student,on_delete=models.CASCADE,null=True,blank=True)
    certificate_pdf = models.FileField(upload_to='certificates/')
    grades = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)




class ActivityCertificate(BaseClass):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activity_certificates')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    certificate_file = models.FileField(upload_to='activity_certificates/')
    activity_type = models.CharField(max_length=50, choices=[
        ('Sports', 'Sports'),
        ('Cultural', 'Cultural'),
        ('Academic', 'Academic'),
        ('Other', 'Other')
    ],null=True,blank=True)
    issue_date = models.DateField(null=True,blank=True)
    issuing_organization = models.CharField(max_length=200,null=True,blank=True)
    achievement_level = models.CharField(max_length=50, choices=[
        ('Participation', 'Participation'),
        ('Winner', 'Winner'),
        ('Runner Up', 'Runner Up'),
        ('Merit', 'Merit')
    ],null=True,blank=True)
    mark=models.FloatField(null=True,blank=True)
    pdf_text=models.TextField(null=True,blank=True)
    is_approved=models.BooleanField(default=False)


    def __str__(self):
        return f"{self.student.profile.email} - {self.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Activity Certificate'
        verbose_name_plural = 'Activity Certificates'
