from builtin_types import *
from lexer import TokenType
from utils import camel_to_snake


class ASTVisitor:
    """Abstract Syntax Tree Visitor to traverse in the syntax tree.

    Any class that derives from this can call self.visit with a SyntaxNode
    that calls the corresponding method. There are methods for every SyntaxNode.
    """

    def visit(self, node):
        """Find the corresponding method with a given node
        and call it.

        Args:
            node (SyntaxNode): Node to be visited.

        Returns:
            any: Return value of the actual method.
        """

        camel_case_name = camel_to_snake(node.__class__.__name__)
        method = getattr(self, f"visit_{camel_case_name}")
        return method(node)

    def visit_bool_literal_syntax(self, node):
        pass

    def visit_program_syntax(self, node):
        pass

    def visit_function_syntax(self, node):
        pass

    def visit_binary_operation_syntax(self, node):
        pass

    def visit_variable_syntax(self, node):
        pass

    def visit_parenthesized_syntax(self, node):
        pass

    def visit_declaration_syntax(self, node):
        pass

    def visit_assignment_syntax(self, node):
        pass

    def visit_int_literal_syntax(self, node):
        pass

    def visit_float_literal_syntax(self, node):
        pass

    def visit_function_call_syntax(self, node):
        pass

    def visit_give_syntax(self, node):
        pass


class SyntaxNode:
    """Base class for all syntax node."""

    def get_type(self):
        """Return the type of the syntax if any.

        EXAMPLE:

        -----------------------------------------
        (1 + 2)
        -----------------------------------------
        > BinaryOperationSyntax: <int + int> => get_type(): int

        -----------------------------------------
        (1 / 2)
        -----------------------------------------
        > BinaryOperationSyntax: <int / int> => get_type(): float


        Returns:
            type_: Type of the syntax or None.
        """

        return None

    def get_pos(self):
        """Start position of the syntax.

        Returns:
            int: 1D start position of the syntax node.
        """

        return None


class ProgramSyntax(SyntaxNode):
    """SyntaxNode that represents the program."""

    def __init__(self, name):
        """Construct a ProgramSyntax object.

        Args:
            name (str): Name of the program.
        """

        self.name = name
        self.statements = []

    def get_pos(self):
        return self.statements[0].get_pos()

    def __str__(self):
        raw = ""
        for s in self.statements:
            raw += str(s) + ",\n"

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class GiveSyntax(SyntaxNode):
    def __init__(self, token, expr):
        self.token = token
        self.expr = expr

    def get_pos(self):
        return self.token.pos

    def __str__(self):
        raw = str(self.expr)

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class BinaryOperationSyntax(SyntaxNode):
    """SyntaxNode that represents a binary operation."""

    def __init__(self, left, op, right):
        """Construct a BinaryOperationSyntax object.

        Args:
            left (SyntaxNode): Left side of the binary operation.
            op (Token): Token of the binary operator.
            right (SyntaxNode): Right side of the binary operation.
        """

        self.left = left
        self.op = op
        self.right = right

    def get_pos(self):
        return self.left.get_pos()

    def get_type(self):
        lType = self.left.get_type()
        rType = self.right.get_type()
        pos = self.get_pos()

        if self.op.token_type == TokenType.PLUS:
            return lType.additionType(rType, pos)

        if self.op.token_type == TokenType.MINUS:
            return lType.subtractionType(rType, pos)

        if self.op.token_type == TokenType.STAR:
            return lType.multiplicationType(rType, pos)

        if self.op.token_type == TokenType.SLASH:
            return lType.divisionType(rType, pos)

        if self.op.token_type == TokenType.AMPERSAND_AMPERSAND:
            return lType.andType(rType, pos)

        if self.op.token_type == TokenType.PIPE_PIPE:
            return lType.orType(rType, pos)

    def __str__(self):
        raw = ""
        raw += str(self.left) + ",\n"
        raw += str(self.op) + ",\n"
        raw += str(self.right)

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class TypeSyntax(SyntaxNode):
    """SyntaxNode that represents a type name."""

    def __init__(self, token):
        """Construct a TypeSyntax object.

        Args:
            token (Token): Token of the type name.
        """

        self.token = token

    def get_pos(self):
        return self.token.pos

    def __str__(self):
        return f"{self.__class__.__name__}: {repr(self.token)}"


class DeclarationSyntax(SyntaxNode):
    """SyntaxNode that represents a variable declaration."""

    def __init__(self, var_type, name, expr):
        """Construct a DeclarationSyntax object.

        Args:
            var_type (TypeSyntax): Syntax node of the variable type.
            name (str): Name of the variable.
            expr (SyntaxNode): Value to be assigned to the variable is there is any.
        """

        self.var_type = var_type
        self.name = name
        self.expr = expr

    def get_type(self):
        if self.var_type.token.token_type == TokenType.DYNAMIC_TYPE:
            return dyn_
        elif self.var_type.token.token_type == TokenType.INT_TYPE:
            return int_
        elif self.var_type.token.token_type == TokenType.BOOL_TYPE:
            return bool_
        elif self.var_type.token.token_type == TokenType.FLOAT_TYPE:
            return float_

    def get_pos(self):
        return self.var_type.get_pos()

    def __str__(self):
        raw = ""
        raw += str(self.var_type) + ",\n"
        raw += str(self.name) + ",\n"
        if self.expr is not None:
            raw += str(self.expr)

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class IntLiteralSyntax(SyntaxNode):
    """SyntaxNode that represents an integer literal."""

    def __init__(self, token):
        """Construct an IntLiteralSyntax object.

        Args:
            token (Token): Token of the int literal.
        """

        self.token = token
        self.val = token.val

    def get_pos(self):
        return self.token.pos

    def get_type(self):
        return int_

    def __str__(self):
        return f"{self.__class__.__name__}: {self.val}"


class FloatLiteralSyntax(SyntaxNode):
    """SyntaxNode that represents a float literal."""

    def __init__(self, token):
        """Construct an FloatLiteralSyntax object.

        Args:
            token (Token): Token of the float literal.
        """

        self.token = token
        self.val = token.val

    def get_pos(self):
        return self.token.pos

    def get_type(self):
        return float_

    def __str__(self):
        return f"{self.__class__.__name__}: {self.val}"


class BoolLiteralSyntax(SyntaxNode):
    """SyntaxNode that represents a bool literal."""

    def __init__(self, token):
        """Construct an BoolLiteralSyntax object.

        Args:
            token (Token): Token of the bool literal.
        """

        self.token = token
        self.val = token.val

    def get_pos(self):
        return self.token.pos

    def get_type(self):
        return bool_

    def __str__(self):
        return f"{self.__class__.__name__}: {self.val}"


class UnaryOperationSyntax(SyntaxNode):
    """SyntaxNode that represents a unary operation."""

    def __init__(self, op, expr):
        """Construct a UnaryOperationSyntax object.

        Args:
            op (Token): Operator token.
            expr (SyntaxNode): Expression as a syntax node.
        """

        self.op = op
        self.expr = expr

    def get_pos(self):
        return self.op.pos

    def get_type(self):
        return self.expr.get_type()

    def __str__(self):
        return f"{self.__class__.__name__}: {self.op} {self.expr}"


class AssignmentSyntax(SyntaxNode):
    """SyntaxNode that represents an variable assignment."""

    def __init__(self, var, expr):
        """Construct an AssignmentSyntax object.

        Args:
            var (VariableSyntax): Variable reference as a SyntaxNode.
            expr (SyntaxNode): Expression as a SyntaxNode.
        """

        self.var = var
        self.expr = expr

    def get_pos(self):
        return self.var.get_pos()

    def __str__(self):
        raw = ""
        raw += str(self.var) + "\n=\n"
        raw += str(self.expr)

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class VariableSyntax(SyntaxNode):
    """SyntaxNode that represents a variable reference."""

    def __init__(self, token):
        """Construct a VariableSyntax object.

        Args:
            token (Token): Token of the variable name.
        """

        self.token = token
        self.name = token.val

        # Set by SymbolTableBuilder.
        self.var_type = None

    def get_pos(self):
        return self.token.pos

    def get_type(self):
        return self.var_type

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"


class ParenthesizedSyntax(SyntaxNode):
    """SyntaxNode that represents a parenthesized expression."""

    def __init__(self, expr):
        """Construct a ParenthesizedSyntax object.

        Args:
            expr (SyntaxNode): Expression as a SyntaxNode.
        """

        self.expr = expr

    def get_pos(self):
        return self.expr.get_pos() - 1

    def get_type(self):
        return self.expr.get_type()

    def __str__(self):
        raw = str(self.expr)

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class FunctionSyntax(SyntaxNode):
    """SyntaxNode that represents a function declaration."""

    def __init__(self, name, give_type_syntax):
        """Construct a FunctionSyntax object.

        Args:
            name (Token): Name token of the function.
            give_type_syntax (TypeSyntax): Given type from the function.
        """

        self.name = name
        self.give_type_syntax = give_type_syntax
        self.statements = []
        self.args = []

    def get_pos(self):
        return self.name.pos

    def __str__(self):
        raw = ""
        raw += "Name: " + self.name.val + ",\n"

        raw += "Arguments: [\n"
        for a in self.args:
            raw += str(a) + ",\n"
        raw += "],\n"

        raw += "Statements: [\n"
        for s in self.statements:
            raw += str(s) + ",\n"
        raw += "],\n"

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"


class FunctionCallSyntax(SyntaxNode):
    """SyntaxNode that represents a function call."""

    def __init__(self, var, args):
        """Construct a FunctionCallSyntax object.

        Args:
            var (VariableSyntax): Function reference as a VariableSyntax.
            args (list): List of expressions passed as arguments.
        """

        self.var = var
        self.args = args
        self.var_type = None

    def get_pos(self):
        return self.var.token.pos

    def get_type(self):
        print("Type requested", self.var_type)
        return self.var_type

    def __str__(self):
        raw = ""
        raw += "Name: " + self.var.name + ",\n"

        raw += "Arguments: [\n"
        for a in self.args:
            raw += str(a) + ",\n"
        raw += "],\n"

        indented = ""
        for l in raw.splitlines():
            indented += "    " + l + "\n"

        return f"{self.__class__.__name__}: {{\n{indented}}}"
