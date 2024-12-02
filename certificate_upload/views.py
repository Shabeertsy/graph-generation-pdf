# Third-party imports
import fitz 

# Django REST Framework imports
from rest_framework import status
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

# Local imports
from .serializers import CertificateSerializer
from chatbot.utils import gemini_ai 

## models import
from .models import Certificate,ActivityCertificate

## serializers import
from .serializers import ActivityCertificateSerializer



## Function to upload certificate and extract grades from it
class CertificateUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            certificate = serializer.save()
            self.extract_grades_from_pdf(certificate=certificate)
            return Response(CertificateSerializer(certificate).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_grades_from_pdf(self, certificate):
        pdf_file_path = certificate.certificate_pdf.path
        document = fitz.open(pdf_file_path)
        
        text = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text += page.get_text()
            
        data_format = """
            {
            "course_code": "",
            "subject": "",
            "internal_marks": "",
            "external_marks": "",
            "total_marks": "",
            "max_internal": "",
            "max_external": "",
            "max_total": "",
            "percentage": "",
            "credits": "",
            "grade": "",
            "status": ""
        }
        """

        prompt=f"from {text} fetch details in this format {data_format} must be in json format and the data must be accurate "
        grade_data=gemini_ai(prompt)
        if grade_data['flag']:
            certificate.grades = grade_data['data']
            certificate.save()
        else:
            return Response({'message':grade_data['message'],'error':grade_data['error']},status=status.HTTP_400_BAD_REQUEST)


## Function to upload activity certificates
class UploadActivityCertificates(APIView):
    def post(self,request,*args,**kwargs):
        serializer=ActivityCertificateSerializer(data=request.data)
        if serializer.is_valid():
            activity_certificate=serializer.save()
            
            pdf_file_path = activity_certificate.certificate_file.path
            document = fitz.open(pdf_file_path)
            text = ""
            for page_num in range(document.page_count):
                page = document.load_page(page_num)
                text += page.get_text()
                
            activity_certificate.extracted_text = text
            activity_certificate.save()
            
            return Response(ActivityCertificateSerializer(activity_certificate).data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


## Function to list student certificates
class CertificateListView(APIView):
    def get(self,request):  
        student_uuid=request.query_params.get('student_uuid')
        certificates=Certificate.objects.all()
        if student_uuid:
            certificates=certificates.filter(student__uuid=student_uuid)
        serializer=CertificateSerializer(certificates,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'message':'No certificates found'},status=status.HTTP_400_BAD_REQUEST)


## Function to get a single certificate
class CertificateDetailView(APIView):
    def get(self,request,pk):
        certificate=Certificate.objects.get(id=pk)
        serializer=CertificateSerializer(certificate)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'message':'Certificate not found'},status=status.HTTP_400_BAD_REQUEST)


## Function to delete a certificate
class CertificateDeleteView(APIView):
    def delete(self,request):
        certificate_uuid=request.query_params.get('certificate_uuid')
        try:
            certificate=Certificate.objects.get(uuid=certificate_uuid)
            certificate.delete()
            return Response({'message':'Certificate deleted successfully'},status=status.HTTP_200_OK)
        except Certificate.DoesNotExist:
            return Response({'message':'Certificate not found'},status=status.HTTP_400_BAD_REQUEST)



