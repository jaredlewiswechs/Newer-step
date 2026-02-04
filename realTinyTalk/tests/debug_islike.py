#!/usr/bin/env python3
"""Debug islike transpilation"""

import sys
sys.path.insert(0, 'c:/Users/jnlew/Newton-api')

from realTinyTalk.lexer import Lexer
from realTinyTalk.parser import Parser
from realTinyTalk.backends.js.emitter import JSEmitter
from realTinyTalk.backends.python.emitter import PythonEmitter

codes = [
    'show("test" islike "t*")',
    'show("hello.txt" islike "*.txt")',
    '"test" islike "t*"',
]

for code in codes:
    print("=" * 60)
    print("Code:", code)
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    for stmt in ast.statements:
        print(f"  Statement: {type(stmt).__name__}")
        
        def walk_node(node, depth=2):
            indent = "  " * depth
            name = type(node).__name__
            if hasattr(node, 'op'):
                print(f"{indent}{name} op={repr(node.op)}")
            elif hasattr(node, 'value'):
                print(f"{indent}{name} value={repr(node.value)}")
            else:
                print(f"{indent}{name}")
            
            for attr in ['left', 'right', 'args', 'callee', 'operand']:
                if hasattr(node, attr):
                    val = getattr(node, attr)
                    if val is None:
                        continue
                    if isinstance(val, list):
                        for i, item in enumerate(val):
                            walk_node(item, depth + 1)
                    else:
                        walk_node(val, depth + 1)
        
        walk_node(stmt)
    
    # Emit
    js_emitter = JSEmitter(include_runtime=False)
    js = js_emitter.emit(ast)
    print(f"  JS: {js}")
    
    py_emitter = PythonEmitter(include_runtime=False)
    py = py_emitter.emit(ast)
    print(f"  PY: {py}")
    print()
