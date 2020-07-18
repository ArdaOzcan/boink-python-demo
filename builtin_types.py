from errors import ErrorHandler, IncompatibleTypesError
from lexer import TokenType


def get_type_by_token_type(token_type):
    """Return corresponding type class with a given token type.

    Args:
        token_type (TokenType): Given token type.

    Returns:
        type_: Corresponding type class.
    """

    type_dict = {TokenType.DYNAMIC_TYPE: dyn_,
                 TokenType.INT_TYPE: int_,
                 TokenType.BOOL_TYPE: bool_,
                 TokenType.FLOAT_TYPE: float_}

    return type_dict[token_type]


class type_:
    """Base class for all built-in types"""

    def __init__(self, name, val):
        """Construct a type_ object with a variable name and value.

        Args:
            name (str): Name of the variable.
            val (any): Value of the variable.
        """

        self.name = name
        self.val = val

    @classmethod
    def additionType(cls, other_type, pos):
        """Return the resulting type from a addition operation with 
        this type and other variable's type or raise and error if it
        is not supported.

        Args:
            other_type (type_): Type of the other variable.
            pos (int): Position of the statement to use in errors.
        """

        ErrorHandler.error(IncompatibleTypesError(
            f"{cls} type doesn't support addition", pos))

    @classmethod
    def subtractionType(cls, other_type, pos):
        """Return the resulting type from a subtraction operation with 
        this type and other variable's type or raise and error if it
        is not supported.

        Args:
            other_type (type_): Type of the other variable.
            pos (int): Position of the statement to use in errors.
        """

        ErrorHandler.error(IncompatibleTypesError(
            f"{cls} type doesn't support subtraction", pos))

    @classmethod
    def multiplicationType(cls, other_type, pos):
        """Return the resulting type from a multiplication operation with 
        this type and other variable's type or raise and error if it
        is not supported.

        Args:
            other_type (type_): Type of the other variable.
            pos (int): Position of the statement to use in errors.
        """

        ErrorHandler.error(IncompatibleTypesError(
            f"{cls} type doesn't support multiplication", pos))

    @classmethod
    def divisionType(cls, other_type, pos):
        """Return the resulting type from a division operation with 
        this type and other variable's type or raise and error if it
        is not supported.

        Args:
            other_type (type_): Type of the other variable.
            pos (int): Position of the statement to use in errors.
        """

        ErrorHandler.error(IncompatibleTypesError(
            f"{cls} type doesn't support division", pos))

    @classmethod
    def andType(cls, other_type, pos):
        """Return the resulting type from a and operation with 
        this type and other variable's type or raise and error if it
        is not supported.

        Args:
            other_type (type_): Type of the other variable.
            pos (int): Position of the statement to use in errors.
        """

        ErrorHandler.error(IncompatibleTypesError(
            f"{cls} type doesn't support and operation", pos))

    @classmethod
    def orType(cls, other_type, pos):
        """Return the resulting type from a or operation with 
        this type and other variable's type or raise and error if it
        is not supported.

        Args:
            other_type (type_): Type of the other variable.
            pos (int): Position of the statement to use in errors.
        """

        ErrorHandler.error(IncompatibleTypesError(
            f"{cls} type doesn't support or operation", pos))

    def __str__(self):
        return f"{self.val}"

    __repr__ = __str__


class dyn_(type_):

    def __init__(self, name, val):
        super().__init__(name, val)


class int_(type_):

    def __init__(self, name, val):
        super().__init__(name, val)

    @classmethod
    def additionType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return int_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for addition", pos))

    @classmethod
    def subtractionType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return int_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for subtraction", pos))

    @classmethod
    def multiplicationType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return float_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for multiplication", pos))

    @classmethod
    def divisionType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return float_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for division", pos))


class function_(type_):

    def __init__(self, name, val, args):
        super().__init__(name, val)
        self.args = args

    def call_(self, args):
        pass


class float_(type_):

    def __init__(self, name, val):
        super().__init__(name, val)

    @classmethod
    def additionType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return float_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for addition", pos))

    @classmethod
    def subtractionType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return float_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for subtraction", pos))

    @classmethod
    def multiplicationType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return float_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for multiplication", pos))

    @classmethod
    def divisionType(cls, other_type, pos):
        if other_type == float_:
            return float_
        if other_type == int_:
            return float_

        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for division", pos))


class bool_(type_):

    def __init__(self, name, val):
        super().__init__(name, val)

    @classmethod
    def andType(cls, other_type, pos):
        if other_type == bool_:
            return bool_
        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for and operation", pos))

    @classmethod
    def orType(cls, other_type, pos):
        if other_type == bool_:
            return bool_
        ErrorHandler.error(IncompatibleTypesError(
            f"Types {cls} and {other_type} are not compatible for or operation", pos))
