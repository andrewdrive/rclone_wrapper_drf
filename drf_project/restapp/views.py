from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from restapp.serializers import RcloneRemoteSerializer, CopySerializer, CopyNoteSerializer
from restapp.models import Remote, CopyNote
from django.core import management
from drf_yasg.utils import swagger_auto_schema
from .request_to_rclone import rclone_client
from .exceptions import RcloneListingError, RcloneJobStatusError
from .filters import CopyNoteFilter


@api_view(['GET'])
def list_remotes(request):
       """    * Show all remotes in config  """
       res = rclone_client.listremotes()['remotes']
       return Response(res, status=status.HTTP_200_OK)

@api_view(['GET'])
def config_dump(request):
       """    * Dumps a JSON file of config info   """
       res = rclone_client.config_dump()
       return Response(res)

@api_view(['GET'])
def rewrite_config(request):
       """    * Rewrites config file   """
       management.call_command('sync')
       text = 'Config rewrited'
       return Response(text)

@swagger_auto_schema(method='POST', request_body=RcloneRemoteSerializer)
@api_view(['POST'])
def path_listing(request):
       """    * List the given remote and path (initially, in JSON format)    """
       serializer = RcloneRemoteSerializer(data=request.data)
       if serializer.is_valid():
              remote = rclone_client.get_remote(remote_name=serializer.data['remote_name'])
              try:
                     res = remote.operations_list(path=serializer.data['path'])['list']
              except RcloneListingError as le:
                     return Response(le.message, status=le.status_code)
              return Response(res, status=status.HTTP_200_OK)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='POST', request_body=CopySerializer)
@api_view(['POST'])
def copy(request):
       """ 
       operations/copyfile command 
       * parameters:
         * source_remote - a remote name string e.g. "SFTP" for the source
         * source_file_path - a path within that remote e.g. "Distrib/Thumbs.db" for the source
         * destination_remote - a remote name string e.g. "LocalRemote" for the destination
         * destination_file_path - a path within that remote e.g. "Desktop/Thumbs2.db" for the destination
       ----         
       sync/copy command 
       * parameters:
         * source_remote:source_file_path - a remote name string e.g. "drive1:dir1" for the source
         * destionation_remote:destination_file_path - a remote name string e.g. "drive2:dir2" for the destination
       ----
        copy_flag:
          *  0 - Rewrite file/dir 
          *  1 - Create copy with underscore in file_name
          *  2 - Cancel copy
       """
       serializer = CopySerializer(data=request.data)
       if serializer.is_valid():
              source_remote = serializer.data['source_remote']
              source_file_path = serializer.data['source_file_path'] 
              destination_remote = serializer.data['destination_remote']
              destination_file_path = serializer.data['destination_file_path']
              copy_flag = serializer.data['copy_flag']
              source_object_name = source_file_path.split('/')[-1]
        
              status_turp = rclone_client.copy(source_remote, source_file_path,
                                                   destination_remote, destination_file_path,
                                                   copy_flag)
              if status_turp[0] == 200:
                     copied_from = Remote.objects.get(name=source_remote)
                     copied_to = Remote.objects.get(name=destination_remote)
                     if status_turp[1] == 'file':
                            CopyNote(object_name=source_object_name, copied_from=copied_from, copied_to=copied_to).save()
                            return Response({'jobid': status_turp[2]}, status=status.HTTP_200_OK)                                   
                     if status_turp[1] == 'dir':
                            CopyNote(object_name=source_object_name, copied_from=copied_from, copied_to=copied_to).save()
                            return Response({'jobid': status_turp[2]}, status=status.HTTP_200_OK)
              return Response(status_turp[1], status_turp[0])
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def core_stats(request, jobid):
       """ Returns stats about current transfers. 
           * EXAMPLE FOR FASTAPI WEBSOCKET USAGE: ws://0.0.0.0:8003/ws/15
       """
       try:
              res = rclone_client.core_stats(jobid=jobid)
       except RcloneJobStatusError as le:
              return Response(le.message, status=le.status_code)
       return Response(res, status=status.HTTP_200_OK)
    

class CopyNoteViewSet(viewsets.ReadOnlyModelViewSet):
       queryset = CopyNote.objects.all().select_related('copied_from', 'copied_to')
       serializer_class = CopyNoteSerializer
       filter_backends = [DjangoFilterBackend]
       filterset_class = CopyNoteFilter


# class RcloneRemoteViewSet(viewsets.ReadOnlyModelViewSet):
#        queryset = Remote.objects.all()
#        serializer_class = RemoteSerializer