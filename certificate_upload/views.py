# Third-party imports
import fitz 

# Django REST Framework imports
from rest_framework import status
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView
from authentication.serializers import StudentSerializer
from authentication.models import Student
from django.shortcuts import get_object_or_404
from authentication.permissions import *
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
            "status": "",
            "sgpa":""
        }
        """

        prompt=f"from {text} fetch details in this format {data_format} must be in json format and the data must be accurate no addition comments or text not be there"
        grade_data=gemini_ai(prompt)
        if grade_data['flag']:
            certificate.grades = grade_data['data']
            certificate.save()
        else:
            return Response({'message':grade_data['message'],'error':grade_data['error']},status=status.HTTP_400_BAD_REQUEST)


## Function to upload activity certificates
class UploadActivityCertificates(APIView):
    permission_classes=[IsStudent]
    def post(self,request,*args,**kwargs):
        print("Received Data:", request.data)  # Debugging
        data=request.data.copy()
        student=get_object_or_404(Student,profile__id=request.user.id)
        data['student']=student.id
        serializer=ActivityCertificateSerializer(data=data)
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
        else:
            print(serializer.errors)
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
    def get(self,request,uuid):
        certificate=Certificate.objects.get(uuid=uuid)
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



class ListCertificateView(ListAPIView):
    serializer_class=StudentSerializer

    def get_queryset(self):
        year=self.request.GET.get('year')
        programme=self.request.GET.get('programme')
        department=self.request.GET.get('department')
        queryset=Student.objects.all()
        if year :
            queryset=queryset.filter(year = year)
        if programme:
            queryset=queryset.filter(programme = programme)
        if department:
            queryset=queryset.filter(department = department)
        return queryset
    
     
class GetCertificate_gradecard(APIView):
    serializer_class=CertificateSerializer
    serializer_class2=ActivityCertificateSerializer
    def get(self,request):
        student_id=request.GET.get('student_id')
        certificate=Certificate.objects.filter(student__id=student_id)
        activity_certificate=ActivityCertificate.objects.filter(student__id=student_id)

        certificate_serializer=self.serializer_class(certificate,many=True)
        activity_certificate_serializer=self.serializer_class2(activity_certificate,many=True)
        return Response ({'certificate':certificate_serializer.data,'activity_certificate':activity_certificate_serializer.data})
    
from .models import CertificateMarks
class MarkAdd(APIView):
    def post(self,request):
        certificate_id=request.data.get('certificate_id')
        mark=request.data.get('mark')
        if not mark or not certificate_id:
            return Response({'message':'certificate_id and mark are required'},status=400)
        
        certificate=get_object_or_404(ActivityCertificate,id=certificate_id)
        certificate_mark=CertificateMarks(certifcate=certificate,marks=mark,status=True)
        certificate_mark.save()
        certificate.mark=mark
        certificate.save()
        certificate.student.total_activity_marks+=float(mark)
        certificate.student.save()
        return Response({'message':'marks added successfully'},status=200)


from .serializers import CertificateMarksSerializer
class ActivityMarksAPIView(APIView):
    def get(self,request):
        student_id=request.data.get('student_id')
        mark_list=CertificateMarks.objects.filter(certifcate__student__id=student_id)
        serializer=CertificateMarksSerializer(mark_list,many=True)
        return Response(serializer.data,status=200)
      


## acitvity certificates
class ActivityCertificatesListView(APIView):
    def get(self,request):
        student_id=request.query_params.get('student_id')
        certificate=ActivityCertificate.objects.filter(student__id=student_id)
        serializer=ActivityCertificateSerializer(certificate,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'message':'Certificates not found'},status=status.HTTP_400_BAD_REQUEST)


class ActivityCertificateDetailView(APIView):
    def get(self,request):
        certificate_id=request.query_params.get('certificate_id')
        certificate=ActivityCertificate.objects.get(id=certificate_id)
        serializer=ActivityCertificateSerializer(certificate)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'message':'Certificate not found'},status=status.HTTP_400_BAD_REQUEST)
    

from django.db.models import Sum, Count
class AcademicGraph(APIView):
    def get(self,request):
        student_id=request.query_params.get('student_id')
        certificate=Certificate.objects.filter(student__id=student_id)
        academic_certificate=Certificate.objects.filter(student__id=student_id)
        serializer=CertificateSerializer(certificate,many=True)
        grades=certificate.first().grades if certificate else 'certificate not uploaded'

        activity_data = ActivityCertificate.objects.filter(student__id=student_id).aggregate(
            total_marks=Sum('mark'), 
            certificate_count=Count('id') 
        )

        total_marks = activity_data['total_marks'] or 0
        certificate_count = activity_data['certificate_count']
        return Response({'grades':grades,'total_marks':total_marks,'certificate_count':certificate_count,'academic_certificate':serializer.data},status=status.HTTP_200_OK)
    
            


import fitz  # PyMuPDF
import json
import re
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from .models import Certificate, Student
from .serializers import CertificateSerializer

class CertificateBulkUploadView(APIView):
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

        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text = page.get_text("text") 
            print(f"Processing page {page_num + 1}")

            # Extract Register Number
            register_number = self.extract_register_number(text)
            print(f"Extracted Register Number: {register_number}")

            single_page_pdf = fitz.open()
            single_page_pdf.insert_pdf(document, from_page=page_num, to_page=page_num)

            pdf_bytes = single_page_pdf.write()
            pdf_file = ContentFile(pdf_bytes, name=f"certificates/{register_number}.pdf")

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
                "status": "",
                "sgpa":""
            }
            """

            prompt = f"From {text}, fetch details in this format {data_format}. Must be in JSON format and data must be accurate. No additional comments or text should be there."

            grade_data = gemini_ai(prompt)
            
            if isinstance(grade_data, dict) and grade_data.get("flag"):
                student = Student.objects.filter(register_no=register_number).first() 

                Certificate.objects.create(
                    student=student if student else None,
                    certificate_pdf=pdf_file,  # Save only this student's PDF
                    grades=grade_data['data']
                )

            else:
                print("Invalid response format:", grade_data)
                return Response({'message': "AI returned an invalid format", 'error': grade_data}, status=status.HTTP_400_BAD_REQUEST)

    def extract_register_number(self, text):
        """Extract Register Number from the given text."""
        pattern = r'Register\s*No\.\s*[:\-]?\s*(\w+)'  
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1) if match else "Unknown"
