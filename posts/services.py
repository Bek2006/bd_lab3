from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from django.db.models import Avg, Count, Max, Min
from django.db.models.functions import ExtractYear

from .models import Course, Student, StudentCourse


@dataclass(frozen=True)
class QueryDefinition:
    query_id: int
    title: str
    description: str
    runner: Callable[[], dict]


class QueryService:
    """Возвращает данные в универсальном формате: title, columns, rows."""

    @staticmethod
    def _to_table(title: str, columns: list[str], rows: list[list]) -> dict:
        return {"title": title, "columns": columns, "rows": rows}

    @staticmethod
    def base_courses() -> dict:
        data = Course.objects.select_related("teacher").order_by("course_name")
        rows = [
            [
                item.course_name,
                item.credits,
                item.description,
                f"{item.teacher.first_name} {item.teacher.last_name}",
            ]
            for item in data
        ]
        return QueryService._to_table(
            "Список курсов",
            ["Курс", "Кредиты", "Описание", "Преподаватель"],
            rows,
        )

    @staticmethod
    def base_students() -> dict:
        data = Student.objects.order_by("last_name", "first_name")
        rows = [
            [
                f"{item.first_name} {item.last_name}",
                item.email,
                item.birth_date,
                item.enrollment_date,
            ]
            for item in data
        ]
        return QueryService._to_table(
            "Список студентов",
            ["Студент", "Email", "Дата рождения", "Дата поступления"],
            rows,
        )

    @staticmethod
    def base_enrollments() -> dict:
        data = StudentCourse.objects.select_related("student", "course").order_by(
            "course__course_name",
            "student__last_name",
        )
        rows = [
            [
                f"{item.student.first_name} {item.student.last_name}",
                item.course.course_name,
                item.grade,
                item.enrollment_date,
            ]
            for item in data
        ]
        return QueryService._to_table(
            "Электронный журнал",
            ["Студент", "Курс", "Оценка", "Дата записи"],
            rows,
        )

    @staticmethod
    def q1_students_with_high_grade() -> dict:
        data = (
            StudentCourse.objects.select_related("student", "course")
            .filter(grade__gte=4.0)
            .order_by("-grade")
        )
        rows = [
            [
                f"{item.student.first_name} {item.student.last_name}",
                item.course.course_name,
                item.grade,
            ]
            for item in data
        ]
        return QueryService._to_table(
            "ЛР: студенты с оценкой >= 4.0",
            ["Студент", "Курс", "Оценка"],
            rows,
        )

    @staticmethod
    def q2_course_load() -> dict:
        data = (
            Course.objects.annotate(
                students_count=Count("course_students", distinct=True),
                avg_grade=Avg("course_students__grade"),
            )
            .order_by("course_name")
            .values_list("course_name", "students_count", "avg_grade")
        )
        rows = [list(item) for item in data]
        return QueryService._to_table(
            "ЛР: нагрузка по курсам",
            ["Курс", "Количество студентов", "Средний балл"],
            rows,
        )

    @staticmethod
    def q3_teacher_courses() -> dict:
        data = (
            Course.objects.values("teacher__first_name", "teacher__last_name")
            .annotate(courses_count=Count("id"))
            .order_by("teacher__last_name", "teacher__first_name")
        )
        rows = [
            [
                f"{row['teacher__first_name']} {row['teacher__last_name']}",
                row["courses_count"],
            ]
            for row in data
        ]
        return QueryService._to_table(
            "ЛР: количество курсов у преподавателей",
            ["Преподаватель", "Количество курсов"],
            rows,
        )

    @staticmethod
    def query_definitions() -> list[QueryDefinition]:
        return [
            QueryDefinition(1, "Студенты с высокой оценкой", "Оценки >= 4.0", QueryService.q1_students_with_high_grade),
            QueryDefinition(2, "Нагрузка по курсам", "Количество студентов и средний балл по курсу", QueryService.q2_course_load),
            QueryDefinition(3, "Курсы преподавателей", "Число курсов у каждого преподавателя", QueryService.q3_teacher_courses),
        ]

    @staticmethod
    def run_query(query_id: int) -> dict | None:
        for definition in QueryService.query_definitions():
            if definition.query_id == query_id:
                return definition.runner()
        return None


class OlapService:
    @staticmethod
    def _metrics_base(queryset):
        return queryset.annotate(
            records_count=Count("id"),
            avg_grade=Avg("grade"),
            min_grade=Min("grade"),
            max_grade=Max("grade"),
        )

    @staticmethod
    def course_rollup() -> dict:
        data = OlapService._metrics_base(
            StudentCourse.objects.values("course__course_name").order_by("course__course_name")
        )
        rows = [
            [row["course__course_name"], row["records_count"], row["avg_grade"], row["min_grade"], row["max_grade"]]
            for row in data
        ]
        return QueryService._to_table(
            "OLAP Roll-up по курсу",
            ["Курс", "Число записей", "Средний балл", "Мин", "Макс"],
            rows,
        )

    @staticmethod
    def student_rollup() -> dict:
        data = OlapService._metrics_base(
            StudentCourse.objects.values("student__first_name", "student__last_name")
            .order_by("student__last_name", "student__first_name")
        )
        rows = [
            [
                f"{row['student__first_name']} {row['student__last_name']}",
                row["records_count"],
                row["avg_grade"],
                row["min_grade"],
                row["max_grade"],
            ]
            for row in data
        ]
        return QueryService._to_table(
            "OLAP Roll-up по студенту",
            ["Студент", "Число курсов", "Средний балл", "Мин", "Макс"],
            rows,
        )

    @staticmethod
    def year_rollup() -> dict:
        data = (
            StudentCourse.objects.annotate(year=ExtractYear("enrollment_date"))
            .values("year")
            .annotate(records_count=Count("id"), avg_grade=Avg("grade"))
            .order_by("year")
        )
        rows = [[row["year"], row["records_count"], row["avg_grade"]] for row in data]
        return QueryService._to_table(
            "OLAP Roll-up по году",
            ["Год", "Число записей", "Средний балл"],
            rows,
        )

    @staticmethod
    def slice_by_course(course_id: int | None) -> dict:
        data = StudentCourse.objects.select_related("student", "course").order_by(
            "student__last_name",
            "student__first_name",
        )
        title = "OLAP Slice по курсу"
        if course_id:
            data = data.filter(course_id=course_id)
            course = Course.objects.filter(id=course_id).first()
            if course:
                title = f"{title}: {course.course_name}"
        rows = [
            [f"{row.student.first_name} {row.student.last_name}", row.grade, row.enrollment_date]
            for row in data
        ]
        return QueryService._to_table(title, ["Студент", "Оценка", "Дата записи"], rows)

    @staticmethod
    def slice_by_student(student_id: int | None) -> dict:
        data = StudentCourse.objects.select_related("student", "course").order_by("course__course_name")
        title = "OLAP Slice по студенту"
        if student_id:
            data = data.filter(student_id=student_id)
            student = Student.objects.filter(id=student_id).first()
            if student:
                title = f"{title}: {student.first_name} {student.last_name}"
        rows = [[row.course.course_name, row.grade, row.enrollment_date] for row in data]
        return QueryService._to_table(title, ["Курс", "Оценка", "Дата записи"], rows)

    @staticmethod
    def cube_face() -> dict:
        data = StudentCourse.objects.select_related("student", "course").order_by(
            "course__course_name",
            "student__last_name",
        )
        rows = [
            [
                row.course.course_name,
                f"{row.student.first_name} {row.student.last_name}",
                row.grade,
                row.enrollment_date,
            ]
            for row in data
        ]
        return QueryService._to_table(
            "OLAP Грань: Курс × Студент",
            ["Курс", "Студент", "Оценка", "Дата записи"],
            rows,
        )
