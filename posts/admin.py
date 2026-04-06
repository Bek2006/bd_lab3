from django.contrib import admin

from .models import Course, Student, StudentCourse, Teacher

admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(StudentCourse)
