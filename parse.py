"""This module is responsible for parsing the tokens into meaningful syntaxes."""

from errors import Error, ErrorHandler, UnexpectedTokenError
from lexer import Lexer, TokenType
from syntax_tree import *

# Token types that are for type declarations.
# e.g. int, bool, float, dyn
TYPE_TOKENS = {TokenType.DYNAMIC_TYPE,
               TokenType.INT_TYPE,
               TokenType.BOOL_TYPE,
               TokenType.FLOAT_TYPE}

# Token types that are for binary operators
# e.g. +, -, &&, ||
BINARY_OPERATOR_TOKENS = {TokenType.PLUS,
                          TokenType.MINUS,
                          TokenType.AMPERSAND_AMPERSAND,
                          TokenType.PIPE_PIPE}


class Parser:
    """Parser for the program.

    Parser takes tokens from the lexer and converts them to SyntaxNodes.
    That created the tree of SyntaxNodes which creates the program syntax.
    """

    def __init__(self, lexer, error_handler):
        """Construct a Parser object.

        Args:
            lexer (Lexer): Lexer of the program.
            error_handler (ErrorHandler): Error handler of the program.
        """

        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.error_handler = error_handler

    def log_tree(self, root):
        """Log the parse tree with header and ender.

        Args:
            root (SyntaxNode): Root node of the AST.
        """

        print("------- Parsed Program ------\n")
        print(root)
        print("\n------------- End -----------")

    def consume_all(self, token_type):
        """Consume all tokens until it reaches another token type.

        At least one token whose type is the given type is necessary,
        otherwise an error will be thrown.

        Args:
            token_type (TokenType): Requested token type.
        """

        self.consume(token_type)
        while self.current_token.token_type == token_type:
            self.consume(token_type)

    def consume_multiple(self, token_types):
        """Consume a token that can have multiple possible types.

        So a tuple or a list that contains few TokenTypes can be
        passed into this method and if the next token is one of 
        them, it will be consumed, else an error will be thrown.

        Args:
            token_types (container): A container that holds TokenTypes.
        """

        if self.current_token.token_type in token_types:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error_handler.error(
                UnexpectedTokenError(f"Expected one of {token_types} instead of {self.current_token.token_type} {repr(self.current_token.val)}",
                                     self.current_token.pos))

    def consume_optional(self, token_type):
        """Consume a token but don't throw an error if it's not found.

        Args:
            token_type (TokenType): Requested token type.
        """

        if self.current_token.token_type == token_type:
            self.current_token = self.lexer.get_next_token()

    def consume_all_optional(self, token_type):
        """Consume all tokens until it reaches another token type.
        But don't throw an error if it's not found.

        Args:
            token_type (TokenType): Requested TokenType.
        """

        while self.current_token.token_type == token_type:
            self.consume(token_type)

    def consume(self, token_type):
        """Consume the next token if it is found, else throw an error.

        Args:
            token_type (TokenType): Requested TokenType.
        """

        if self.current_token.token_type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error_handler.error(
                UnexpectedTokenError(f"Expected a {token_type} instead of {self.current_token.token_type} {repr(self.current_token.val)}",
                                     self.current_token.pos)
            )
            self.current_token = self.lexer.get_next_token()

    def parse_give(self):
        """Parse a GiveSyntax.

        Returns:
            GiveSyntax: Parsed SyntaxNode.
        """

        token = self.current_token
        self.consume(TokenType.GIVE)
        expr = self.parse_expression()
        return GiveSyntax(token, expr)

    def parse_variable(self):
        """Parse a VariableSyntax.

        Returns:
            VariableSyntax: Parsed SyntaxNode.
        """

        token = self.current_token
        self.consume(TokenType.WORD)
        return VariableSyntax(token)

    def parse_int_literal(self):
        """Parse a IntLiteralSyntax.

        Returns:
            IntLiteralSyntax: Parsed SyntaxNode.
        """

        token = self.current_token
        self.consume(TokenType.INT_LITERAL)
        return IntLiteralSyntax(token)

    def parse_float_literal(self):
        """Parse a IntLiteralSyntax.

        Returns:
            IntLiteralSyntax: Parsed SyntaxNode.
        """

        token = self.current_token
        self.consume(TokenType.FLOAT_LITERAL)
        return FloatLiteralSyntax(token)

    def parse_parenthesized_expression(self):
        """Parse a ParenthesizedSyntax.

        Returns:
            ParenthesizedSyntax: Parsed SyntaxNode.
        """

        self.consume(TokenType.L_PAR)
        expr = self.parse_expression()
        self.consume(TokenType.R_PAR)
        return ParenthesizedSyntax(expr)

    def parse_bool_literal(self):
        """Parse a BoolLiteralSyntax.

        Returns:
            BoolLiteralSyntax: Parsed SyntaxNode.
        """

        token = self.current_token
        self.consume(TokenType.BOOL_LITERAL)
        return BoolLiteralSyntax(token)

    def parse_factor(self):
        """Parse the first part of expression.

        Example:
            -----------------------------------------

            (1 + 2) * 3

            -----------------------------------------

            - Left factor is a ParenthesizedSyntax and the right factor is an IntLiteralSyntax.

        Returns:
            SyntaxNode: The syntax node of the factor.
        """

        token = self.current_token
        if token.token_type == TokenType.MINUS:
            self.consume(TokenType.MINUS)
            return UnaryOperationSyntax(token, self.parse_factor())

        if token.token_type == TokenType.PLUS:
            self.consume(TokenType.PLUS)
            return UnaryOperationSyntax(token, self.parse_factor())

        if token.token_type == TokenType.INT_LITERAL:
            return self.parse_int_literal()

        if token.token_type == TokenType.FLOAT_LITERAL:
            return self.parse_float_literal()

        if token.token_type == TokenType.BOOL_LITERAL:
            return self.parse_bool_literal()

        if token.token_type == TokenType.L_PAR:
            return self.parse_parenthesized_expression()

        if token.token_type == TokenType.WORD:
            var = self.parse_variable()

            if self.current_token.token_type == TokenType.L_PAR:  # Is a function call
                args = self.parse_call_arguments()
                return FunctionCallSyntax(var, args)

            return var

    def parse_term(self):
        """Parse the second part of an expression.

        Example:
            -----------------------------------------

            (1 + 2) * 3

            -----------------------------------------

            - Left factor is a ParenthesizedSyntax and the right factor is an IntLiteralSyntax,
            - So the term is a BinaryOperationSyntax : (ParenthesizedSyntax * IntLiteralSyntax).

        Returns:
            SyntaxNode: Binary operation of factors or just the factor.
        """

        node = self.parse_factor()

        while self.current_token.token_type in (TokenType.STAR, TokenType.SLASH):
            token = self.current_token
            self.consume(token.token_type)
            node = BinaryOperationSyntax(node, token, self.parse_factor())

        return node

    def parse_expression(self):
        """Parse an expression.

        An expression can be an equation or a logic operation.

        Example:
            -----------------------------------------

            1 + (0 * 2.23) - 2
            true && (false || true)

            -----------------------------------------

            - An expression is a binary operation of two terms. (see parse_term)

        Returns:
            SyntaxNode: Binary operation of two terms or just the term.
        """

        node = self.parse_term()

        # BINARY_OPERATOR_TOKENS contain all binary operators as tokens.
        while self.current_token.token_type in BINARY_OPERATOR_TOKENS:
            token = self.current_token
            self.consume(token.token_type)
            node = BinaryOperationSyntax(node, token, self.parse_term())

        return node

    def parse_argument_list(self):
        """Parse an arguments list in a function declaration.

        Example:
            <test.boink>
            -----------------------------------------

            1 fn increment(int a)
            2     int c = a + 1
            3 ;

            -----------------------------------------
            - Return value: [DeclarationSyntax: <int a>]

        Returns:
            list: List of DeclarationSyntaxes.
        """

        self.consume(TokenType.L_PAR)

        args = []
        while True:
            if self.current_token.token_type in TYPE_TOKENS:
                decl = self.parse_declaration()
                args.append(decl)
                if self.current_token.token_type == TokenType.COMMA:
                    self.consume(TokenType.COMMA)
                else:
                    break
            else:
                break

        self.consume(TokenType.R_PAR)
        return args

    def parse_function(self):
        """Parse a function declaration.

        Returns:
            FunctionSyntax: SyntaxNode representation of the parsed function.
        """

        self.consume(TokenType.FUNC_DEF)

        name = self.current_token
        self.consume(TokenType.WORD)

        args = self.parse_argument_list()

        give_type = None
        if self.current_token.token_type == TokenType.RIGHT_ARROW:
            self.consume(TokenType.RIGHT_ARROW)
            give_type = self.parse_type()

        self.consume_all(TokenType.NEW_LINE)

        func = FunctionSyntax(name, give_type)

        statements = self.parse_statements()

        self.consume(TokenType.SEMI_COLON)

        for s in statements:
            func.statements.append(s)

        for a in args:
            func.args.append(a)

        return func

    def parse_type(self):
        """Parse a type name.

        Returns:
            TypeSyntax: SyntaxNode representation of a type name.
        """

        token = None
        if self.current_token.token_type in TYPE_TOKENS:
            token = self.current_token
            self.consume(self.current_token.token_type)
            return TypeSyntax(token)
        else:
            self.error_handler.error(
                UnexpectedTokenError(f"Expected a type token instead of {self.current_token.token_type}: {repr(self.current_token.val)}",
                                     self.current_token.pos))

    def parse_declaration(self):
        """Parse a variable declaration.

        Returns:
            DeclarationSyntax: SyntaxNode representation of a variable declaration.
        """

        var_type = self.parse_type()

        name = self.current_token.val
        self.consume(TokenType.WORD)

        expr = None
        if self.current_token.token_type == TokenType.EQUALS:
            self.consume(TokenType.EQUALS)
            expr = self.parse_expression()

        return DeclarationSyntax(var_type, name, expr)

    def parse_call_arguments(self):
        """Parse arguments of a function call.

        Returns:
            list: List of expressions passed as arguments.
        """

        self.consume(TokenType.L_PAR)

        args = []
        while True:
            if self.current_token.token_type != TokenType.R_PAR:
                var = self.parse_expression()
                args.append(var)
                if self.current_token.token_type == TokenType.COMMA:
                    self.consume(TokenType.COMMA)
                else:
                    break
            else:
                break

        self.consume(TokenType.R_PAR)
        return args

    def parse_statement(self):
        """Parse statement.

        Returns:
            SyntaxNode: SyntaxNode representation of the statement.
        """

        # Is a type name, so a declaration.
        if self.current_token.token_type in TYPE_TOKENS:
            return self.parse_declaration()

        if self.current_token.token_type == TokenType.WORD:  # Is variable name
            var = self.parse_variable()

            if self.current_token.token_type == TokenType.EQUALS:  # Is an assignment
                self.consume(TokenType.EQUALS)
                expr = self.parse_expression()
                return AssignmentSyntax(var, expr)

            if self.current_token.token_type == TokenType.L_PAR:  # Is a call
                args = self.parse_call_arguments()
                return FunctionCallSyntax(var, args)

            self.consume(TokenType.EQUALS)

        if self.current_token.token_type == TokenType.FUNC_DEF:  # Is a function decleration.
            return self.parse_function()

        if self.current_token.token_type == TokenType.GIVE:
            return self.parse_give()

        if self.current_token.token_type == TokenType.IF:
            return self.parse_if()

    def parse_statements(self):
        """Parse a list of statements seperated by newlines

        Returns:
            list: List of statements.
        """

        statements = []
        statement = self.parse_statement()

        if statement == None:
            return statements

        self.consume_all(TokenType.NEW_LINE)

        while True:
            statements.append(statement)
            statement = self.parse_statement()
            if statement == None:
                break
            self.consume_all(TokenType.NEW_LINE)

        return statements

    def parse(self, filename):
        """Entry point of a parser.

        Args:
            filename (str): Name of the file to be given to the program.

        Returns:
            ProgramSyntax: Root node of the AST.
        """

        program = ProgramSyntax(filename)

        self.consume_all_optional(TokenType.NEW_LINE)

        for statement in self.parse_statements():
            program.statements.append(statement)

        self.consume(TokenType.EOF)

        return program

    def parse_if(self):
        """Parse an if statement.

        Returns:
            IfSyntax: SyntaxNode representation of an if statement.
        """

        token = self.current_token

        self.consume(TokenType.IF)
        self.consume(TokenType.L_PAR)

        expr = self.parse_expression()

        self.consume(TokenType.R_PAR)
        self.consume(TokenType.NEW_LINE)

        if_statement = IfSyntax(token, expr)

        statements = self.parse_statements()

        self.consume(TokenType.SEMI_COLON)

        for s in statements:
            if_statement.statements.append(s)

        return if_statement
