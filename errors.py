import sys
import threading

from colr import Colr


class Error:
    """Base class for all errors."""

    def __init__(self, msg, pos):
        """Construct an Error object.

        Args:
            msg (str): Message of the error.
            pos (int): 1D position of the error.
        """

        self.msg = msg
        self.pos = pos

# Builtin errors


class UnexpectedTokenError(Error):
    pass


class UnknownTokenError(Error):
    pass


class UndefinedSymbolError(Error):
    pass


class MultipleDefinitionError(Error):
    pass


class IncompatibleTypesError(Error):
    pass


class ArgumentMismatchError(Error):
    pass


class NotGivenError(Error):
    pass


class GiveNotAllowedError(Error):
    pass


class ErrorHandler:
    """Data structure to hold a list of errors."""

    def __init__(self):
        """Construct an ErrorHandler."""

        self.errors = []

    def error(self, err):
        """Add an error to the list.

        Args:
            err (Error): Error to be added.
        """

        self.errors.append(Colr(
            f"{err.__class__.__name__}: {err.msg}. Error Position: {self.lexer.convert_pos_to_line(err.pos)}",
            fore="red",
            style="bold"))

    def log_all(self):
        """Log all errors in the list with a header."""

        print(Colr("ERRORS: ", fore="red", style="bold"))

        for err in self.errors:
            print(err)
