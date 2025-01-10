from rest_framework import serializers
from .models import Student, Parent, Profile,Teacher

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['email', 'role', 'phone']

class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ['profile', 'roll_number', 'date_of_birth',
                 'blood_group', 'address', 'city', 'state', 'pincode','department','programme','year']


class ParentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = ['profile', 'occupation', 'annual_income', 'alternate_phone',
                 'address', 'city', 'state', 'pincode', 'relationship']
        
class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher
        fields = ['profile','programme', 'year', 'department','designation']



