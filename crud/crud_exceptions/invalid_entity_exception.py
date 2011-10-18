class InvalidEntityException(Exception):
    """Exception raised when entity is invalid"""
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg
        
