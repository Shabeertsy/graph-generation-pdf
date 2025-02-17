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
        if role==RoleChoices.STUDENT:
            student=Student.objects.get(profile=user)
            data={
                'token':str(token.access_token),
                'refresh':str(token),
                'role':role,
                'student_id':StudentSerializer(student).data.get('id')
            }
        else:

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
            user.save()
            return Response({'message':'password changed successfully'},status=status.HTTP_200_OK)
        return Response({'message':'password doesnt match'},status=status.HTTP_400_BAD_REQUEST)


## student registration

class StudentRegistrationAPIView(APIView):
    def post(self, request):
        # Extract fields from the request data
        email = request.data.get('email')
        name = request.data.get('name')
        password = request.data.get('password')
        phone = request.data.get('phone')
        father_email = request.data.get('father_email')
        father_phone = request.data.get('father_phone')
        roll_number = request.data.get('roll_number')
        date_of_birth = request.data.get('date_of_birth')
        address = request.data.get('address')
        city = request.data.get('city')
        state = request.data.get('state')
        pincode = request.data.get('pincode')
        programme = request.data.get('programme')
        department = request.data.get('department')
        year = request.data.get('year')

        # Check for missing mandatory fields
        if not email or not password or not phone or not roll_number or not date_of_birth:
            return Response({'message': 'Email, password, phone, roll number, and date of birth are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if Profile.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Create father profile if father_email is provided
        father = None
        if father_email:
            father, created = Profile.objects.get_or_create(
                email=father_email,
                defaults={
                    'role': RoleChoices.PARENT,
                    'phone': father_phone,
                    'username': father_email
                }
            )
 
        # print('name',name)
        # Create student profile
        profile_data = {
            'email': email,
            'password': password,
            'role': RoleChoices.STUDENT,
            'phone': phone,
            'username': email ,
            'first_name': name,
             
              # Username is the same as email here
        }
        try:
            student_profile = Profile.objects.create_user(**profile_data, father=father)
        except Exception as e:
            return Response({'message': f'Error creating student profile: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare student-specific data
        student_data = {
            'profile': student_profile.id,
            'roll_number': roll_number,
            'date_of_birth': date_of_birth,
            'address': address,
            'city': city,
            'state': state,
            'pincode': pincode,
            'programme': programme,
            'department': department,
            'year': year,
        }

        # Serialize student data
        student_serializer = StudentSerializer(data=student_data)
        if not student_serializer.is_valid():
            student_profile.delete()  # Rollback profile creation if serializer fails
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student = student_serializer.save()

        data = {
            'student': student_serializer.data
        }

        return Response({'data': data}, status=status.HTTP_201_CREATED)



class ParentRegistrationAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = Profile.objects.filter(email=email).first()
            parent = Parent.objects.filter(profile=profile).first()
            if profile:
                if Profile.objects.filter(email=email).exclude(role=RoleChoices.PARENT).exists():
                  return Response({'message': 'Email already exists for other user role'}, status=status.HTTP_400_BAD_REQUEST)
            
            if parent:
                return Response({'message': 'Parent with this email is already registered. Please log in.'}, status=status.HTTP_400_BAD_REQUEST)

            if profile and profile.role != RoleChoices.PARENT:
                profile.set_password(request.data.get('password'))
                profile.save()

            if not profile:
                profile_data = {
                    'email': email,
                    'password': request.data.get('password'),
                    'role': RoleChoices.PARENT,
                    'phone': request.data.get('phone'),
                    'username': email
                }
                
                profile = Profile.objects.create_user(**profile_data)

            parent_data = {
                'profile': profile.id,
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
                'programme': request.data.get('programme'),
                'department': request.data.get('department'),
                'year': request.data.get('year'),
                'occupation': request.data.get('occupation'),
                'address': request.data.get('address'),
                'city': request.data.get('city'),
                'state': request.data.get('state'),
                'pincode': request.data.get('pincode'),
                'relationship': request.data.get('relationship'),
            }

            parent_serializer = ParentSerializer(data=parent_data)
            if not parent_serializer.is_valid():
                return Response(parent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            parent_serializer.save()
            return Response({'message': 'Parent registered successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    

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


from django.shortcuts import get_object_or_404
class ViewParentData(APIView):
    def get(self,request):
        parent=get_object_or_404(Parent,profile=request.user)
        student=Student.objects.filter(profile__father=parent.profile)
        print(student)
        parent_serializer=ParentSerializer(parent)
        student_serializer=StudentSerializer(student,many=True)
        return Response({'parent':parent_serializer.data,'student':student_serializer.data})


class ParentDetailsByEmail(APIView):
    def get(self,request):
        parent=Profile.objects.filter(email=request.query_params.get('email')).first()
        data={
            'parent_email':parent.email,
            'parent_phone':parent.phone,
        }
        return Response(data,status=status.HTTP_200_OK)