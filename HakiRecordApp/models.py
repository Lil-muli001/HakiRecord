from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.utils.encoding import force_str
from django.contrib.contenttypes.models import ContentType
import json

class Statement(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=100)
    dob = models.DateField()
    service_no = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    INCIDENT_TYPES = [
        ('theft', 'Theft'),
        ('murder', 'Murder'),
        ('abuse', 'Child Abuse'),
        ('accident', 'Accident'),
    ]
    incident_type = models.CharField(max_length=20, choices=INCIDENT_TYPES)

    incident_location = models.CharField(max_length=255)

    incident_date = models.DateField(default=timezone.now)

    INCIDENT_TIMES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]
    incident_time = models.CharField(max_length=20, choices=INCIDENT_TIMES)

    suspect_description = models.TextField(blank=True, null=True)

    incident_description = models.TextField(blank=True, null=True)
    incident_evidence = models.FileField(upload_to='evidence/')
    ob_number = models.CharField(max_length=30, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ob_number:
            today = timezone.localtime().date()
            # Count how many entries are recorded today
            count_today = Statement.objects.filter(
                recorded_at__date=today
            ).count() + 1
            # Generate OB number, e.g., "OB 1/14/10/2025"
            self.ob_number = f"OB {count_today}/{today.day}/{today.month}/{today.year}"
        super().save(args, *kwargs)

    recorded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.first_name} {self.last_name}"

class Contact(models.Model):
    contact_name = models.CharField(max_length=120)
    contact_email = models.EmailField(max_length=100)
    contact_message = models.TextField()

    def _str_(self):
       return f"{self.contact_name} {self.contact_email}"

class StatementAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            # Compare old and new field values
            old_obj = self.model.objects.get(pk=obj.pk)
            changes = {}
            for field in form.changed_data:
                old_value = getattr(old_obj, field)
                new_value = getattr(obj, field)
                changes[field] = {"old": str(old_value), "new": str(new_value)}

            # Save the object
            super().save_model(request, obj, form, change)

            # Log a more detailed change message
            change_message = json.dumps({"changed_fields": changes})
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=force_str(obj),
                action_flag=CHANGE,
                change_message=change_message,
            )
        else:
            super().save_model(request, obj, form, change)

