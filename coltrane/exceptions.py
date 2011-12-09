__author__ = 'qweqwe'

class AppException(Exception):
    def __init__(self, message=None, *args, **kwargs):
        super(AppException, self).__init__(*args)
        if message:
            if  kwargs:
                self.message = message.format(**kwargs)
            else:
                self.message = message
        elif kwargs:
            if not self.message:
                raise RuntimeError("Formatting message before specifing the message itself")
            self.message = self.message.format(**kwargs)

    def __str__(self):
        return self.message
