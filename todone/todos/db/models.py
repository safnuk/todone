from django.db import models

from .. import folders

class Todo(models.Model):
    action = models.CharField(max_length=255)
    folder = models.CharField(
        max_length=15,
        choices=folders.FOLDER_CHOICES,
        default=folders.INBOX,
    )
    remind_date = models.DateField(
        blank=True, null=True,
    )
    date_completed = models.DateField(
        blank=True, null=True,
    )
    due_date = models.DateField(
        blank=True, null=True
    )
    notes = models.TextField(blank=True)
    repeat_interval = models.CharField(
        max_length=10, blank=True,
    )
