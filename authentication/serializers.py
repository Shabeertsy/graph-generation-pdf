from rest_framework import serializers
from .models import Student, Parent, Profile,Teacher

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['email', 'role', 'phone']

class StudentSerializer(serializers.ModelSerializer):
    student_name=serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id','uuid','profile', 'roll_number', 'date_of_birth',
                 'blood_group', 'address', 'city', 'state', 'pincode','department','programme','year','student_name']
        
    def get_student_name(self,obj):
        return f'{obj.profile.first_name } '

class ParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = ['profile', 'occupation', 'annual_income', 'alternate_phone',
                 'address', 'city', 'state', 'pincode', 'relationship']
        
class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ['profile','programme', 'year', 'department','designation']



