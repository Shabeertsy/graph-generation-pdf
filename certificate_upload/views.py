import fitz 
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import CertificateSerializer
from chatbot.utils import gemini_ai


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
        


