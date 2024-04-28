from django.contrib import admin
from .models import Student, Book, Faculty, Issue

# Register your models here.
admin.site.register(Student)
admin.site.register(Book)
admin.site.register(Faculty)
admin.site.register(Issue)