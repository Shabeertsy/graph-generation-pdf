## restframework  imports 
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.db.models import Q

## django imports 
from django.contrib.auth import authenticate


## model imports
from .models import Profile,Student,Parent,Teacher

## serializer imports
from .serializers import StudentSerializer,ParentSerializer,ProfileSerializer,TeacherSerializer

## Other imports
from .permissions import *


##  login api
class LoginAPIView(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')

        user=authenticate(email=email,password=password)

        if user is None:
            return Response ({'message':'invalid credentials'},status=status.HTTP_400_BAD_REQUEST)

        token=RefreshToken.for_user(user)
        role=user.role
        data={
            'token':str(token.access_token),
            'refresh':str(token),
            'role':role
        }

        return Response({'data':data},status=status.HTTP_200_OK)



## change password
class ChangePassword(APIView):
    permission_classes=[IsStudent|IsTeacher]
    def post(self,request):
        user=request.user
        password=request.data.get('old_password')

        if user.check_password(password):
            new_password=request.data.get('new_password')
            user.set_password(new_password)
            return Response({'message':'password changed successfully'},status=status.HTTP_200_OK)
        return Response({'message':'password doesnt match'},status=status.HTTP_400_BAD_REQUEST)


## student registration
class StudentRegistrationAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        profile_data = {
            'email': email,
            'password': request.data.get('password'),
            'role': RoleChoices.STUDENT,
            'phone': request.data.get('phone'),
            'username': request.data.get('email') 
        }

        # Check if email exists
        if Profile.objects.filter(email=profile_data['email']).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        father = None
        if father_email := request.data.get('father_email'):
            father, _ = Profile.objects.get_or_create(
                email=father_email,
                defaults={
                    'role': RoleChoices.PARENT,
                    'phone': request.data.get('father_phone'),
                    'username': father_email
                }
            )
        # Create student profile
        student_profile = Profile.objects.create_user(
            **profile_data,
            father=father
        )

        student_data = {
            'profile': student_profile.id,
            'roll_number': request.data.get('roll_number'),
            'date_of_birth': request.data.get('date_of_birth'),
            'address': request.data.get('address'),
            'city': request.data.get('city'), 
            'state': request.data.get('state'),
            'pincode': request.data.get('pincode'),
            'programme': request.data.get('programme'),
            'department': request.data.get('department'),
            'year': request.data.get('year'),
        }
        print(student_data)
        student_serializer = StudentSerializer(data=student_data)
        if not student_serializer.is_valid():
            student_profile.delete()
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        student = student_serializer.save()
        # Generate token
        # token = RefreshToken.for_user(profile)
        
        data = {
                # 'token': str(token.access_token),
                # 'refresh': str(token),
            'student': student_serializer.data
        }

        return Response({'data': data}, status=status.HTTP_201_CREATED)


## parent registration 
class ParentRegistrationAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        
        try:
            parent_profile = Profile.objects.get(
                Q(email=email) | Q(phone=phone),
                role=RoleChoices.PARENT
            )
            
            # Update existing parent profile with new details
            parent_profile.first_name = request.data.get('first_name', parent_profile.first_name)
            parent_profile.last_name = request.data.get('last_name', parent_profile.last_name)
            if request.data.get('password'):
                parent_profile.set_password(request.data.get('password'))
            parent_profile.save()

        except Profile.DoesNotExist:
            # Create new parent profile if doesn't exist
            profile_data = {
                'email': email,
                'password': request.data.get('password'),
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                'phone': phone,
                'role': RoleChoices.PARENT,
                'username': email
            }
            parent_profile = Profile.objects.create_user(**profile_data)

        # Update or create parent details
        parent_data = {
            'profile': parent_profile.id,
            'occupation': request.data.get('occupation'),
            'address': request.data.get('address'),
            'city': request.data.get('city'),
            'state': request.data.get('state'),
            'pincode': request.data.get('pincode'),
            'department':request.data.get('department'),
            'programme':request.data.get('programme'),
            'year':request.data.get('year')
        }

        # Try to get existing parent object or create new one
        try:
            parent = Parent.objects.get(profile=parent_profile)
            parent_serializer = ParentSerializer(parent, data=parent_data)
        except Parent.DoesNotExist:
            parent_serializer = ParentSerializer(data=parent_data)

        if not parent_serializer.is_valid():
            if parent_profile._state.adding:  
                parent_profile.delete()
            return Response(parent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        parent = parent_serializer.save()
        
        data = {
            'parent': parent_serializer.data
        }

        return Response({'data': data}, status=status.HTTP_201_CREATED)
    

##teacher registration
class TeacherRegistrationAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        profile_data = {
            'email': email,
            'password': request.data.get('password'),
            'role': RoleChoices.TEACHER,
            'phone': request.data.get('phone'),
            'username': request.data.get('email') 
        }

        # Check if email exists
        if Profile.objects.filter(email=profile_data['email']).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    
        # Create teacher profile
        teacher_profile = Profile.objects.create_user(
            **profile_data,
        
        )

        teacher_data = {
            'profile': teacher_profile.id,
            'programme': request.data.get('programme'), 
            'year': request.data.get('year'),
            'department': request.data.get('department'),
            'designation': request.data.get('designation')
        }
        print(teacher_data)
        teacher_serializer = TeacherSerializer(data=teacher_data)
        if not teacher_serializer.is_valid():
            teacher_profile.delete()
            return Response(teacher_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        teacher = teacher_serializer.save()
        # Generate token
        # token = RefreshToken.for_user(profile)
        
        data = {
                # 'token': str(token.access_token),
                # 'refresh': str(token),
            'teacher': teacher_serializer.data
        }

        return Response({'data': data}, status=status.HTTP_201_CREATED)
    
##student details for teacher
class StudentsDetailsAPIView(APIView):
    def get(self, request):
        year=request.GET.get('year')
        programme=request.GET.get('programme')
        students=Student.objects.all()
        if year :
            students=students.filter(year=year)
        if programme:
            students=students.filter(programme=programme)
        if students:
            return Response({'message':'Student found'})
        else:
            return Response({'message':'Student not found'})


