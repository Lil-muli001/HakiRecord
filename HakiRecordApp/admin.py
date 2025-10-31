from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
import json

class StatementAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'id_number', 'incident_type', 'incident_location', 'incident_date')
    search_fields = ('id_number', 'last_name', 'incident_location')
    list_filter = ('recorded_at',)
    readonly_fields = [f.name for f in Statement._meta.fields]

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Statement,StatementAdmin)
class ContactAdmin(admin.ModelAdmin):
    list_display = ( 'contact_name', 'contact_email', 'contact_message')
    search_fields = ( 'contact_name', 'contact_email', 'contact_message')
    list_filter = ('contact_name', 'contact_email', 'contact_message')

admin.site.register(Contact, ContactAdmin)

class DetailedLoggingAdmin(admin.ModelAdmin):
    """Logs old and new field values in admin actions."""

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            changes = {}

            for field in form.changed_data:
                old_value = getattr(old_obj, field)
                new_value = getattr(obj, field)
                changes[field] = {"old": str(old_value), "new": str(new_value)}

            super().save_model(request, obj, form, change)

            # Create detailed log entry
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=force_str(obj),
                action_flag=CHANGE,
                change_message=json.dumps({"changed_fields": changes}),
            )
        else:
            super().save_model(request, obj, form, change)