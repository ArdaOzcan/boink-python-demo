"""This module is responsible for interpreting Boink code."""

from copy import deepcopy

from syntax_tree import ASTVisitor, GiveSyntax
from builtin_types import *
from lexer import TokenType


class ActivationRecord:
    """Temporary memory of a procedure (program, function). Also contains information
    about the activation/call of a procedure.

    Nesting level of the call to the procedure is the depth of the
    call e.g. a program's nesting level is 1. Parent record is the 
    caller of this procedure. A program procedure's parent record 
    is None and a function called in the global scope has the program
    for parent record. This way the interpreter can check the parent's 
    memory to find some variables that were not declared in its scope.

    Example:
        <test.boink>
        -----------------------------------------

        1 fn increment(int a)
        2     int c = a + 1
        3 ;
        4 
        5 increment(1)

        -----------------------------------------

        - ------- END OF FUNCTION increment -------
        - CALL STACK
        - 2: increment            ---> Activation record for increment call in line 5.
        - a              : 1
        - c              : 2
        - 1: test.boink           ---> Activation record for the program.
        - increment      : [<syntax_tree.DeclarationSyntax object at 0x0395E970>]

    """

    def __init__(self, name, nesting_level, parent_record):
        """Construct an ActivationRecord object.

        Args:
            name (str): Name of the procedure that is called.
            nesting_level (int): Nesting level of the activation.
            parent_record (ActivationRecord): Caller of the activation.
        """

        self.name = name
        self.nesting_level = nesting_level
        self.parent_record = parent_record
        self.members = {}

    def __setitem__(self, key, value):
        """Set a variable

        Args:
            key (str): Name of the variable.
            value (any): Value of the variable.
        """

        self.members[key] = value

    def __getitem__(self, key):
        """Access a variable in memory.

        This method first checks for the current activation record 
        a.k.a. the local variables. But if the name doesn't exists
        in the local scope, the method asks for the parent record
        to search for the given name. If a variable actually exists
        in the nonlocal or global scope, it deepcopies the variable
        so change in value doesn't effect the outer scope.

        NOTE: If the variable doesn't exists, Boink would've caught it
              during semantic analysis (class SymbolTableBuilder) so if
              it throws a KeyError, something is wrong in SymbolTableBuilder.

        Args:
            key (str): Name of the variable.

        Returns:
            type_: Variable.
        """

        current_scope = self.members.get(key)
        if current_scope is None:
            if self.parent_record is not None:
                var_in_parent = self.parent_record[key]
                self.members[key] = deepcopy(var_in_parent)
                return self.members[key]
            else:
                # Shouldn't come here if SymbolTableBuilder works.
                self.members[key]
        else:
            return current_scope

    # def get(self, key):
    #     return self.members.get(key)

    def __str__(self):
        lines = [
            f"{self.nesting_level}: {self.name}"
        ]

        for name, val in self.members.items():
            lines.append(f"   {name:<15}: {val}")

        s = "\n".join(lines)
        return s

    __repr__ = __str__


class CallStack:
    """Simple data structure to keep track of activation records."""

    def __init__(self):
        """Construct a CallStack object."""

        self._records = []

    def push(self, ar):
        """Add a activation record to the call stack.

        Args:
            ar (ActivationRecrod): Record to add.
        """

        self._records.append(ar)

    def pop(self):
        """Remove a record from the end of the call stack.

        Returns:
            ActivationRecrod: Removed record.
        """

        return self._records.pop()

    def peek(self):
        """Return the last element of the call stack.

        Returns:
            ActivationRecord: The last activation record.
        """

        return self._records[-1]

    def __str__(self):
        s = "\n".join(repr(ar) for ar in reversed(self._records))
        s = f"CALL STACK\n{s}\n"
        return s

    __repr__ = __str__


class Interpreter(ASTVisitor):
    """Interpreter of the program. Derives from ASTVisitor."""

    def __init__(self, root, error_handler):
        """Construct an Interpreter object.

        Args:
            root (SyntaxNode): Root node of the program a.k.a. the program itself.
            error_handler (ErrorHandler): Error handler of the interpreter.
        """

        super().__init__()

        self.error_handler = error_handler
        self.call_stack = CallStack()

        # Start the tree traversal with the root, a ProgramSyntax.
        self.visit(root)

    def visit_program_syntax(self, node):
        """Create an ActivationRecord and visit every statement.

        Args:
            node (ProgramSyntax): Syntax node.
        """

        program_name = node.name

        ar = ActivationRecord(
            name=program_name,
            nesting_level=1,
            parent_record=None
        )

        self.call_stack.push(ar)
        print(f"------- START OF FUNCTION {program_name} -------")
        print(self.call_stack)

        for s in node.statements:
            self.visit(s)

        print(f"-------- END OF FUNCTION {program_name} --------")
        print(self.call_stack)

        self.call_stack.pop()

    def visit_declaration_syntax(self, node):
        """Visit expression if there is any and define a variable
        in the activation record.

        Args:
            node (DeclerationSyntax): Syntax node.
        """

        var_type = get_type_by_token_type(node.var_type.token.token_type)

        val = None
        if node.expr is not None:
            val = self.visit(node.expr)

        ar = self.call_stack.peek()
        ar[node.name] = var_type(node.name, val)

    def visit_function_call_syntax(self, node):
        """Create an activation record, set arguments and visit 
        every statement.

        Args:
            node (FunctionCallSyntax): Syntax node.
        """

        func_name = node.var.name
        parent_record = self.call_stack.peek()

        ar = ActivationRecord(
            name=func_name,
            nesting_level=parent_record.nesting_level + 1,
            parent_record=parent_record
        )

        func_symbol = self.call_stack.peek()[node.var.name]
        arg_decls = func_symbol.args
        passed_args = node.args

        for arg_decl, passed_arg in zip(arg_decls, passed_args):
            token_type = arg_decl.var_type.token.token_type
            var_type = get_type_by_token_type(token_type)
            ar[arg_decl.name] = var_type(arg_decl.name, self.visit(passed_arg))

        self.call_stack.push(ar)
        print(f"------- START OF FUNCTION {func_name} -------")
        print(self.call_stack)

        give_value = None
        for s in func_symbol.val:
            if type(s) == GiveSyntax:
                give_value = self.visit(s)
                break

            self.visit(s)

        print(f"-------- END OF FUNCTION {func_name} --------")
        print(self.call_stack)

        self.call_stack.pop()
        return give_value

    def visit_function_syntax(self, node):
        """Define a function in the last activation record.

        Args:
            node (FunctionSyntax): Syntax node.
        """

        ar = self.call_stack.peek()
        ar[node.name.val] = function_(
            node.name.val, node.statements, node.args)

    def visit_give_syntax(self, node):
        return self.visit(node.expr)

    def visit_variable_syntax(self, node):
        """Get the variable and return the value.

        Args:
            node (VariableSyntax): Syntax node.

        Returns:
            any: Value of the variable.
        """

        varName = node.name

        ar = self.call_stack.peek()
        var = ar[varName]

        return var.val

    def visit_binary_operation_syntax(self, node):
        """Visit both the left and right side and return the
        evaluated version.

        Args:
            node (BinaryOperationSyntax): Syntax node.

        Returns:
            any: Evaluated expression.
        """

        left, right = self.visit(node.left), self.visit(node.right)

        if node.op.token_type == TokenType.PLUS:
            return left + right

        if node.op.token_type == TokenType.MINUS:
            return left - right

        if node.op.token_type == TokenType.STAR:
            return left * right

        if node.op.token_type == TokenType.SLASH:
            return left / right

        if node.op.token_type == TokenType.AMPERSAND_AMPERSAND:
            return left and right

        if node.op.token_type == TokenType.PIPE_PIPE:
            return left or right

    def visit_assignment_syntax(self, node):
        """Get the variable and set the value.

        Args:
            node (AssignmentSyntax): Syntax node.
        """

        var_name = node.var.name
        var_value = self.visit(node.expr)

        ar = self.call_stack.peek()
        var = ar[var_name]
        var.val = var_value

    def visit_int_literal_syntax(self, node):
        """Return the int value.

        Args:
            node (IntLiteralSyntax): Syntax node.

        Returns:
            int: Value of the literal.
        """

        return node.val

    def visit_float_literal_syntax(self, node):
        """Return the float value.

        Args:
            node (FloatLiteralSyntax): Syntax node.

        Returns:
            float: Value of the literal.
        """

        return node.val

    def visit_bool_literal_syntax(self, node):
        """Return the bool value.

        Args:
            node (BoolLiteralSyntax): Syntax node.

        Returns:
            bool: Value of the literal.
        """

        return node.val
