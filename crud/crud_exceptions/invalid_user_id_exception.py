class InvalidUserIdException(Exception):
    """Exception raised when user id is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

