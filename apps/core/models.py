from django.db import models


class Major(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.name


class Professor(models.Model):
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name


class SchoolClass(models.Model):
    name = models.CharField(max_length=100)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="classes")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="classes")

    def __str__(self):
        return self.name


class Exam(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=False, null=False)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    classroom = models.CharField(max_length=100, blank=True, default="")
    results_available = models.BooleanField(default=False)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exams")

    def __str__(self):
        return self.name


class PageSnapshot(models.Model):
    page_hash = models.CharField(max_length=64, blank=True, default="")
    fetched_at = models.DateTimeField(auto_now=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="snapshots")

    def __str__(self):
        return f"Snapshot for {self.major.name} at {self.fetched_at}"
