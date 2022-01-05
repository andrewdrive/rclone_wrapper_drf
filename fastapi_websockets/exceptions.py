
class RcloneBaseException(BaseException):
       def __init__(self, message, status_code):
              super().__init__(message)
              self.status_code = status_code
              self.message = message

class RcloneCopyFileError(RcloneBaseException):
       pass
class RcloneCopyDirError(RcloneBaseException):
       pass
class RcloneListingError(RcloneBaseException):
       pass
class RcloneJobStatusError(RcloneBaseException):
       pass