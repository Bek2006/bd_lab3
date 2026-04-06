from django.shortcuts import render
from .models import Course, Student, StudentCourse
def index(request):
 courses = Course.objects.all().order_by("course_name")
 return render(request, "courses.html", {
 "courses": courses
 })
def students_list(request):
 students = Student.objects.all().order_by("last_name")
 return render(request, "students.html", {
 "students": students
 })
def enrollments(request):
 enrollments = StudentCourse.objects.select_related(
 "student",
 "course"
 ).all()
 return render(request, "enrollments.html", {
 "enrollments": enrollments
 })
