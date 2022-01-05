from django.db import models


class Remote(models.Model):
       
       SFTP = 'sftp'
       FTP = 'ftp'
       LOCAL = 'local'

       TYPE_CHOICES = [
              (SFTP, 'sftp'),
              (FTP, 'ftp'),
              (LOCAL, 'local'),
       ]

       name = models.CharField(max_length=50, unique=True)
       _type = models.CharField(max_length=50,
                                choices=TYPE_CHOICES,
                                default='sftp',)
       host = models.CharField(max_length=100)
       port = models.IntegerField()
       user = models.CharField(max_length=30, default='user')
       password = models.CharField(max_length=100, default='pass')
       disable_hashcheck = models.BooleanField(default=True)

       def __str__(self):
              return self.name
       
       def add_to_config(self, client):
              """    Add remote from model to config    """
              params = {"name": self.name, "type":  self._type, "parameters": {"host": self.host, "port": self.port, "user": self.user,
                            "pass": self.password, "disable_hashcheck": self.disable_hashcheck}}
              status_code = client.create_remote(params)
              return status_code

       def delete_from_config(self, client):
              """    Delete remote from config   """
              status_code = client.delete_remote(remote_name=self.name)
              return status_code

       class Meta:
              ordering = ['_type']

class CopyNote(models.Model):
       
       object_name = models.CharField(max_length=100)
       copy_date_time = models.DateTimeField(auto_now_add=True, verbose_name='Copy datetime')
       copied_from = models.ForeignKey(Remote, on_delete=models.CASCADE, related_name='copied_from_story')
       copied_to = models.ForeignKey(Remote, on_delete=models.CASCADE, related_name='copied_to_story') 
       
       def __str__(self):
              return self.object_name
       
       class Meta:
              default_related_name = 'copy_notes'
              ordering = ['copy_date_time']


# Create your models here.