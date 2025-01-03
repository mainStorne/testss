class ManagerException(Exception):
    pass


class UserNotFoundException(ManagerException):
    pass

class UploadFileException(ManagerException):
    pass
