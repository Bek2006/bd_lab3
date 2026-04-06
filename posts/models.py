from django.db import models
from django.db.models import Q
from django.utils import timezone
import datetime
class Course(models.Model):
 course_name = models.CharField(max_length=100)
 description = models.TextField()
 credits = models.IntegerField()
 created_at = models.DateTimeField(default=timezone.now)
 def __str__(self):
 return self.course_name
class Student(models.Model):
 first_name = models.CharField(max_length=50)
 last_name = models.CharField(max_length=50)
 email = models.EmailField(max_length=100)
 birth_date = models.DateField()
 enrollment_date = models.DateField(default=datetime.date.today)
 def __str__(self):
 return f"{self.first_name} {self.last_name}"
class StudentCourse(models.Model):
 student = models.ForeignKey(
 Student,
 on_delete=models.CASCADE
 )
 course = models.ForeignKey(
 Course,
 on_delete=models.CASCADE
 )
 grade = models.DecimalField(max_digits=3, decimal_places=2)
 enrollment_date = models.DateField(default=datetime.date.today)
 class Meta:
 constraints = [
 models.CheckConstraint(
 check=Q(grade__gte=0) & Q(grade__lte=5),
 name="grade_between_0_and_5"
 ),
 models.UniqueConstraint(
 fields=["student", "course"],
 name="unique_student_course"
 )
 ]
 def __str__(self):
 return f"{self.student} - {self.course}"