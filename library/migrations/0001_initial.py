# Generated by Django 4.2.11 on 2024-05-10 17:21

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.CharField(max_length=20, unique=True)),
                ('accession_date', models.DateField(blank=True, null=True)),
                ('title', models.CharField(max_length=100)),
                ('vendor', models.CharField(max_length=100)),
                ('language', models.CharField(max_length=100)),
                ('publication', models.CharField(max_length=100)),
                ('shelf_name', models.CharField(max_length=100)),
                ('available_copies', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('faculty_id', models.CharField(max_length=20, unique=True)),
                ('max_books_allowed', models.PositiveIntegerField(default=1)),
                ('books_issued', models.ManyToManyField(blank=True, null=True, related_name='issued_to_faculty', to='library.book')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('adm_number', models.CharField(max_length=20, unique=True)),
                ('school_class', models.CharField(max_length=100)),
                ('max_books_allowed', models.PositiveIntegerField(default=1)),
                ('books_issued', models.ManyToManyField(blank=True, null=True, related_name='issued_to_student', to='library.book')),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateField(auto_now_add=True)),
                ('return_date', models.DateField(blank=True, null=True)),
                ('overdue_fee_per_day', models.DecimalField(decimal_places=2, default=5, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('overdue_amount', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('returned', models.BooleanField(default=False)),
                ('days', models.IntegerField(default=7, validators=[django.core.validators.MinValueValidator(1)])),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='library.book')),
                ('faculty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='faculty_issues', to='library.faculty')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_issues', to='library.student')),
            ],
        ),
    ]
