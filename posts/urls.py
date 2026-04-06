from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="courses"),
    path("students/", views.students_list, name="students"),
    path("enrollments/", views.enrollments, name="enrollments"),
    path("queries/", views.queries_list, name="queries"),
    path("queries/<int:query_id>/", views.query_run, name="query_run"),
    path("olap/", views.olap_index, name="olap_index"),
    path("olap/course-rollup/", views.olap_course_rollup, name="olap_course_rollup"),
    path("olap/student-rollup/", views.olap_student_rollup, name="olap_student_rollup"),
    path("olap/year-rollup/", views.olap_year_rollup, name="olap_year_rollup"),
    path("olap/by-course/", views.olap_by_course, name="olap_by_course"),
    path("olap/by-student/", views.olap_by_student, name="olap_by_student"),
    path("olap/cube-face/", views.olap_cube_face, name="olap_cube_face"),
]
