from django.urls import path
from . import views
urlpatterns = [
 path("", views.index),
 path("students/", views.students_list),
 path("enrollments/", views.enrollments),
]