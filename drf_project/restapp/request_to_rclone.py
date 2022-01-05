import requests
import os
from .exceptions import RcloneCopyFileError, RcloneCopyDirError, RcloneListingError, RcloneJobStatusError
from enum import Enum

class CopyCase(Enum):
       rewrite = 0
       create_copy_under_score = 1
       cancel = 2

class RcloneClient:
       """
              Wrapper class for rclone_http usage
              provides get_all_remotes, get_specific_remote and copy methods
              
       """
       def __init__(self, host_name=None, port=None):
              """  """
              self.host_name = host_name
              self.port = port

       def listremotes(self):
              """ 
                     --- config/listremotes command ---
              Returns remotes - array of remote names in config file of rclone
              """
              url = 'http://{host_name}:{port}/config/listremotes'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, data={})
              return response.json()

       def get_remote(self, remote_name):
              """
                     Returns existing specific remote by passing remote_name
              """
              return RcloneRemote(remote_name=remote_name, host=self.host_name, port=self.port)

       def create_remote(self, parameters):
              """
                     --- config/create command ---
              name - name of remote
              parameters - a map of { "key": "value" } pairs
              type - type of the new remote
              """
              url = 'http://{host_name}:{port}/config/create'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, json=parameters)
              return response.status_code

       def delete_remote(self, remote_name):
              """
                     --- config/delete command ---
              parameters:
              name - name of remote to delete
              """
              url = 'http://{host_name}:{port}/config/delete'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, data={'name': remote_name})
              return response.status_code

       def config_dump(self):
              """
                  --- Returns a JSON object:
              key: value
              Where keys are remote names and values are the config parameters.
              """
              url = 'http://{host_name}:{port}/config/dump'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url)
              return response.json()

       def copy_file(self, source_remote, source_file_path, destination_remote, destination_file_path):
              """
                     --- operations/copyfile command ---
              parameters:
              source_remote - a remote name string e.g. "SFTP:Distrib/" for the source
              source_file_path - a path within that remote e.g. "Thumbs.db" for the source
              destination_remote - a remote name string e.g. "LocalRemote:Desktop/" for the destination
              destination_file_path - a path within that remote e.g. "Thumbs2.db" for the destination
              """
              url = 'http://{host_name}:{port}/operations/copyfile'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, data={'srcFs': source_remote, 'srcRemote': source_file_path,
                                                  'dstFs': destination_remote, 'dstRemote': destination_file_path, '_async': True})
              jobid = response.json()['jobid']
              if self.job_status(jobid)['error'] != '':
                     raise RcloneCopyFileError(message=response.json(), status_code=response.status_code)
              return (response.status_code, response.headers['X-Rclone-Jobid'])

       def copy_dir(self, source_remote, destination_remote):
              """
                  --- sync/copy command ---
              parameters:
              source_remote:source_file_path - a remote name string e.g. "drive1:dir1" for the source
              destionation_remote:destination_file_path - a remote name string e.g. "drive2:dir2" for the destination
              """
              url = 'http://{host_name}:{port}/sync/copy'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, data={'srcFs': source_remote, 'dstFs': destination_remote, '_async': True})
              jobid = response.json()['jobid']
              if self.job_status(jobid)['error'] != '':
                     raise RcloneCopyDirError(message=response.json(), status_code=response.status_code)
              return (response.status_code, response.headers['X-Rclone-Jobid'])

       def copy(self, source_remote, source_file_path, destination_remote, destination_file_path, copy_flag):
              """    func for copy file or dir      """

              def file_or_dir(source_remote, source_file_path, destination_remote, destination_file_path):
                     try: 
                            status_code, jobid = self.copy_file(source_remote + ':', source_file_path,
                                                         destination_remote + ':', destination_file_path)
                            return (status_code, 'file', jobid) 
                     except RcloneCopyFileError as ef:
                            try:
                                   status_code, jobid = self.copy_dir(source_remote=source_remote + ':' + source_file_path,
                                                               destination_remote=destination_remote + ':' + destination_file_path)
                                   return (status_code, 'dir', jobid)
                            except RcloneCopyDirError as ed:
                                   return (ed.status_code, ['OPERATIONS_ERRORS: ',ef.message, ed.message])

              dst = self.get_remote(remote_name=destination_remote)
              dst_path = destination_file_path[:].split('/')
              dst_path.pop()
              dst_path = '/'.join(dst_path)
              try:
                     res = dst.operations_list(path=dst_path)['list']
              except RcloneListingError as le:
                     return (le.status_code, le.message)
              names = [dir['Name'] for dir in res]
              destination_object_name = destination_file_path.split('/')[-1]

              if destination_object_name in names and copy_flag != CopyCase.rewrite:
                     if copy_flag == CopyCase.create_copy_under_score:
                            destination_object_name = '_' + destination_object_name
                            destination_file_path = os.sep.join([dst_path, destination_object_name]) if dst_path != '' else destination_object_name
                            status_turp = file_or_dir(source_remote, source_file_path,
                                        destination_remote, destination_file_path=destination_file_path)
                            return status_turp
                     elif copy_flag == CopyCase.cancel:
                            return (501, 'Copying was canceled')
              else:
                     if copy_flag == CopyCase.cancel:
                            return (501, 'Copying was canceled')
                     status_turp = file_or_dir(source_remote, source_file_path,
                                        destination_remote, destination_file_path=destination_file_path)
                     return status_turp

       def job_status(self, jobid):
              """
              request Reads the status of the job ID
              """
              url = 'http://{host_name}:{port}/job/status'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, data={'jobid': jobid})
              if response.status_code != 200:
                     raise RcloneJobStatusError(message=response.json(), status_code=response.status_code)
              return response.json()

       def core_stats(self, jobid):
              """
              request Returns stats about current transfers.
              """
              url = 'http://{host_name}:{port}/core/stats'.format(host_name=self.host_name, port=self.port)
              response = requests.post(url, data={'jobid': jobid})
              if response.status_code != 200:
                     raise RcloneJobStatusError(message=response.json(), status_code=response.status_code)
              return response.json()

class RcloneRemote:
       """
              Wrapper class for rclone_http usage
       """
       def __init__(self, host, port, remote_name=None, root_path=''):
              """ """
              self._host = host
              self._port = port
              self.remote_name = remote_name
              self.root_path = root_path
              
       @property
       def host(self):
              return self._host

       @property
       def port(self):
              return self._port

       def operations_list(self, path):
              """
                     --- operation/list command ---
              fs - a remote name string e.g. "drive:"
              remote - a path within that remote e.g. "dir"
              """
              url = 'http://{host_name}:{port}/operations/list'.format(host_name=self.host, port=self.port)
              response = requests.post(url, data={'remote': self.root_path + path.lstrip('/'),'fs': self.remote_name + ':'})
              if response.status_code != 200:
                     raise RcloneListingError(message=response.json()['error'] + ': ' + str(response.json()['input']['remote']), 
                                              status_code=404)#status_code=response.status_code)
              return response.json()

rclone_client = RcloneClient(host_name='rclone', port=8002)