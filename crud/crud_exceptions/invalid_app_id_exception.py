class InvalidAppIdException(Exception):
    """Exception raised when application id is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
        
