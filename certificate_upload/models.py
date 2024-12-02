from django.db import models
from authentication.models import Profile,BaseClass



class Certificate(models.Model):
    student_name = models.CharField(max_length=255)
    certificate_pdf = models.FileField(upload_to='certificates/')
    grades = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Certificate for {self.student_name}"
