from rest_framework import serializers
from restapp.models import Remote, CopyNote
from .request_to_rclone import CopyCase


# class RemoteSerializer(serializers.ModelSerializer):
#        class Meta:
#               model = Remote
#               fields = ['id', '_type', 'name', 'host', 'port', 'user']

class CopyNoteSerializer(serializers.ModelSerializer):
      
       copied_from = serializers.StringRelatedField()
       copied_to = serializers.StringRelatedField()

       #copied_from = serializers.SerializerMethodField(source='get_copied_from')
       #copied_to = serializers.SerializerMethodField(source='get_copied_to')       
       # def get_copied_from(self, obj):
       #       return obj.copied_from.name
       
       # def get_copied_to(self, obj):
       #        return obj.copied_to.name
       class Meta:
              model = CopyNote
              fields = '__all__'

class RcloneRemoteSerializer(serializers.Serializer):
       remote_name = serializers.CharField(max_length=255)
       path = serializers.CharField(max_length=255, default='', allow_blank=True)

class CopySerializer(serializers.Serializer):
       source_remote = serializers.CharField(max_length=255)
       source_file_path = serializers.CharField(max_length=255, allow_blank=True)
       destination_remote = serializers.CharField(max_length=255)
       destination_file_path = serializers.CharField(max_length=255, allow_blank=True)
       copy_flag = serializers.ChoiceField(choices=[(x[1].value, x[0]) for x in CopyCase.__members__.items()])

       def validate_source_remote(self, value):
           """
           Check that the source_remote name is valid
           """
           if Remote.objects.filter(name=value).exists():
                  return value
           else:
                  raise serializers.ValidationError('There is no such source_remote in config')

       def validate_destination_remote(self, value):
           """
           Check that the destination_remote name is valid
           """
           if Remote.objects.filter(name=value).exists():
                  return value
           else:
                  raise serializers.ValidationError('There is no such destination_remote in config')

       def validate_copy_flag(self, value):
              return CopyCase(value)
       