from django.contrib import admin

from .models import Exam, Major, PageSnapshot, Professor, SchoolClass

admin.site.register(Major)
admin.site.register(Professor)
admin.site.register(SchoolClass)
admin.site.register(Exam)
admin.site.register(PageSnapshot)
