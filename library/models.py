from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from datetime import timedelta
from datetime import date

class School(models.Model):
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    HIGHER_SECONDARY = 'higher_secondary'
    SCHOOL_LEVEL_CHOICES = [
        (PRIMARY, 'Primary'),
        (SECONDARY, 'Secondary'),
        (HIGHER_SECONDARY, 'Higher Secondary'),
    ]

    level = models.CharField(max_length=20, choices=SCHOOL_LEVEL_CHOICES, unique=True)

class User(AbstractUser):
    school = models.ForeignKey(School, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.username

class Book(models.Model):
    book_id = models.CharField(max_length=20, unique=True)
    accession_date = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    publication = models.CharField(max_length=100, blank=True)
    shelf_name = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    available_copies = models.PositiveIntegerField(default=0)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Student(models.Model):
    name = models.CharField(max_length=100)
    adm_number = models.CharField(max_length=20, unique=True)
    school_class = models.CharField(max_length=100)
    max_books_allowed = models.PositiveIntegerField(default=1)
    books_issued = models.ManyToManyField(Book, related_name='issued_to_student', blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    faculty_id = models.CharField(max_length=20, unique=True)
    max_books_allowed = models.PositiveIntegerField(default=1)
    books_issued = models.ManyToManyField(Book, related_name='issued_to_faculty', blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Issue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_issues', blank=True, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='faculty_issues', blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(blank=True, null=True)
    overdue_fee_per_day = models.DecimalField(default=5, max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    overdue_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    returned = models.BooleanField(default=False)
    days = models.IntegerField(default=7, validators=[MinValueValidator(1)])
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='issues')

    def calculate_overdue_amount(self, current_date=None):
        if current_date is None:
            current_date = date.today()

        if self.returned:
            return 0

        if self.return_date and self.return_date < current_date:
            overdue_days = (current_date - self.return_date).days
            return overdue_days * (self.overdue_fee_per_day or 0)
        
        return 0
    
    def save(self, *args, **kwargs):
        if self.returned and self.return_date:
            self.overdue_amount = self.calculate_overdue_amount(self.return_date)
        else:
            self.overdue_amount = self.calculate_overdue_amount(date.today())
        super().save(*args, **kwargs)

    def __str__(self):
        if self.student:
            return f"{self.book.title} issued to {self.student.name}"
        elif self.faculty:
            return f"{self.book.title} issued to {self.faculty.name}"
        else:
            return f"{self.book.title} issued (unspecified)"
