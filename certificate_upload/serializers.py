from rest_framework import serializers
from .models import Certificate,ActivityCertificate
from django.db.models import Sum
from chatbot.utils import gemini_ai
import re

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'student', 'certificate_pdf', 'grades', 'uploaded_at']


class ActivityCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCertificate
        fields = ['id', 'student', 'title', 'description', 'certificate_file', 'activity_type', 'issue_date', 'issuing_organization', 'achievement_level','mark']

    def create(self, validated_data):
        activity_certificate = ActivityCertificate.objects.create(**validated_data)
        
        prompt = (
            f"You are a marking system. Based on the following certificate details, "
            f"assign a numerical mark out of 10. Consider the following factors:\n"
            f"- Title: {activity_certificate.title}\n"
            f"- Activity Type: {activity_certificate.activity_type}\n"
            f"- Achievement Level: {activity_certificate.achievement_level}\n"
            f"- Certificate content: {activity_certificate.pdf_text}\n"
            f"- Organization: {activity_certificate.issuing_organization}\n\n"
            f"Please respond with ONLY a numerical value between 0 and 10. "
            f"For example: 8.5"
        )
        
        mark_data = gemini_ai(prompt, json_format=False)
        print(mark_data)
        
        try:
            if mark_data['flag']:
                mark_str = mark_data['data'].strip()
                number_match = re.search(r'\d*\.?\d+', mark_str)
                
                if number_match:
                    mark = float(number_match.group())
                    mark = min(max(mark, 0), 10)
                    
                    activity_certificate.mark = mark
                    activity_certificate.save()
                    
                    student = activity_certificate.student
                    total_marks = ActivityCertificate.objects.filter(student=student).aggregate(Sum('mark'))['mark__sum'] or 0
                    student.total_activity_marks = total_marks
                    student.save()
                else:
                    activity_certificate.mark = 0
                    activity_certificate.save()
        except Exception as e:
            print(f"Error processing mark: {e}")
            activity_certificate.mark = 0
            activity_certificate.save()
            
        return activity_certificate
    