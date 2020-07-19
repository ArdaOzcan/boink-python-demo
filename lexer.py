from enum import Enum

from errors import ErrorHandler, UnknownTokenError


class TokenType(Enum):
    """Enum to hold information about a token's type. Derives from Enum class."""

    EOF = 0  # End of file
    NEW_LINE = 1  # \n
    INT_LITERAL = 2  # 0, 1, 2, 123, 314 ...
    FLOAT_LITERAL = 3  # 0.123123, 3.1415, 2.72 ...
    PLUS = 4  # +
    MINUS = 5  # -
    STAR = 6  # *
    SLASH = 7  # /
    AMPERSAND_AMPERSAND = 8  # &&
    PIPE_PIPE = 9  # ||
    WORD = 10  # hello, lol, x, y, z ...
    FUNC_DEF = 11  # fn
    EQUALS = 12  # =
    L_PAR = 13  # (
    R_PAR = 14  # )
    SEMI_COLON = 15  # ;
    DYNAMIC_TYPE = 16  # dyn
    INT_TYPE = 17  # int
    COMMA = 18  # ,
    BOOL_LITERAL = 19  # true, false
    BOOL_TYPE = 20  # bool
    FLOAT_TYPE = 21  # float
    RIGHT_ARROW = 22  # ->
    GIVE = 23  # give
    IF = 24  # if
    GREATER = 25  # >
    GREATER_EQUALS = 26  # >=
    LESS = 27  # <
    LESS_EQUALS = 28  # <=
    EQUALS_EQUALS = 29  # ==


# Dict to hold information about existing keywords and
# the corresponding token type to separate regular words
# (e.g. variable names) from keywords.
KEYWORDS = {"fn": TokenType.FUNC_DEF,
            "dyn": TokenType.DYNAMIC_TYPE,
            "int": TokenType.INT_TYPE,
            "false": TokenType.BOOL_LITERAL,
            "true": TokenType.BOOL_LITERAL,
            "bool": TokenType.BOOL_TYPE,
            "float": TokenType.FLOAT_TYPE,
            "give": TokenType.GIVE,
            "if": TokenType.IF}


class Token:
    """Simple data structure to hold information about a token."""

    def __init__(self, token_type, val, pos):
        """Construct a Token object.

        Args:
            token_type (TokenType): Type of the token.
            val (any): Value of the Token, usually the string that the token refers to.
            pos (int): 1D starting position of the token.
        """

        self.token_type = token_type
        self.val = val
        self.pos = pos

    def __str__(self):
        return f"{self.token_type}, {repr(self.val)}"

    def __repr__(self):
        return self.__str__()


class Lexer:
    """Lexer of the program.

    Lexer loops through every character and converts them to tokens
    or raises errors if an unknown character or character sequence occurs.
    """

    def __init__(self, text, error_handler):
        """Construct a Lexer object.

        Args:
            text (str): Text of the program.
            error_handler (ErrorHandler): Error handler of the program.
        """

        self.text = text
        self.pos = 0
        self.error_handler = error_handler

    def convert_pos_to_line(self, pos):
        """Convert a 1D position to a 2D position that is
        the line number and the offset from the previous newline.

        Args:
            pos (int): 1D position of a character.

        Returns:
            tuple: New 2D position with the line number and offset.
        """

        if pos >= len(self.text):
            return None

        i = 0
        line_count = 0
        offset_to_new_line = 0
        char = self.text[i]
        while i < pos:
            offset_to_new_line += 1
            if char == '\n':
                line_count += 1
                offset_to_new_line = 0
            i += 1
            char = self.text[i]

        return (line_count + 1, offset_to_new_line + 1)

    def get_next_number_token(self):
        """Return the next number (whole or floating) as a token.

        Returns:
            Token: Token of the next number.
        """

        result = ""
        start_pos = self.pos

        while self.current_char() != None and self.current_char().isdigit():
            result += self.current_char()
            self.pos += 1

        if self.current_char() == '.':  # It is a floating number.
            result += self.current_char()
            self.pos += 1

            while self.current_char() != None and self.current_char().isdigit():
                result += self.current_char()
                self.pos += 1

            return Token(TokenType.FLOAT_LITERAL, float(result), start_pos)

        else:
            return Token(TokenType.INT_LITERAL, int(result), start_pos)

    def peek(self, amount=1):
        """Return the character with the offset of amount 
        from the current position. Return None if the character
        is out of range.

        Args:
            amount (int, optional): Offset from the current character. Defaults to 1.

        Returns:
            char: Peeked character.
        """

        if self.pos + amount < len(self.text) - 1:
            return self.text[self.pos + amount]

        return None

    def is_ahead(self, text):
        """Check if a text is ahead from the current character.

        Args:
            text (str): Text to be checked if is ahead.

        Returns:
            bool: If the text is ahead.
        """

        index = 0
        while index < len(text):
            if self.peek(index) != text[index]:
                return False

            index += 1

            if self.peek(index) == None:
                return False

        return True

    def get_next_word_token(self):
        """Get the next word token and separate keywords 
        with regular word.

        Returns:
            Token: The next word token.
        """

        result = ""
        start_pos = self.pos

        while self.current_char() != None and self.current_char().isalpha():
            result += self.current_char()
            self.pos += 1

        if result in KEYWORDS:  # Is a keyword.
            val = result
            if KEYWORDS[result] == TokenType.BOOL_LITERAL:
                val = (result == "true")
                
            return Token(KEYWORDS[result], val, start_pos)

        return Token(TokenType.WORD, result, start_pos)

    def ignore_white_space(self):
        """Pass whitespace until it isn't whitespace."""

        while self.current_char() != None and self.current_char() == ' ':
            self.pos += 1

    def ignore_comment(self):
        """Pass characters until it's newline."""

        while self.current_char() not in ('\n', None):
            self.pos += 1

    def get_next_token(self):
        """Return the next token or call a method that would.
        this method is the entry point for getting the next.

        Returns:
            Token: Token to be returned.
        """

        self.ignore_white_space()
        if self.current_char() == '#':
            self.ignore_comment()
            return self.get_next_token()

        if self.current_char() == None:
            return Token(TokenType.EOF, None, self.pos)

        if self.current_char().isdigit():
            return self.get_next_number_token()

        if self.current_char().isalpha():
            return self.get_next_word_token()

        if self.current_char() == '+':
            token = Token(TokenType.PLUS, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == ',':
            token = Token(TokenType.COMMA, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '-':
            if self.is_ahead('->'):
                start_pos = self.pos
                self.pos += len('->')
                return Token(TokenType.RIGHT_ARROW, '->', start_pos)

            token = Token(TokenType.MINUS, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '*':
            token = Token(TokenType.STAR, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '/':
            token = Token(TokenType.SLASH, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '(':
            token = Token(TokenType.L_PAR, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == ')':
            token = Token(TokenType.R_PAR, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '=':
            if self.is_ahead('=='):
                start_pos = self.pos
                self.pos += len('==')
                return Token(TokenType.EQUALS_EQUALS, '==', start_pos)

            token = Token(TokenType.EQUALS, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == ';':
            token = Token(TokenType.SEMI_COLON, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '\n':
            token = Token(TokenType.NEW_LINE, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '>':
            if self.is_ahead('>='):
                start_pos = self.pos
                self.pos += len('>=')
                return Token(TokenType.GREATER_EQUALS, '>=', start_pos)

            token = Token(TokenType.GREATER, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.current_char() == '<':
            if self.is_ahead('<='):
                start_pos = self.pos
                self.pos += len('<=')
                return Token(TokenType.LESS_EQUALS, '<=', start_pos)

            token = Token(TokenType.LESS, self.current_char(), self.pos)
            self.pos += 1
            return token

        if self.is_ahead('&&'):
            start_pos = self.pos
            self.pos += len('&&')
            return Token(TokenType.AMPERSAND_AMPERSAND, '&&', start_pos)

        if self.is_ahead('||'):
            start_pos = self.pos
            self.pos += len('||')
            return Token(TokenType.PIPE_PIPE, '||', start_pos)

        self.error_handler.error(
            UnknownTokenError(f"Character '{self.current_char()}' is not known",
                              self.pos))

        self.pos += 1
        return self.get_next_token()

    def current_char(self):
        """Get the current char with the current pos.
        Return None if the pos is out of range.

        Returns:
            chr: The character to be returned.
        """

        if self.pos > len(self.text) - 1:
            return None

        return self.text[self.pos]
