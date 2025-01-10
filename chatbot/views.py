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

class ChatbotAPIView(APIView):
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


class ChatbotTeachersAPIView(APIView):
    def post(self, request):
        data = request.data
        document_id=request.data.get('document_id')
        doc = get_object_or_404(Certificate,id=document_id)
        question = data.get('question')

        prompt = f"""
        Please analyze the following document and answer the question.
        
        Question: {question}
        
        Document Content:
        {doc.grades}
        
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


