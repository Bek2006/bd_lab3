from django.db import models


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    department = models.CharField(max_length=100)

    class Meta:
        db_table = "teachers"
        managed = False

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField()
    credits = models.IntegerField()
    created_at = models.DateTimeField()
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.DO_NOTHING,
        db_column="teacher_id",
        related_name="courses",
    )

    class Meta:
        db_table = "courses"
        managed = False

    def __str__(self) -> str:
        return self.course_name


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    birth_date = models.DateField()
    enrollment_date = models.DateField()

    class Meta:
        db_table = "students"
        managed = False

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class StudentCourse(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        Student,
        on_delete=models.DO_NOTHING,
        db_column="student_id",
        related_name="student_courses",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.DO_NOTHING,
        db_column="course_id",
        related_name="course_students",
    )
    grade = models.DecimalField(max_digits=3, decimal_places=2)
    enrollment_date = models.DateField()

    class Meta:
        db_table = "student_courses"
        managed = False

    def __str__(self) -> str:
        return f"{self.student} - {self.course}"
