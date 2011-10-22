__author__ = 'nik'

class InvalidAppIdException(Exception):
    """Exception raised when application id is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
        
class InvalidDocumentException(Exception):
    """Exception raised when document is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
        
class InvalidUserIdException(Exception):
    """Exception raised when user id is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
    
class InvalidDocumentIdException(Exception):
    """Exception is raised when document id is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg