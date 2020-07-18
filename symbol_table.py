from syntax_tree import ASTVisitor
from builtin_types import *
from errors import *
from parse import TYPE_TOKENS, TokenType
from syntax_tree import *


class Symbol:
    """Base class for symbols."""

    def __init__(self, var_type, name):
        """Construct a Symbol object.

        Args:
            var_type (type_): Type of the variable.
            name (str): Name of the variable.
        """

        self.var_type = var_type
        self.name = name

    def __str__(self):
        return f"{self.var_type} {self.name}"

    __repr__ = __str__


class FunctionSymbol(Symbol):
    """Special symbol for functions."""

    def __init__(self, arg_types, name, give_type):
        """Construct a FunctionSymbol object.

        Args:
            arg_types (list): List of argument types for semantic analysis.
            name (str): Name of the variable.
            give_type (type_) Given type from the function.
        """

        super().__init__(function_, name)

        self.arg_types = arg_types
        self.give_type = give_type

    def __str__(self):
        return f"{self.var_type} {self.arg_types} {self.name}"

    __repr__ = __str__


class VarSymbol(Symbol):
    """Symbol for variables. Same as the base class."""
    pass


class SymbolTable(dict):
    """A symbol table that holds symbols for a certain scope."""

    def __init__(self, scope_name, owner=None, parent_scope=None):
        """Construct a SymbolTable object.

        Args:
            scope_name (str): Name of the scope.
            owner (FunctionSymbol, optional): Owner of this symbol table, a function symbol. Defaults to None.
            parent (SymbolTable, optional): Parent SymbolTable to check outer scopes. Defaults to None.
        """
        super().__init__()

        self.scope_name = scope_name
        self.owner = owner
        self.parent = parent_scope

    def define(self, symbol):
        """Define a new symbol in the symbol table.

        Args:
            symbol (Symbol): Symbol to be defined.
        """

        self[symbol.name] = symbol

    def lookup(self, name):
        """Check the current scope and then the outer scopes.

        If the name is not defined, return None, otherwise
        return the symbol.

        Args:
            name (str): Name of the variable.

        Returns:
            Symbol: Corresponding symbol or None.
        """

        symbol = self.get(name)
        if symbol is None and self.parent is not None:
            symbol = self.parent.lookup(name)
        return symbol

    def lookup_only_current_scope(self, name):
        """Check only the current scope for the name.

        Return None if the name doesn't exists.

        NOTE:   Used for overriding variables.

        Args:
            name (str): Name of the variable.

        Returns:
            Symbol: Corresponding symbol or None.
        """

        symbol = self.get(name)
        return symbol


class SymbolTableBuilder(ASTVisitor):
    """ASTVisitor to do type and definition checking.

    This allows the interpreter to work without type or definition checking.
    """

    def __init__(self, error_handler):
        """Construct a SymbolTableBuilder object.

        Args:
            error_handler (ErrorHandler): Error handler of the program.
        """

        self.logs = []
        self.error_handler = error_handler

    def log_info(self):
        """Log all information stored in the list of logs with header and footer."""

        print("------ Semantic Analysis ----\n")
        for l in self.logs:
            print(l)
        print("\n------------- End -----------")

    def visit_program_syntax(self, node):
        """Create a scope and visit every statement in ProgramSyntax.

        Args:
            node (ProgramSyntax): Syntax node.
        """

        scope = SymbolTable("global")
        self.current_scope = scope

        for s in node.statements:
            self.visit(s)
            self.current_scope = scope

    def visit_function_syntax(self, node):
        """Check for previous definitions, create a FunctionSymbol, 
        create a scope and visit every statement.

        Note:   
            This type of approach requires the user to declare a 
            variable before defining a function.

        Examples:

            <test.boink>
            -----------------------------------------
            1 fn test()
            2    a = 3
            3 ;
            4
            5 int a
            6 test()
            -----------------------------------------

            - ERRORS:  
            - UndefinedSymbolError: Variable 'a' is not defined. Error Position: (2, 4)

            <test.boink>
            -----------------------------------------
            1 int a
            2 fn test()
            3    a = 3
            4 ;
            5 
            6 test()
            -----------------------------------------
            - Works.

        Args:
            node (FunctionSyntax): Syntax node.
        """

        if self.current_scope.lookup(node.name.val) is not None:
            self.error_handler.error(
                MultipleDefinitionError(f"Function {repr(node.name.val)} is already defined",
                                        node.get_pos()))
            return

        arg_types = [a.get_type() for a in node.args]

        give_type = None
        if node.give_type_syntax is not None:
            give_type = get_type_by_token_type(
                node.give_type_syntax.token.token_type
            )

        symbol = FunctionSymbol(arg_types, node.name.val, give_type)
        self.current_scope.define(symbol)
        self.logs.append(
            f"{'DEFINITION':<15}: {symbol} defined in scope {repr(self.current_scope.scope_name)}.")

        scope = SymbolTable(node.name.val, symbol, self.current_scope)
        self.current_scope = scope

        for a in node.args:
            self.visit(a)

        has_give = False
        for s in node.statements:
            if type(s) == GiveSyntax:
                has_give = True

            self.visit(s)
            self.current_scope = scope

        if not has_give and give_type is not None:
            self.error_handler.error(
                NoGiveError(f"Function {repr(node.name.val)} doesn't give any value even though it has a give type of {give_type}",
                              node.get_pos())
            )

    def visit_binary_operation_syntax(self, node):
        """Visit left and right sides of a binary operation.

        Args:
            node (BinaryOperationSyntax): Syntax node.
        """

        self.visit(node.left)
        self.visit(node.right)

    def visit_variable_syntax(self, node):
        """Lookup for a  variable reference and set the variable 
        type of the reference.

        Args:
            node (VariableSyntax): Syntax node.
        """

        symbol = self.current_scope.lookup(node.name)
        if symbol is None:
            self.error_handler.error(UndefinedSymbolError(
                f"Variable '{node.name}' is not defined", node.get_pos()))
            return

        node.var_type = symbol.var_type

    def visit_parenthesized_syntax(self, node):
        """Visit the expression of the syntax.

        Args:
            node (ParenthesizedExpressionSyntax): Syntax node.
        """

        self.visit(node.expr)

    def visit_declaration_syntax(self, node):
        """Check for previous definitions, define a variable in the
        current scope, check types if assigned.

        Args:
            node (DeclarationSyntax): Syntax node.
        """

        var_type = get_type_by_token_type(node.var_type.token.token_type)
        var_symbol = self.current_scope.lookup_only_current_scope(node.name)

        if var_symbol is not None:  # It is already defined in the current scope.
            self.error_handler.error(
                MultipleDefinitionError(f"Variable {repr(node.name)} is already defined",
                                        node.get_pos())
            )
            return

        symbol = VarSymbol(var_type, node.name)
        self.current_scope.define(symbol)
        self.logs.append(
            f"{'DEFINITION':<15}: {symbol} defined in scope {repr(self.current_scope.scope_name)}."
        )

        if node.expr is not None:   # Assigned in decleration.
            self.visit(node.expr)

            if node.expr.get_type() != var_type:    # Type mismatch.
                self.error_handler.error(
                    IncompatibleTypesError(f"Type {node.expr.get_type()} and {var_type} are not compatible for assignment",
                                           node.get_pos())
                )
                return

            self.logs.append(
                f"{'ASSIGNMENT':<15}: Assigned {node.expr.get_type()} to {var_type}."
            )

    def visit_assignment_syntax(self, node):
        """Check types and previous definitions.

        Args:
            node (AssignmentSyntax): Syntax node.
        """

        symbol = self.current_scope.lookup(node.var.name)

        self.visit(node.expr)
        if symbol is None:
            self.error_handler.error(
                UndefinedSymbolError(f"Variable '{node.var.name}' is not defined",
                                     node.var.get_pos())
            )
            return

        if node.expr.get_type() != symbol.var_type:
            self.error_handler.error(
                IncompatibleTypesError(f"Type {node.expr.get_type()} and {symbol.var_type} are not compatible for assignment",
                                       node.get_pos())
            )
            return

        self.logs.append(
            f"{'ASSIGNMENT':<15}: Assigned {node.expr.get_type()} to {symbol.var_type}.")

    def visit_function_call_syntax(self, node):
        """Check types and amounts of arguments.

        Args:
            node (FunctionCall): Syntax node.
        """

        symbol = self.current_scope.lookup(node.var.name)
        if symbol is None:
            self.error_handler.error(
                UndefinedSymbolError(f"Variable '{node.var.name}' is not defined",
                                     node.get_pos())
            )
            return

        node.var_type = symbol.give_type

        for call_arg_type in node.args:
            self.visit(call_arg_type)

        arg_types = [call_arg_type.get_type() for a in node.args]

        if len(arg_types) > len(symbol.arg_types):
            self.error_handler.error(
                ArgumentMismatchError(f"Too many arguments for function call",
                                      node.get_pos())
            )
            return

        elif len(arg_types) < len(symbol.arg_types):
            self.error_handler.error(
                ArgumentMismatchError(f"Too few arguments for function call",
                                      node.get_pos())
            )
            return

        else:
            for call_arg_type, actual_arg_type in zip(arg_types, symbol.arg_types):
                if call_arg_type != actual_arg_type:
                    self.error_handler.error(
                        IncompatibleTypesError(f"Type {call_arg_type} and {actual_arg_type} are not compatible for assignment",
                                               node.get_pos())
                    )
                    return

            self.logs.append(
                f"{'CALL':<15}: Function {symbol.name} called with arguments {symbol.arg_types}")

    def visit_give_syntax(self, node):
        self.visit(node.expr)
        current_function_symbol = self.current_scope.owner
        
        if current_function_symbol is None:
            self.error_handler.error(
                GiveNotAllowedError(f"'give' is not allowed here because it is not inside of a function",
                                       node.get_pos())
            )
            return

        give_type = current_function_symbol.give_type

        if give_type is None:
            self.error_handler.error(
                IncompatibleTypesError(f"'give' is not allowed because function {repr(current_function_symbol.name)} has no return type",
                                       node.get_pos())
            )
            return

        if give_type != node.expr.get_type():
            self.error_handler.error(
                IncompatibleTypesError(f"Type {node.expr.get_type()} and {give_type} are not compatible for giving",
                                       node.get_pos())
            )
