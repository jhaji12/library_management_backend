# library/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Issue

@shared_task
def update_overdue():
    try:
        today = timezone.localtime().date()
        issues = Issue.objects.filter(returned=False, return_date__lt=today)
        print("here", issues)
        for issue in issues:
            print("here", issue)
            days_overdue = (today - issue.return_date).days
            issue.overdue_amount = issue.overdue_fee_per_day * days_overdue
            issue.save()
    except Exception as e:
        print("error", e)
