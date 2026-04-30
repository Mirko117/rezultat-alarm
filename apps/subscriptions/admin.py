from django.contrib import admin

from .models import Student, StudentExamSubscription

admin.site.register(Student)
admin.site.register(StudentExamSubscription)
