from django.http import Http404
from django.shortcuts import render

from .models import Course, Student
from .services import OlapService, QueryService


def render_table(request, template_name: str, table_data: dict, **extra_context):
    context = {
        "table": table_data,
        **extra_context,
    }
    return render(request, template_name, context)


def index(request):
    return render_table(request, "courses.html", QueryService.base_courses())


def students_list(request):
    return render_table(request, "students.html", QueryService.base_students())


def enrollments(request):
    return render_table(request, "enrollments.html", QueryService.base_enrollments())


def queries_list(request):
    return render(request, "queries.html", {"queries": QueryService.query_definitions()})


def query_run(request, query_id: int):
    data = QueryService.run_query(query_id)
    if data is None:
        raise Http404("Запрос не найден")
    return render_table(request, "query_result.html", data)


def olap_index(request):
    return render(request, "olap.html")


def olap_course_rollup(request):
    return render_table(request, "query_result.html", OlapService.course_rollup())


def olap_student_rollup(request):
    return render_table(request, "query_result.html", OlapService.student_rollup())


def olap_year_rollup(request):
    return render_table(request, "query_result.html", OlapService.year_rollup())


def olap_by_course(request):
    selected_course = request.GET.get("course_id")
    course_id = int(selected_course) if selected_course and selected_course.isdigit() else None
    return render_table(
        request,
        "query_result.html",
        OlapService.slice_by_course(course_id),
        courses=Course.objects.order_by("course_name"),
        selected_course=course_id,
    )


def olap_by_student(request):
    selected_student = request.GET.get("student_id")
    student_id = int(selected_student) if selected_student and selected_student.isdigit() else None
    return render_table(
        request,
        "query_result.html",
        OlapService.slice_by_student(student_id),
        students=Student.objects.order_by("last_name", "first_name"),
        selected_student=student_id,
    )


def olap_cube_face(request):
    return render_table(request, "query_result.html", OlapService.cube_face())
