__author__ = 'qweqwe'


class ServingError(Exception):
    """Serving error"""
    message = 'Serving Error'

    def __str__(self):
        return self.formatted_message

class CommandError(ServingError):
    message = "INVALID COMMAND: {0}"

    def __init__(self, command):
        super(CommandError, self).__init__()
        self.command = command
        self.formatted_message = self.message.format(command)


class InvalidCommandError(CommandError):
    pass

class InvalidCommandArgumentError(CommandError):
    message = "INVALID COMMAND ARGUMENT, COMMAND: <{0}>  ARGUMENT {1}"

    def __init__(self, command, argument):
        super(CommandError, self).__init__(command)
        self.command = command
        self.argument = argument
        self.formatted_message = self.message.format(command, argument)


class UnknownCommandError(InvalidCommandError):
    message = "UKNOWN COMMAND: {0}"

class NotaGitCommandError(InvalidCommandError):
    message = "NOT A GIT COMMAND: {0}"

class UnsafeArgumentsError(InvalidCommandArgumentError):
    message = "UNSAFE COMMAND ARGUMENT, COMMAND: {0}  ARGUMENT {1}"



class RepoAccessDeniedError(ServingError):
    message = "Repository {0} doesn't exist"

    def __init__(self, path):
        super(RepoAccessDeniedError, self).__init__()
        self.path = path
        self.formatted_message = self.message.format(path)