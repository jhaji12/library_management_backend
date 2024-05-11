from django.db import models
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone


class Book(models.Model):
    book_id = models.CharField(max_length=20, unique=True)
    accession_date = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    publication = models.CharField(max_length=100)
    shelf_name = models.CharField(max_length=100)
    available_copies = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Student(models.Model):
    name = models.CharField(max_length=100)
    adm_number = models.CharField(max_length=20, unique=True)
    school_class = models.CharField(max_length=100)
    max_books_allowed = models.PositiveIntegerField(default=1)
    books_issued = models.ManyToManyField(Book, related_name='issued_to_student', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Faculty(models.Model):
    name = models.CharField(max_length=100)
    faculty_id = models.CharField(max_length=20, unique=True)
    max_books_allowed = models.PositiveIntegerField(default=1)
    books_issued = models.ManyToManyField(Book, related_name='issued_to_faculty', blank=True, null=True)

    def __str__(self):
        return self.name

class Issue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_issues', blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='faculty_issues', blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)
    overdue_fee_per_day = models.DecimalField(default=5, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    overdue_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    returned = models.BooleanField(default=False)
    days = models.IntegerField(default=7, validators=[MinValueValidator(1)])

    def save(self, *args, **kwargs):
        if not self.returned and not self.return_date:
            self.return_date = timezone.now().date() + timedelta(days=self.days)

        if self.return_date and self.issue_date and self.return_date < timezone.now().date():
            # Calculate days overdue
            days_overdue = (timezone.now().date() - self.return_date).days

            self.overdue_amount = self.overdue_fee_per_day * days_overdue
        else:
            self.overdue_amount = 0  # No overdue amount if return date is not set or is before issue date

        super().save(*args, **kwargs)

    def __str__(self):
        if self.student:
            return f"{self.book.title} issued to {self.student.name}"
        elif self.faculty:
            return f"{self.book.title} issued to {self.faculty.name}"
        else:
            return f"{self.book.title} issued (unspecified)"

