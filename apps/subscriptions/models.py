from core.models import Exam
from django.db import models


class Student(models.Model):
    email_encrypted = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Student id: {self.pk}"


class StudentExamSubscription(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription: Student {self.student.pk} to Exam {self.exam.pk}"
