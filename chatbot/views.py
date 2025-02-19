from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import fitz  # PyMuPDF
from .models import PDFDocument
from .serializers import PDFDocumentSerializer
import openai
## Gemini api
import google.generativeai as genai
from decouple import config
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PDFDocumentSerializer
import json
from decouple import config
from django.shortcuts import get_object_or_404
from certificate_upload.models import Certificate
class PDFUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Handle PDF upload
        serializer = PDFDocumentSerializer(data=request.data)
        if serializer.is_valid():
            pdf_document = serializer.save()
            self.extract_text_from_pdf(pdf_document)
            return Response(PDFDocumentSerializer(pdf_document).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def extract_text_from_pdf(self, pdf_document):
        # Extract text from PDF using PyMuPDF
        pdf_file_path = pdf_document.uploaded_pdf.path
        document = fitz.open(pdf_file_path)
        
        text = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text += page.get_text()

        # Store the extracted text in the database
        pdf_document.extracted_text = text
        pdf_document.save()


GOOGLE_API_KEY= config('API_KEY') if config('API_KEY') else ''

class DocChatbotAPIView(APIView):
    def post(self, request):
        data = request.data
        document_id=request.data.get('document_id')
        doc = get_object_or_404(PDFDocument,id=document_id)
        question = data.get('question')

        prompt = f"""
        Please analyze the following document and answer the question.
        
        Question: {question}
        
        Document Content:
        {doc.extracted_text}
        
        Please provide a clear and concise answer based on the document content above.
        """
        
        # Using Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        try:
            response = model.generate_content(prompt)
            answer = response.text.strip()
            print(answer)
            
            return Response({
                'answer': answer,
                'status': 'success'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': 'Error processing your request',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


from certificate_upload.models import  Certificate, ActivityCertificate, CertificateMarks
from authentication.models import Student

genai.configure(api_key=GOOGLE_API_KEY)

class ChatbotAPIView(APIView):
    def post(self, request):
        data = request.data
        question = data.get('question')

        if not question:
            return Response({'message': 'Question is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all students
        students = Student.objects.all()

        if not students.exists():
            return Response({'message': 'No students found'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare student data
        all_students_data = []
        for student in students:
            student_info = {
                "Name": f"{student.profile.first_name} {student.profile.last_name}",
                "Email": student.profile.email,
                "Roll Number": student.roll_number,
                "Register Number": student.register_no,
                "Department": student.department,
                "Programme": student.programme,
                "Year": student.year,
                "Total Activity Marks": student.total_activity_marks,
            }

            # Fetch certificates
            certificates = Certificate.objects.filter(student=student)
            certificates_data = [
                {"Certificate ID": cert.id, "Grades": cert.grades, "Uploaded At": cert.uploaded_at}
                for cert in certificates
            ]

            # Fetch activity certificates
            activity_certificates = ActivityCertificate.objects.filter(student=student)
            activity_data = [
                {
                    "Title": cert.title,
                    "Type": cert.activity_type,
                    "Issuing Organization": cert.issuing_organization,
                    "Marks": cert.mark,
                    "Achievement": cert.achievement_level,
                    "Approved": cert.is_approved,
                }
                for cert in activity_certificates
            ]

            # Fetch certificate marks
            marks_data = [
                {
                    "Activity": cert.certifcate.title,
                    "Marks": cert.marks,
                    "Status": "Approved" if cert.status else "Pending",
                }
                for cert in CertificateMarks.objects.filter(certifcate__student=student)
            ]

            # Combine all data
            student_entry = {
                "Student Information": student_info,
                "Certificates": certificates_data,
                "Activity Certificates": activity_data,
                "Marks Data": marks_data,
            }
            all_students_data.append(student_entry)

        # Formulate the prompt
        prompt = f"""
        Here is the data for all students in the system:
        {all_students_data}

        Based on the above data, please answer the following question in a descripitve manner:
        {question}
        """

        try:
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            answer = response.text.strip()

            return Response({'answer': answer, 'status': 'success'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': 'Error processing request', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

