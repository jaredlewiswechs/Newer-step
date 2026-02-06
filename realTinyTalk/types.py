"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK TYPE SYSTEM
Static typing with inference

Types are verified, not assumed.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Any, Union, Set


class TypeKind(Enum):
    """Kinds of types in TinyTalk."""
    # Primitives
    INT = auto()
    FLOAT = auto()
    STR = auto()
    BOOL = auto()
    NULL = auto()
    
    # Compound
    LIST = auto()
    MAP = auto()
    TUPLE = auto()
    
    # Function
    FUNCTION = auto()
    
    # User-defined
    STRUCT = auto()
    ENUM = auto()
    
    # Special
    ANY = auto()
    VOID = auto()
    NEVER = auto()
    UNKNOWN = auto()
    
    # Union/intersection
    UNION = auto()
    OPTIONAL = auto()


@dataclass
class TinyType:
    """A type in the TinyTalk type system."""
    kind: TypeKind
    name: str = ""
    params: List['TinyType'] = field(default_factory=list)  # Generic parameters
    fields: Dict[str, 'TinyType'] = field(default_factory=dict)  # Struct fields
    variants: Dict[str, Optional['TinyType']] = field(default_factory=dict)  # Enum variants
    
    # Function type specifics
    param_types: List['TinyType'] = field(default_factory=list)
    return_type: Optional['TinyType'] = None
    
    def __eq__(self, other: 'TinyType') -> bool:
        if not isinstance(other, TinyType):
            return False
        if self.kind != other.kind:
            return False
        if self.kind in (TypeKind.LIST, TypeKind.MAP, TypeKind.TUPLE):
            return self.params == other.params
        if self.kind == TypeKind.FUNCTION:
            return self.param_types == other.param_types and self.return_type == other.return_type
        if self.kind in (TypeKind.STRUCT, TypeKind.ENUM):
            return self.name == other.name
        return True
    
    def __hash__(self):
        return hash((self.kind, self.name, tuple(self.params)))
    
    def __repr__(self) -> str:
        if self.kind == TypeKind.INT:
            return "int"
        if self.kind == TypeKind.FLOAT:
            return "float"
        if self.kind == TypeKind.STR:
            return "str"
        if self.kind == TypeKind.BOOL:
            return "bool"
        if self.kind == TypeKind.NULL:
            return "null"
        if self.kind == TypeKind.ANY:
            return "any"
        if self.kind == TypeKind.VOID:
            return "void"
        if self.kind == TypeKind.NEVER:
            return "never"
        if self.kind == TypeKind.LIST:
            inner = self.params[0] if self.params else "any"
            return f"list[{inner}]"
        if self.kind == TypeKind.MAP:
            key = self.params[0] if len(self.params) > 0 else "any"
            val = self.params[1] if len(self.params) > 1 else "any"
            return f"map[{key}, {val}]"
        if self.kind == TypeKind.TUPLE:
            types = ", ".join(str(t) for t in self.params)
            return f"({types})"
        if self.kind == TypeKind.FUNCTION:
            params = ", ".join(str(t) for t in self.param_types)
            ret = str(self.return_type) if self.return_type else "void"
            return f"fn({params}) -> {ret}"
        if self.kind == TypeKind.STRUCT:
            return self.name
        if self.kind == TypeKind.ENUM:
            return self.name
        if self.kind == TypeKind.OPTIONAL:
            inner = self.params[0] if self.params else "any"
            return f"?{inner}"
        if self.kind == TypeKind.UNION:
            types = " | ".join(str(t) for t in self.params)
            return f"({types})"
        return f"<{self.kind.name}>"
    
    @classmethod
    def int_type(cls) -> 'TinyType':
        return cls(TypeKind.INT)
    
    @classmethod
    def float_type(cls) -> 'TinyType':
        return cls(TypeKind.FLOAT)
    
    @classmethod
    def str_type(cls) -> 'TinyType':
        return cls(TypeKind.STR)
    
    @classmethod
    def bool_type(cls) -> 'TinyType':
        return cls(TypeKind.BOOL)
    
    @classmethod
    def null_type(cls) -> 'TinyType':
        return cls(TypeKind.NULL)
    
    @classmethod
    def any_type(cls) -> 'TinyType':
        return cls(TypeKind.ANY)
    
    @classmethod
    def void_type(cls) -> 'TinyType':
        return cls(TypeKind.VOID)
    
    @classmethod
    def list_type(cls, element_type: 'TinyType') -> 'TinyType':
        return cls(TypeKind.LIST, params=[element_type])
    
    @classmethod
    def map_type(cls, key_type: 'TinyType', value_type: 'TinyType') -> 'TinyType':
        return cls(TypeKind.MAP, params=[key_type, value_type])
    
    @classmethod
    def function_type(cls, param_types: List['TinyType'], return_type: 'TinyType') -> 'TinyType':
        return cls(TypeKind.FUNCTION, param_types=param_types, return_type=return_type)
    
    @classmethod
    def optional_type(cls, inner: 'TinyType') -> 'TinyType':
        return cls(TypeKind.OPTIONAL, params=[inner])
    
    @classmethod
    def union_type(cls, *types: 'TinyType') -> 'TinyType':
        return cls(TypeKind.UNION, params=list(types))
    
    def is_numeric(self) -> bool:
        return self.kind in (TypeKind.INT, TypeKind.FLOAT)
    
    def is_primitive(self) -> bool:
        return self.kind in (TypeKind.INT, TypeKind.FLOAT, TypeKind.STR, 
                             TypeKind.BOOL, TypeKind.NULL)


# ═══════════════════════════════════════════════════════════════════════════════
# VALUE TYPE
# ═══════════════════════════════════════════════════════════════════════════════

class ValueType(Enum):
    """Runtime value types."""
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    NULL = "null"
    LIST = "list"
    MAP = "map"
    FUNCTION = "function"
    STRUCT_INSTANCE = "struct_instance"
    ENUM_VARIANT = "enum_variant"


@dataclass
class Value:
    """Runtime value with type."""
    type: ValueType
    data: Any
    verified: bool = True
    
    @classmethod
    def int_val(cls, n: int) -> 'Value':
        return cls(ValueType.INT, int(n))
    
    @classmethod
    def float_val(cls, n: float) -> 'Value':
        return cls(ValueType.FLOAT, float(n))
    
    @classmethod
    def string_val(cls, s: str) -> 'Value':
        return cls(ValueType.STRING, str(s))
    
    @classmethod
    def bool_val(cls, b: bool) -> 'Value':
        return cls(ValueType.BOOLEAN, bool(b))
    
    @classmethod
    def null_val(cls) -> 'Value':
        return cls(ValueType.NULL, None)
    
    @classmethod
    def list_val(cls, items: List['Value']) -> 'Value':
        return cls(ValueType.LIST, items)
    
    @classmethod
    def map_val(cls, pairs: Dict[Any, 'Value']) -> 'Value':
        return cls(ValueType.MAP, pairs)
    
    @classmethod
    def function_val(cls, fn: Any) -> 'Value':
        return cls(ValueType.FUNCTION, fn)
    
    def is_truthy(self) -> bool:
        if self.type == ValueType.BOOLEAN:
            return self.data
        if self.type == ValueType.NULL:
            return False
        if self.type == ValueType.INT or self.type == ValueType.FLOAT:
            return self.data != 0
        if self.type == ValueType.STRING:
            return len(self.data) > 0
        if self.type == ValueType.LIST:
            return len(self.data) > 0
        if self.type == ValueType.MAP:
            return len(self.data) > 0
        return True
    
    def __repr__(self) -> str:
        if self.type == ValueType.NULL:
            return "null"
        if self.type == ValueType.STRING:
            return f'"{self.data}"'
        if self.type == ValueType.BOOLEAN:
            return "true" if self.data else "false"
        if self.type == ValueType.LIST:
            items = ", ".join(repr(v) for v in self.data)
            return f"[{items}]"
        if self.type == ValueType.MAP:
            pairs = ", ".join(f"{k}: {repr(v)}" for k, v in self.data.items())
            return f"{{{pairs}}}"
        if self.type == ValueType.FUNCTION:
            return f"<function>"
        return str(self.data)
    
    def to_python(self) -> Any:
        """Convert to Python value."""
        if self.type == ValueType.NULL:
            return None
        if self.type == ValueType.LIST:
            return [v.to_python() for v in self.data]
        if self.type == ValueType.MAP:
            return {k: v.to_python() for k, v in self.data.items()}
        return self.data


# ═══════════════════════════════════════════════════════════════════════════════
# TYPE CHECKER
# ═══════════════════════════════════════════════════════════════════════════════

class TypeChecker:
    """
    Static type checker for TinyTalk.
    
    Performs type inference and checking on the AST.
    """
    
    def __init__(self):
        self.type_env: Dict[str, TinyType] = {}
        self.struct_types: Dict[str, TinyType] = {}
        self.enum_types: Dict[str, TinyType] = {}
        self.errors: List[str] = []
    
    def check(self, ast) -> List[str]:
        """Type check an AST. Returns list of errors."""
        self.errors = []
        self._check_node(ast)
        return self.errors
    
    def _check_node(self, node) -> Optional[TinyType]:
        """Check a node and return its type."""
        from .parser import (Program, Literal, Identifier, BinaryOp, UnaryOp,
                            Call, Index, Member, Array, MapLiteral, Lambda,
                            LetStmt, FnDecl, IfStmt, ForStmt, WhileStmt,
                            Block, ReturnStmt)
        
        if isinstance(node, Program):
            for stmt in node.statements:
                self._check_node(stmt)
            return None
        
        if isinstance(node, Literal):
            return self._infer_literal_type(node.value)
        
        if isinstance(node, Identifier):
            if node.name in self.type_env:
                return self.type_env[node.name]
            self.errors.append(f"Line {node.line}: Unknown identifier '{node.name}'")
            return TinyType.any_type()
        
        if isinstance(node, BinaryOp):
            left_type = self._check_node(node.left)
            right_type = self._check_node(node.right)
            return self._check_binary_op(node.op, left_type, right_type, node.line)
        
        if isinstance(node, UnaryOp):
            operand_type = self._check_node(node.operand)
            return self._check_unary_op(node.op, operand_type, node.line)
        
        if isinstance(node, Call):
            callee_type = self._check_node(node.callee)
            arg_types = [self._check_node(arg) for arg in node.args]
            return self._check_call(callee_type, arg_types, node.line)
        
        if isinstance(node, Array):
            element_types = [self._check_node(el) for el in node.elements]
            if element_types:
                # Infer common type
                return TinyType.list_type(element_types[0])
            return TinyType.list_type(TinyType.any_type())
        
        if isinstance(node, MapLiteral):
            if node.pairs:
                key_type = self._check_node(node.pairs[0][0])
                val_type = self._check_node(node.pairs[0][1])
                return TinyType.map_type(key_type, val_type)
            return TinyType.map_type(TinyType.any_type(), TinyType.any_type())
        
        if isinstance(node, LetStmt):
            if node.value:
                value_type = self._check_node(node.value)
                if node.type_hint:
                    declared_type = self._parse_type_string(node.type_hint)
                    if not self._is_compatible(value_type, declared_type):
                        self.errors.append(
                            f"Line {node.line}: Type mismatch: expected {declared_type}, got {value_type}")
                    self.type_env[node.name] = declared_type
                else:
                    self.type_env[node.name] = value_type
            elif node.type_hint:
                self.type_env[node.name] = self._parse_type_string(node.type_hint)
            else:
                self.type_env[node.name] = TinyType.any_type()
            return None
        
        if isinstance(node, FnDecl):
            param_types = []
            for name, type_hint in node.params:
                t = self._parse_type_string(type_hint) if type_hint else TinyType.any_type()
                param_types.append(t)
                self.type_env[name] = t
            
            return_type = self._parse_type_string(node.return_type) if node.return_type else TinyType.void_type()
            
            fn_type = TinyType.function_type(param_types, return_type)
            self.type_env[node.name] = fn_type
            
            if node.body:
                self._check_node(node.body)
            
            return fn_type
        
        if isinstance(node, Block):
            result = None
            for stmt in node.statements:
                result = self._check_node(stmt)
            return result
        
        if isinstance(node, IfStmt):
            cond_type = self._check_node(node.condition)
            if cond_type and cond_type.kind != TypeKind.BOOL:
                self.errors.append(f"Line {node.line}: Condition must be boolean, got {cond_type}")
            
            self._check_node(node.then_branch)
            for cond, body in node.elif_branches:
                self._check_node(cond)
                self._check_node(body)
            if node.else_branch:
                self._check_node(node.else_branch)
            return None
        
        if isinstance(node, ForStmt):
            iter_type = self._check_node(node.iterable)
            if iter_type and iter_type.kind == TypeKind.LIST and iter_type.params:
                self.type_env[node.var] = iter_type.params[0]
            else:
                self.type_env[node.var] = TinyType.any_type()
            self._check_node(node.body)
            return None
        
        if isinstance(node, WhileStmt):
            cond_type = self._check_node(node.condition)
            if cond_type and cond_type.kind != TypeKind.BOOL:
                self.errors.append(f"Line {node.line}: Condition must be boolean, got {cond_type}")
            self._check_node(node.body)
            return None
        
        if isinstance(node, ReturnStmt):
            if node.value:
                return self._check_node(node.value)
            return TinyType.void_type()
        
        if isinstance(node, Lambda):
            param_types = [TinyType.any_type() for _ in node.params]
            for name in node.params:
                self.type_env[name] = TinyType.any_type()
            body_type = self._check_node(node.body) or TinyType.any_type()
            return TinyType.function_type(param_types, body_type)
        
        return TinyType.any_type()
    
    def _infer_literal_type(self, value: Any) -> TinyType:
        """Infer type from a literal value."""
        if value is None:
            return TinyType.null_type()
        if isinstance(value, bool):
            return TinyType.bool_type()
        if isinstance(value, int):
            return TinyType.int_type()
        if isinstance(value, float):
            return TinyType.float_type()
        if isinstance(value, str):
            return TinyType.str_type()
        return TinyType.any_type()
    
    def _check_binary_op(self, op: str, left: TinyType, right: TinyType, line: int) -> TinyType:
        """Check binary operation types."""
        if op in ('+', '-', '*', '/', '%', '**', '//'):
            # Arithmetic
            if left and right and left.is_numeric() and right.is_numeric():
                if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                    return TinyType.float_type()
                return TinyType.int_type()
            if op == '+' and left and left.kind == TypeKind.STR:
                return TinyType.str_type()
            self.errors.append(f"Line {line}: Cannot apply {op} to {left} and {right}")
            return TinyType.any_type()
        
        if op in ('<', '>', '<=', '>='):
            if left and right and left.is_numeric() and right.is_numeric():
                return TinyType.bool_type()
            self.errors.append(f"Line {line}: Cannot compare {left} and {right}")
            return TinyType.bool_type()
        
        if op in ('==', '!='):
            return TinyType.bool_type()
        
        if op in ('and', 'or'):
            return TinyType.bool_type()
        
        if op in ('&', '|', '^', '<<', '>>'):
            return TinyType.int_type()
        
        return TinyType.any_type()
    
    def _check_unary_op(self, op: str, operand: TinyType, line: int) -> TinyType:
        """Check unary operation types."""
        if op == '-':
            if operand and operand.is_numeric():
                return operand
            self.errors.append(f"Line {line}: Cannot negate {operand}")
            return TinyType.any_type()
        
        if op in ('not', '!'):
            return TinyType.bool_type()
        
        if op == '~':
            return TinyType.int_type()
        
        return TinyType.any_type()
    
    def _check_call(self, callee: TinyType, args: List[TinyType], line: int) -> TinyType:
        """Check function call types."""
        if callee and callee.kind == TypeKind.FUNCTION:
            # Check argument count
            if len(args) != len(callee.param_types):
                self.errors.append(
                    f"Line {line}: Expected {len(callee.param_types)} arguments, got {len(args)}")
            
            # Check argument types
            for i, (expected, actual) in enumerate(zip(callee.param_types, args)):
                if not self._is_compatible(actual, expected):
                    self.errors.append(
                        f"Line {line}: Argument {i+1}: expected {expected}, got {actual}")
            
            return callee.return_type or TinyType.any_type()
        
        return TinyType.any_type()
    
    def _is_compatible(self, actual: TinyType, expected: TinyType) -> bool:
        """Check if actual type is compatible with expected."""
        if expected.kind == TypeKind.ANY:
            return True
        if actual.kind == TypeKind.ANY:
            return True
        if actual == expected:
            return True
        # Int is compatible with float
        if actual.kind == TypeKind.INT and expected.kind == TypeKind.FLOAT:
            return True
        # Null is compatible with optional
        if actual.kind == TypeKind.NULL and expected.kind == TypeKind.OPTIONAL:
            return True
        return False
    
    def _parse_type_string(self, type_str: str) -> TinyType:
        """Parse a type string into a TinyType."""
        type_str = type_str.strip()
        
        # Optional type
        if type_str.startswith('?'):
            inner = self._parse_type_string(type_str[1:])
            return TinyType.optional_type(inner)
        
        # Primitive types
        type_map = {
            'int': TinyType.int_type,
            'float': TinyType.float_type,
            'str': TinyType.str_type,
            'bool': TinyType.bool_type,
            'any': TinyType.any_type,
            'void': TinyType.void_type,
        }
        
        if type_str in type_map:
            return type_map[type_str]()
        
        # Generic types: list[T], map[K, V]
        if '[' in type_str:
            base = type_str[:type_str.index('[')]
            params_str = type_str[type_str.index('[')+1:-1]
            
            if base == 'list':
                inner = self._parse_type_string(params_str)
                return TinyType.list_type(inner)
            
            if base == 'map':
                parts = params_str.split(',', 1)
                key = self._parse_type_string(parts[0])
                val = self._parse_type_string(parts[1]) if len(parts) > 1 else TinyType.any_type()
                return TinyType.map_type(key, val)
        
        # User-defined types
        if type_str in self.struct_types:
            return self.struct_types[type_str]
        if type_str in self.enum_types:
            return self.enum_types[type_str]
        
        return TinyType.any_type()
