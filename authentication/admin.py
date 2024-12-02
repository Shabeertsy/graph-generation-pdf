from django.contrib import admin
from .models import *



class ProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'role')
    list_filter = ('role',)
    search_fields = ('email',)
    ordering = ('-id',)

admin.site.register(Profile, ProfileAdmin)

admin.site.register(Student)
admin.site.register(Parent) 