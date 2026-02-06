"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK - The Verified General-Purpose Programming Language

A Turing-complete language built on Newton's verified computation architecture.
Every loop bounded. Every operation traced. Every output proven.

The constraint IS the instruction.
The verification IS the computation.
The trace IS the proof.
═══════════════════════════════════════════════════════════════════════════════
"""

__version__ = "1.0.0"
__author__ = "Newton Supercomputer"

from .kernel import TinyTalkKernel, ExecutionBounds, Trace, Ledger, fin, finfr
from .lexer import Lexer, Token, TokenType
from .parser import Parser, Program, Literal, Identifier, BinaryOp, UnaryOp
from .types import Value, ValueType, TinyType, TypeChecker
from .runtime import Runtime, Scope, TinyFunction, TinyTalkError
from .ffi import (
    FFIConfig, configure_ffi, 
    to_python, from_python, wrap_python_function,
    import_python, import_builtin, import_external,
    call_javascript, call_go, call_rust, call_shell,
    http_get, http_post
)
from .stdlib import STDLIB_FUNCTIONS, STDLIB_CONSTANTS

__all__ = [
    # Kernel
    'TinyTalkKernel',
    'ExecutionBounds',
    'Trace',
    'Ledger',
    'fin',
    'finfr',
    
    # Lexer
    'Lexer',
    'Token',
    'TokenType',
    
    # Parser
    'Parser',
    'Program',
    'Literal',
    'Identifier',
    'BinaryOp',
    'UnaryOp',
    
    # Types
    'Value',
    'ValueType',
    'TinyType',
    'TypeChecker',
    
    # Runtime
    'Runtime',
    'Scope',
    'TinyFunction',
    'TinyTalkError',
    
    # FFI
    'FFIConfig',
    'configure_ffi',
    'to_python',
    'from_python',
    'wrap_python_function',
    'import_python',
    'import_builtin',
    'import_external',
    'call_javascript',
    'call_go',
    'call_rust',
    'call_shell',
    'http_get',
    'http_post',
    
    # Stdlib
    'STDLIB_FUNCTIONS',
    'STDLIB_CONSTANTS',
]


def run(source: str, bounds: ExecutionBounds = None) -> Value:
    """Run TinyTalk source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    runtime = Runtime(bounds)
    return runtime.execute(ast)


def repl():
    """Start TinyTalk REPL."""
    print("TinyTalk v1.0.0 - Verified Computation")
    print("Type 'exit' to quit, 'help' for help")
    print()
    
    runtime = Runtime()
    
    while True:
        try:
            line = input(">>> ")
            if line.strip() == 'exit':
                break
            if line.strip() == 'help':
                print("TinyTalk is a verified programming language.")
                print("Built-in functions: print, len, type, range, etc.")
                print("Import Python: import @math")
                continue
            
            if not line.strip():
                continue
            
            result = run(line)
            if result.type != ValueType.NULL:
                print(result)
                
        except TinyTalkError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted")
        except EOFError:
            break
    
    print("Goodbye!")
