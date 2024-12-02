from django.db import models
from authentication.models import Profile ,RoleChoices,BaseClass


class PDFDocument(BaseClass):
    teacher=models.ForeignKey(Profile,on_delete=models.CASCADE,null=True,blank=True)
    uploaded_pdf = models.FileField(upload_to='pdfs/')
    extracted_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"PDF Document uploaded on {self.created_at}"
