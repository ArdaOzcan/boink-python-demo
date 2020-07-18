import argparse
import os
import sys

from colr import Colr

from errors import ErrorHandler
from interpreter import Interpreter
from lexer import Lexer
from parse import Parser
from symbol_table import *


def main(args):
    """Main entry point for Boink. Apply necessary operations
    with the given arguments.

    Args:
        args (Namespace): Arguments supplied by the user.
    """

    if args.command == 'run':
        try:
            
            with open(args.file, 'r') as file:
                # Extra newline for parsing.
                inp = file.read() + '\n'
                
        except FileNotFoundError:
            
            print(Colr(f"File '{args.file}' not found.", fore="red"))
            return

        # Handler for exceptions during lexing, parsing and semantic analysis.
        error_handler = ErrorHandler()

        lexer_ = Lexer(inp, error_handler)
        
        # Assign lexer to convert positions to line and offset.
        error_handler.lexer = lexer_
        parser_ = Parser(lexer_, error_handler)
        
        # Root node of the program a.k.a. the program itself.
        # Argument is the program name which is equivalent to file's name.
        root = parser_.parse(os.path.basename(args.file))

        parser_.log_tree(root)

        symbol_tree_builder = SymbolTableBuilder(error_handler)
        symbol_tree_builder.visit(root)

        symbol_tree_builder.log_info()

        if not error_handler.errors:
            interpreter_ = Interpreter(root, error_handler)
        else:
            error_handler.log_all()
    else:
        print(Colr(f"Command {repr(args.command)} doesn't exist", fore="red"))
        return


if __name__ == "__main__":
    """Manage arguments for boink command line"""
    
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("command")
    arg_parser.add_argument("file")
    
    main(arg_parser.parse_args())
