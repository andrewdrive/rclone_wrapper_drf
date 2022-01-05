from restapp.models import Remote
from restapp.request_to_rclone import rclone_client
from typing import Any, Optional
from django.core.management.base import BaseCommand
import subprocess


class Command(BaseCommand):

       def handle(self, *args: Any, **options: Any) -> Optional[str]:
              configs = rclone_client.config_dump()
              
              for config in configs:
                     rclone_client.delete_remote(config)

              self.stdout.write(self.style.WARNING(' - Config cleared.')) 

              remotes = Remote.objects.all()
              for obj in remotes:
                     obj.add_to_config(rclone_client)
              self.stdout.write(self.style.SUCCESS(' - Config rewrited successfully.'))    