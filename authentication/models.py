from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


# baseclass
class BaseClass(models.Model):
    uuid=models.SlugField(default=uuid.uuid4,unique=True)
    active_status=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class RoleChoices(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    PARENT = 'Parent', 'Parent' 
    TEACHER = 'Teacher', 'Teacher'
    STUDENT = 'Student', 'Student'


## Profile model 
class Profile(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    username = models.CharField(max_length=150, null=True, blank=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    role = models.CharField(max_length=10, choices=RoleChoices.choices)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    father = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.email} ,-- {self.role}'
    
    class Meta:
        ordering=['-id']
        verbose_name='Profile'
        verbose_name_plural='Profile'



class Student(BaseClass):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='student')
    roll_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    admission_date = models.DateTimeField(default=timezone.now)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    department=models.CharField(max_length=100)
    programme=models.CharField(max_length=100)
    year=models.CharField(max_length=100)
    total_activity_marks=models.FloatField(default=0)
    register_no=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f"{self.profile.email} - {self.roll_number}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'


class Parent(BaseClass):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='parent')
    occupation = models.CharField(max_length=100)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    alternate_phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    relationship = models.CharField(max_length=20, choices=[
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Guardian', 'Guardian')
    ])

    def __str__(self):
        return f"{self.profile.email} - {self.relationship}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Parent'
        verbose_name_plural = 'Parents'

class Teacher(BaseClass):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='Teacher')
    programme=models.CharField(max_length=25,null=True,blank=True)
    year=models.CharField(max_length=25,null=True,blank=True)
    department=models.CharField(max_length=25,null=True,blank=True)
    designation=models.CharField(max_length=25,null=True,blank=True)
    def __str__(self):
        return f"{self.profile.email} - {self.programme}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Teacher'
        verbose_name_plural = 'Teachers'


class OTP(BaseClass):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6)
    expiry = models.DateTimeField()

    def __str__(self):
        return f"{self.profile.email} - {self.otp}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'OTP'
        verbose_name_plural = 'OTPs'