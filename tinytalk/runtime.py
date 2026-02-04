"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK RUNTIME
Verified execution with bounded computation

Every step is traced. Every result is verified.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Tuple
import time

from .kernel import ExecutionBounds, Trace, Ledger, fin, finfr
from .types import Value, ValueType, TinyType
from .parser import (
    Program, Literal, Identifier, BinaryOp, UnaryOp, Call, Index, Member,
    Array, MapLiteral, Lambda, Conditional, Range, Pipe, LetStmt, ConstStmt,
    Block, IfStmt, ForStmt, WhileStmt, ReturnStmt, BreakStmt, ContinueStmt,
    FnDecl, StructDecl, EnumDecl, ImportStmt, MatchStmt, TryStmt, ThrowStmt,
    AssignStmt
)


class BreakException(Exception):
    """Break out of loop."""
    pass


class ContinueException(Exception):
    """Continue to next iteration."""
    pass


class ReturnException(Exception):
    """Return from function."""
    def __init__(self, value: Value):
        self.value = value


class TinyTalkError(Exception):
    """Runtime error."""
    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


# ═══════════════════════════════════════════════════════════════════════════════
# SCOPE
# ═══════════════════════════════════════════════════════════════════════════════

class Scope:
    """Variable scope with parent chain."""
    
    def __init__(self, parent: Optional['Scope'] = None):
        self.parent = parent
        self.variables: Dict[str, Value] = {}
        self.constants: set = set()
    
    def define(self, name: str, value: Value, const: bool = False):
        """Define a new variable in this scope."""
        self.variables[name] = value
        if const:
            self.constants.add(name)
    
    def get(self, name: str) -> Optional[Value]:
        """Get a variable, searching parent scopes."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def set(self, name: str, value: Value) -> bool:
        """Set a variable, searching parent scopes."""
        if name in self.variables:
            if name in self.constants:
                raise TinyTalkError(f"Cannot reassign constant '{name}'")
            self.variables[name] = value
            return True
        if self.parent:
            return self.parent.set(name, value)
        return False
    
    def has(self, name: str) -> bool:
        """Check if variable exists."""
        if name in self.variables:
            return True
        if self.parent:
            return self.parent.has(name)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TinyFunction:
    """A TinyTalk function."""
    name: str
    params: List[Tuple[str, Optional[str]]]  # (name, type_hint)
    body: Any  # AST node
    closure: Scope
    is_native: bool = False
    native_fn: Optional[Callable] = None


@dataclass
class TinyStruct:
    """A TinyTalk struct definition."""
    name: str
    fields: List[Tuple[str, Optional[str], Optional[Any]]]  # (name, type, default)


@dataclass
class TinyEnum:
    """A TinyTalk enum definition."""
    name: str
    variants: Dict[str, Optional[Any]]  # variant_name -> associated_data


@dataclass
class StructInstance:
    """Instance of a struct."""
    struct: TinyStruct
    fields: Dict[str, Value]


@dataclass
class EnumVariant:
    """Instance of an enum variant."""
    enum_name: str
    variant_name: str
    data: Optional[Value] = None


# ═══════════════════════════════════════════════════════════════════════════════
# RUNTIME
# ═══════════════════════════════════════════════════════════════════════════════

class Runtime:
    """
    TinyTalk runtime interpreter.
    
    Executes AST with bounded computation and full tracing.
    """
    
    def __init__(self, bounds: Optional[ExecutionBounds] = None):
        self.bounds = bounds or ExecutionBounds()
        self.global_scope = Scope()
        self.structs: Dict[str, TinyStruct] = {}
        self.enums: Dict[str, TinyEnum] = {}
        self.ledger = Ledger()
        self.traces: List[Trace] = []  # List of traces instead of single Trace
        
        # Execution metrics
        self.op_count = 0
        self.iteration_count = 0
        self.recursion_depth = 0
        self.start_time = 0.0
        
        # Register builtins
        self._register_builtins()
    
    def _register_builtins(self):
        """Register built-in functions."""
        from . import stdlib
        
        builtins = {
            'print': stdlib.builtin_print,
            'println': stdlib.builtin_println,
            'len': stdlib.builtin_len,
            'type': stdlib.builtin_type,
            'str': stdlib.builtin_str,
            'int': stdlib.builtin_int,
            'float': stdlib.builtin_float,
            'bool': stdlib.builtin_bool,
            'list': stdlib.builtin_list,
            'map': stdlib.builtin_map,
            'range': stdlib.builtin_range,
            'sum': stdlib.builtin_sum,
            'min': stdlib.builtin_min,
            'max': stdlib.builtin_max,
            'abs': stdlib.builtin_abs,
            'round': stdlib.builtin_round,
            'floor': stdlib.builtin_floor,
            'ceil': stdlib.builtin_ceil,
            'sqrt': stdlib.builtin_sqrt,
            'pow': stdlib.builtin_pow,
            'sin': stdlib.builtin_sin,
            'cos': stdlib.builtin_cos,
            'tan': stdlib.builtin_tan,
            'log': stdlib.builtin_log,
            'exp': stdlib.builtin_exp,
            'input': stdlib.builtin_input,
            'split': stdlib.builtin_split,
            'join': stdlib.builtin_join,
            'append': stdlib.builtin_append,
            'pop': stdlib.builtin_pop,
            'push': stdlib.builtin_push,
            'keys': stdlib.builtin_keys,
            'values': stdlib.builtin_values,
            'contains': stdlib.builtin_contains,
            'slice': stdlib.builtin_slice,
            'reverse': stdlib.builtin_reverse,
            'sort': stdlib.builtin_sort,
            'filter': stdlib.builtin_filter,
            'map_': stdlib.builtin_map_fn,
            'reduce': stdlib.builtin_reduce,
            'zip': stdlib.builtin_zip,
            'enumerate': stdlib.builtin_enumerate,
            'assert': stdlib.builtin_assert,
            'typeof': stdlib.builtin_typeof,
            'hash': stdlib.builtin_hash,
        }
        
        for name, fn in builtins.items():
            self.global_scope.define(
                name,
                Value.function_val(TinyFunction(name, [], None, self.global_scope, True, fn)),
                const=True
            )
    
    def execute(self, ast) -> Value:
        """Execute an AST and return result."""
        self.op_count = 0
        self.iteration_count = 0
        self.recursion_depth = 0
        self.start_time = time.time()
        self.traces = []
        
        try:
            result = self._eval(ast, self.global_scope)
            self.traces.append(Trace.t("execute", True, {"result": str(result)}))
            return result
        except ReturnException as e:
            self.traces.append(Trace.t("return", True, {"value": str(e.value)}))
            return e.value
        except (BreakException, ContinueException):
            raise TinyTalkError("Break/continue outside of loop")
    
    def _check_bounds(self):
        """Check execution bounds."""
        self.op_count += 1
        
        if self.op_count > self.bounds.max_ops:
            raise TinyTalkError(f"Exceeded maximum operations ({self.bounds.max_ops})")
        
        elapsed = time.time() - self.start_time
        if elapsed > self.bounds.timeout_seconds:
            raise TinyTalkError(f"Exceeded timeout ({self.bounds.timeout_seconds}s)")
    
    def _eval(self, node, scope: Scope) -> Value:
        """Evaluate an AST node."""
        self._check_bounds()
        
        # Program
        if isinstance(node, Program):
            result = Value.null_val()
            for stmt in node.statements:
                result = self._eval(stmt, scope)
            return result
        
        # Literals
        if isinstance(node, Literal):
            return self._eval_literal(node)
        
        # Identifier
        if isinstance(node, Identifier):
            val = scope.get(node.name)
            if val is None:
                raise TinyTalkError(f"Undefined variable '{node.name}'", node.line)
            return val
        
        # Binary operations
        if isinstance(node, BinaryOp):
            return self._eval_binary(node, scope)
        
        # Unary operations
        if isinstance(node, UnaryOp):
            return self._eval_unary(node, scope)
        
        # Function call
        if isinstance(node, Call):
            return self._eval_call(node, scope)
        
        # Index access
        if isinstance(node, Index):
            return self._eval_index(node, scope)
        
        # Member access
        if isinstance(node, Member):
            return self._eval_member(node, scope)
        
        # Array literal
        if isinstance(node, Array):
            elements = [self._eval(el, scope) for el in node.elements]
            return Value.list_val(elements)
        
        # Map literal
        if isinstance(node, MapLiteral):
            pairs = {}
            for key, val in node.pairs:
                k = self._eval(key, scope)
                v = self._eval(val, scope)
                # Use Python-hashable key
                pairs[k.to_python()] = v
            return Value.map_val(pairs)
        
        # Lambda
        if isinstance(node, Lambda):
            params = [(p, None) for p in node.params]
            return Value.function_val(TinyFunction("<lambda>", params, node.body, scope))
        
        # Conditional (ternary)
        if isinstance(node, Conditional):
            cond = self._eval(node.condition, scope)
            if cond.is_truthy():
                return self._eval(node.then_expr, scope)
            else:
                return self._eval(node.else_expr, scope)
        
        # Range
        if isinstance(node, Range):
            start = self._eval(node.start, scope)
            end = self._eval(node.end, scope)
            
            items = []
            i = start.data
            end_val = end.data + 1 if node.inclusive else end.data
            while i < end_val:
                items.append(Value.int_val(i))
                i += 1
            return Value.list_val(items)
        
        # Pipe
        if isinstance(node, Pipe):
            # x |> f  becomes  f(x)
            left = self._eval(node.left, scope)
            
            # Right side must be callable or a call
            if isinstance(node.right, Call):
                # Insert left as first argument
                fn = scope.get(node.right.callee.name) if isinstance(node.right.callee, Identifier) else self._eval(node.right.callee, scope)
                args = [left] + [self._eval(a, scope) for a in node.right.args]
                return self._call_function(fn.data, args, scope, node.line)
            elif isinstance(node.right, Identifier):
                fn = scope.get(node.right.name)
                if fn is None:
                    raise TinyTalkError(f"Undefined function '{node.right.name}'", node.line)
                return self._call_function(fn.data, [left], scope, node.line)
            else:
                fn = self._eval(node.right, scope)
                return self._call_function(fn.data, [left], scope, node.line)
        
        # Let statement
        if isinstance(node, LetStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            scope.define(node.name, val, const=False)
            return val
        
        # Const statement
        if isinstance(node, ConstStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            scope.define(node.name, val, const=True)
            return val
        
        # Assignment statement
        if isinstance(node, AssignStmt):
            val = self._eval(node.value, scope)
            
            if isinstance(node.target, Identifier):
                if node.op == '=':
                    if not scope.set(node.target.name, val):
                        scope.define(node.target.name, val)
                else:
                    # Compound assignment
                    old_val = scope.get(node.target.name)
                    op = node.op[:-1]  # Remove '=' from '+=', '-=', etc.
                    new_val = self._apply_op(old_val, val, op, node.line)
                    scope.set(node.target.name, new_val)
                    return new_val
            elif isinstance(node.target, Index):
                container = self._eval(node.target.obj, scope)
                index = self._eval(node.target.index, scope)
                if container.type == ValueType.LIST:
                    container.data[int(index.data)] = val
                elif container.type == ValueType.MAP:
                    container.data[index.to_python()] = val
            elif isinstance(node.target, Member):
                obj = self._eval(node.target.obj, scope)
                if obj.type == ValueType.STRUCT_INSTANCE:
                    obj.data.fields[node.target.field] = val
                elif obj.type == ValueType.MAP:
                    obj.data[node.target.field] = val
            return val
        
        # Block
        if isinstance(node, Block):
            block_scope = Scope(scope)
            result = Value.null_val()
            for stmt in node.statements:
                result = self._eval(stmt, block_scope)
            return result
        
        # If statement
        if isinstance(node, IfStmt):
            return self._eval_if(node, scope)
        
        # For loop
        if isinstance(node, ForStmt):
            return self._eval_for(node, scope)
        
        # While loop
        if isinstance(node, WhileStmt):
            return self._eval_while(node, scope)
        
        # Return
        if isinstance(node, ReturnStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            raise ReturnException(val)
        
        # Break
        if isinstance(node, BreakStmt):
            raise BreakException()
        
        # Continue
        if isinstance(node, ContinueStmt):
            raise ContinueException()
        
        # Function declaration
        if isinstance(node, FnDecl):
            fn = TinyFunction(node.name, node.params, node.body, scope)
            scope.define(node.name, Value.function_val(fn), const=True)
            return Value.null_val()
        
        # Struct declaration
        if isinstance(node, StructDecl):
            struct = TinyStruct(node.name, node.fields)
            self.structs[node.name] = struct
            # Define constructor
            scope.define(node.name, Value.function_val(
                TinyFunction(node.name, [(f[0], f[1]) for f in node.fields], None, scope, True,
                            lambda args, s=struct: self._construct_struct(s, args))
            ), const=True)
            return Value.null_val()
        
        # Enum declaration
        if isinstance(node, EnumDecl):
            enum = TinyEnum(node.name, node.variants)
            self.enums[node.name] = enum
            return Value.null_val()
        
        # Import
        if isinstance(node, ImportStmt):
            return self._eval_import(node, scope)
        
        # Match
        if isinstance(node, MatchStmt):
            return self._eval_match(node, scope)
        
        # Try
        if isinstance(node, TryStmt):
            return self._eval_try(node, scope)
        
        # Throw
        if isinstance(node, ThrowStmt):
            val = self._eval(node.value, scope) if node.value else Value.null_val()
            raise TinyTalkError(str(val.data), node.line)
        
        # Assignment (binary =)
        if isinstance(node, BinaryOp) and node.op == '=':
            return self._eval_assignment(node, scope)
        
        raise TinyTalkError(f"Unknown node type: {type(node).__name__}")
    
    def _eval_literal(self, node: Literal) -> Value:
        """Evaluate a literal."""
        val = node.value
        if val is None:
            return Value.null_val()
        if isinstance(val, bool):
            return Value.bool_val(val)
        if isinstance(val, int):
            return Value.int_val(val)
        if isinstance(val, float):
            return Value.float_val(val)
        if isinstance(val, str):
            return Value.string_val(val)
        return Value.null_val()
    
    def _eval_binary(self, node: BinaryOp, scope: Scope) -> Value:
        """Evaluate binary operation."""
        op = node.op
        
        # Short-circuit for and/or
        if op == 'and':
            left = self._eval(node.left, scope)
            if not left.is_truthy():
                return Value.bool_val(False)
            right = self._eval(node.right, scope)
            return Value.bool_val(right.is_truthy())
        
        if op == 'or':
            left = self._eval(node.left, scope)
            if left.is_truthy():
                return Value.bool_val(True)
            right = self._eval(node.right, scope)
            return Value.bool_val(right.is_truthy())
        
        # Assignment
        if op == '=':
            return self._eval_assignment(node, scope)
        
        # Compound assignment
        if op in ('+=', '-=', '*=', '/=', '%=', '//=', '**='):
            return self._eval_compound_assignment(node, scope, op[:-1])
        
        left = self._eval(node.left, scope)
        right = self._eval(node.right, scope)
        
        # Arithmetic
        if op == '+':
            if left.type == ValueType.STRING or right.type == ValueType.STRING:
                return Value.string_val(str(left.data) + str(right.data))
            if left.type == ValueType.LIST and right.type == ValueType.LIST:
                return Value.list_val(left.data + right.data)
            return self._numeric_op(left, right, lambda a, b: a + b)
        
        if op == '-':
            return self._numeric_op(left, right, lambda a, b: a - b)
        
        if op == '*':
            if left.type == ValueType.STRING and right.type == ValueType.INT:
                return Value.string_val(left.data * right.data)
            if left.type == ValueType.LIST and right.type == ValueType.INT:
                return Value.list_val(left.data * right.data)
            return self._numeric_op(left, right, lambda a, b: a * b)
        
        if op == '/':
            if right.data == 0:
                raise TinyTalkError("Division by zero", node.line)
            return Value.float_val(left.data / right.data)
        
        if op == '//':
            if right.data == 0:
                raise TinyTalkError("Division by zero", node.line)
            return Value.int_val(int(left.data // right.data))
        
        if op == '%':
            return self._numeric_op(left, right, lambda a, b: a % b)
        
        if op == '**':
            return self._numeric_op(left, right, lambda a, b: a ** b)
        
        # Comparison
        if op == '<':
            return Value.bool_val(left.data < right.data)
        if op == '>':
            return Value.bool_val(left.data > right.data)
        if op == '<=':
            return Value.bool_val(left.data <= right.data)
        if op == '>=':
            return Value.bool_val(left.data >= right.data)
        if op == '==':
            return Value.bool_val(left.data == right.data)
        if op == '!=':
            return Value.bool_val(left.data != right.data)
        
        # Bitwise
        if op == '&':
            return Value.int_val(int(left.data) & int(right.data))
        if op == '|':
            return Value.int_val(int(left.data) | int(right.data))
        if op == '^':
            return Value.int_val(int(left.data) ^ int(right.data))
        if op == '<<':
            return Value.int_val(int(left.data) << int(right.data))
        if op == '>>':
            return Value.int_val(int(left.data) >> int(right.data))
        
        # In/not in
        if op == 'in':
            if right.type == ValueType.LIST:
                return Value.bool_val(any(left.data == v.data for v in right.data))
            if right.type == ValueType.MAP:
                return Value.bool_val(left.data in right.data)
            if right.type == ValueType.STRING:
                return Value.bool_val(str(left.data) in right.data)
            return Value.bool_val(False)
        
        raise TinyTalkError(f"Unknown operator: {op}", node.line)
    
    def _numeric_op(self, left: Value, right: Value, op: Callable) -> Value:
        """Apply numeric operation."""
        result = op(left.data, right.data)
        if isinstance(result, float) and result.is_integer() and \
           left.type == ValueType.INT and right.type == ValueType.INT:
            return Value.int_val(int(result))
        if isinstance(result, float):
            return Value.float_val(result)
        return Value.int_val(int(result))
    
    def _eval_assignment(self, node: BinaryOp, scope: Scope) -> Value:
        """Evaluate assignment."""
        val = self._eval(node.right, scope)
        
        if isinstance(node.left, Identifier):
            if not scope.set(node.left.name, val):
                scope.define(node.left.name, val)
        elif isinstance(node.left, Index):
            container = self._eval(node.left.obj, scope)
            index = self._eval(node.left.index, scope)
            if container.type == ValueType.LIST:
                container.data[int(index.data)] = val
            elif container.type == ValueType.MAP:
                container.data[index.to_python()] = val
        elif isinstance(node.left, Member):
            obj = self._eval(node.left.obj, scope)
            if obj.type == ValueType.STRUCT_INSTANCE:
                obj.data.fields[node.left.field] = val
            elif obj.type == ValueType.MAP:
                obj.data[node.left.field] = val
        
        return val
    
    def _eval_compound_assignment(self, node: BinaryOp, scope: Scope, op: str) -> Value:
        """Evaluate compound assignment like +=, -=."""
        left = self._eval(node.left, scope)
        right = self._eval(node.right, scope)
        
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '%': lambda a, b: a % b,
            '//': lambda a, b: a // b,
            '**': lambda a, b: a ** b,
        }
        
        result = ops[op](left.data, right.data)
        if isinstance(result, float) and result.is_integer():
            val = Value.int_val(int(result))
        elif isinstance(result, float):
            val = Value.float_val(result)
        else:
            val = Value.int_val(result)
        
        if isinstance(node.left, Identifier):
            scope.set(node.left.name, val)
        
        return val
    
    def _apply_op(self, left: Value, right: Value, op: str, line: int) -> Value:
        """Apply binary operator to values."""
        ops = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '%': lambda a, b: a % b,
            '//': lambda a, b: a // b,
            '**': lambda a, b: a ** b,
        }
        
        if op not in ops:
            raise TinyTalkError(f"Unknown operator: {op}", line)
        
        result = ops[op](left.data, right.data)
        if isinstance(result, float) and result.is_integer():
            return Value.int_val(int(result))
        elif isinstance(result, float):
            return Value.float_val(result)
        return Value.int_val(result)
    
    def _eval_unary(self, node: UnaryOp, scope: Scope) -> Value:
        """Evaluate unary operation."""
        operand = self._eval(node.operand, scope)
        
        if node.op == '-':
            return Value.float_val(-operand.data) if operand.type == ValueType.FLOAT else Value.int_val(-int(operand.data))
        if node.op in ('not', '!'):
            return Value.bool_val(not operand.is_truthy())
        if node.op == '~':
            return Value.int_val(~int(operand.data))
        if node.op == '+':
            return operand
        
        raise TinyTalkError(f"Unknown unary operator: {node.op}", node.line)
    
    def _eval_call(self, node: Call, scope: Scope) -> Value:
        """Evaluate function call."""
        callee = self._eval(node.callee, scope)
        args = [self._eval(arg, scope) for arg in node.args]
        
        if callee.type != ValueType.FUNCTION:
            raise TinyTalkError(f"Cannot call {callee.type.value}", node.line)
        
        return self._call_function(callee.data, args, scope, node.line)
    
    def _call_function(self, fn: TinyFunction, args: List[Value], scope: Scope, line: int) -> Value:
        """Call a function."""
        self.recursion_depth += 1
        
        if self.recursion_depth > self.bounds.max_recursion:
            raise TinyTalkError(f"Exceeded maximum recursion depth ({self.bounds.max_recursion})", line)
        
        try:
            if fn.is_native:
                return fn.native_fn(args)
            
            # Create function scope
            fn_scope = Scope(fn.closure)
            
            # Bind parameters
            for i, (param_name, _) in enumerate(fn.params):
                if i < len(args):
                    fn_scope.define(param_name, args[i])
                else:
                    fn_scope.define(param_name, Value.null_val())
            
            # Execute body
            try:
                result = self._eval(fn.body, fn_scope)
                return result
            except ReturnException as e:
                return e.value
        finally:
            self.recursion_depth -= 1
    
    def _eval_index(self, node: Index, scope: Scope) -> Value:
        """Evaluate index access."""
        obj = self._eval(node.obj, scope)
        index = self._eval(node.index, scope)
        
        if obj.type == ValueType.LIST:
            idx = int(index.data)
            if idx < 0:
                idx = len(obj.data) + idx
            if idx < 0 or idx >= len(obj.data):
                raise TinyTalkError(f"Index {idx} out of bounds", node.line)
            return obj.data[idx]
        
        if obj.type == ValueType.MAP:
            key = index.to_python()
            if key not in obj.data:
                return Value.null_val()
            return obj.data[key]
        
        if obj.type == ValueType.STRING:
            idx = int(index.data)
            if idx < 0:
                idx = len(obj.data) + idx
            if idx < 0 or idx >= len(obj.data):
                raise TinyTalkError(f"Index {idx} out of bounds", node.line)
            return Value.string_val(obj.data[idx])
        
        raise TinyTalkError(f"Cannot index {obj.type.value}", node.line)
    
    def _eval_member(self, node: Member, scope: Scope) -> Value:
        """Evaluate member access."""
        obj = self._eval(node.obj, scope)
        
        if obj.type == ValueType.STRUCT_INSTANCE:
            if node.field in obj.data.fields:
                return obj.data.fields[node.field]
            raise TinyTalkError(f"Unknown field '{node.field}'", node.line)
        
        if obj.type == ValueType.MAP:
            key = node.field
            if key in obj.data:
                return obj.data[key]
            return Value.null_val()
        
        # Built-in methods
        if obj.type == ValueType.STRING:
            if node.field == 'length':
                return Value.int_val(len(obj.data))
        if obj.type == ValueType.LIST:
            if node.field == 'length':
                return Value.int_val(len(obj.data))
        
        raise TinyTalkError(f"Cannot access member of {obj.type.value}", node.line)
    
    def _eval_if(self, node: IfStmt, scope: Scope) -> Value:
        """Evaluate if statement."""
        cond = self._eval(node.condition, scope)
        
        if cond.is_truthy():
            return self._eval(node.then_branch, scope)
        
        for elif_cond, elif_body in node.elif_branches:
            c = self._eval(elif_cond, scope)
            if c.is_truthy():
                return self._eval(elif_body, scope)
        
        if node.else_branch:
            return self._eval(node.else_branch, scope)
        
        return Value.null_val()
    
    def _eval_for(self, node: ForStmt, scope: Scope) -> Value:
        """Evaluate for loop."""
        iterable = self._eval(node.iterable, scope)
        
        if iterable.type == ValueType.LIST:
            items = iterable.data
        elif iterable.type == ValueType.STRING:
            items = [Value.string_val(c) for c in iterable.data]
        elif iterable.type == ValueType.MAP:
            items = [Value.string_val(k) for k in iterable.data.keys()]
        else:
            raise TinyTalkError(f"Cannot iterate over {iterable.type.value}", node.line)
        
        result = Value.null_val()
        for item in items:
            self.iteration_count += 1
            if self.iteration_count > self.bounds.max_iterations:
                raise TinyTalkError(f"Exceeded maximum iterations ({self.bounds.max_iterations})", node.line)
            
            loop_scope = Scope(scope)
            loop_scope.define(node.var, item)
            
            try:
                result = self._eval(node.body, loop_scope)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def _eval_while(self, node: WhileStmt, scope: Scope) -> Value:
        """Evaluate while loop."""
        result = Value.null_val()
        
        while True:
            self.iteration_count += 1
            if self.iteration_count > self.bounds.max_iterations:
                raise TinyTalkError(f"Exceeded maximum iterations ({self.bounds.max_iterations})", node.line)
            
            cond = self._eval(node.condition, scope)
            if not cond.is_truthy():
                break
            
            try:
                result = self._eval(node.body, scope)
            except BreakException:
                break
            except ContinueException:
                continue
        
        return result
    
    def _eval_import(self, node: ImportStmt, scope: Scope) -> Value:
        """Evaluate import statement."""
        # Will be handled by FFI system
        from . import ffi
        
        if node.module.startswith('@'):
            # Built-in module
            ffi.import_builtin(node.module[1:], scope, node.names)
        else:
            # External module
            ffi.import_external(node.module, scope, node.names, node.alias)
        
        return Value.null_val()
    
    def _eval_match(self, node: MatchStmt, scope: Scope) -> Value:
        """Evaluate match statement."""
        value = self._eval(node.expr, scope)
        
        for pattern, guard, body in node.cases:
            if self._match_pattern(value, pattern, scope):
                if guard:
                    if not self._eval(guard, scope).is_truthy():
                        continue
                return self._eval(body, scope)
        
        return Value.null_val()
    
    def _match_pattern(self, value: Value, pattern, scope: Scope) -> bool:
        """Check if value matches pattern."""
        if isinstance(pattern, Literal):
            return value.data == pattern.value
        if isinstance(pattern, Identifier):
            if pattern.name == '_':
                return True
            scope.define(pattern.name, value)
            return True
        return False
    
    def _eval_try(self, node: TryStmt, scope: Scope) -> Value:
        """Evaluate try statement."""
        try:
            return self._eval(node.try_body, scope)
        except TinyTalkError as e:
            if node.catch_var and node.catch_body:
                catch_scope = Scope(scope)
                catch_scope.define(node.catch_var, Value.string_val(str(e.message)))
                return self._eval(node.catch_body, catch_scope)
            raise
        finally:
            if node.finally_body:
                self._eval(node.finally_body, scope)
    
    def _construct_struct(self, struct: TinyStruct, args: List[Value]) -> Value:
        """Construct a struct instance."""
        fields = {}
        for i, (name, _, default) in enumerate(struct.fields):
            if i < len(args):
                fields[name] = args[i]
            elif default:
                fields[name] = self._eval(default, self.global_scope)
            else:
                fields[name] = Value.null_val()
        
        instance = StructInstance(struct, fields)
        return Value(ValueType.STRUCT_INSTANCE, instance)
