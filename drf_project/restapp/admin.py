from django.contrib import admin
from restapp.models import Remote, CopyNote
from .request_to_rclone import rclone_client
from django.db import transaction
from django.core.exceptions import ValidationError


class CustomAdmin(admin.ModelAdmin):
       
       @transaction.atomic
       def save_model(self, request, obj: Remote, form, change):
              if not change:
                     status_code = obj.add_to_config(rclone_client)
                     if status_code == 200:
                            return super().save_model(request, obj, form, change)
                     else:
                            raise ValidationError('Error while adding to config')
              else: 
                     old_remote_name = Remote.objects.get(id=obj.id).name
                     rclone_client.delete_remote(remote_name=old_remote_name)
                     status_code = obj.add_to_config(rclone_client)
                     if status_code == 200:
                            return super().save_model(request, obj, form, change)
                     else:
                            raise ValidationError('Error while adding to config')
             

       @transaction.atomic
       def delete_model(self, request, obj: Remote):
              status_code = obj.delete_from_config(rclone_client)
              if status_code == 200:
                     return super().delete_model(request, obj)
              else:
                     raise ValidationError('Error while deleting config')
              
class CopyNoteAdmin(admin.ModelAdmin):
       readonly_fields = ('copy_date_time', 'object_name', 'copied_from', 'copied_to')


admin.site.register(Remote, CustomAdmin)
admin.site.register(CopyNote, CopyNoteAdmin)


# Register your models here.