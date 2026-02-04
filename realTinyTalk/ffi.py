"""
═══════════════════════════════════════════════════════════════════════════════
TINYTALK FFI (FOREIGN FUNCTION INTERFACE)
Call any language from TinyTalk

Python, JavaScript, Rust, C, Go, and more.
═══════════════════════════════════════════════════════════════════════════════
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable
import importlib
import sys
import os
import subprocess
import json
import tempfile

from .types import Value, ValueType


# ═══════════════════════════════════════════════════════════════════════════════
# FFI CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FFIConfig:
    """FFI security and configuration."""
    allow_python: bool = True
    allow_javascript: bool = True
    allow_system: bool = False  # System calls
    allow_network: bool = False
    allow_filesystem: bool = False
    trusted_modules: List[str] = None
    
    def __post_init__(self):
        if self.trusted_modules is None:
            self.trusted_modules = [
                'math', 'json', 'datetime', 'collections', 'itertools',
                'functools', 'operator', 'string', 're', 'random',
                'statistics', 'decimal', 'fractions', 'numbers',
            ]


# Global config
_ffi_config = FFIConfig()


def configure_ffi(config: FFIConfig):
    """Configure FFI settings."""
    global _ffi_config
    _ffi_config = config


# ═══════════════════════════════════════════════════════════════════════════════
# VALUE CONVERSION
# ═══════════════════════════════════════════════════════════════════════════════

def to_python(value: Value) -> Any:
    """Convert TinyTalk value to Python."""
    if value.type == ValueType.NULL:
        return None
    if value.type == ValueType.LIST:
        return [to_python(v) for v in value.data]
    if value.type == ValueType.MAP:
        return {k: to_python(v) for k, v in value.data.items()}
    return value.data


def from_python(obj: Any) -> Value:
    """Convert Python value to TinyTalk."""
    if obj is None:
        return Value.null_val()
    if isinstance(obj, bool):
        return Value.bool_val(obj)
    if isinstance(obj, int):
        return Value.int_val(obj)
    if isinstance(obj, float):
        return Value.float_val(obj)
    if isinstance(obj, str):
        return Value.string_val(obj)
    if isinstance(obj, (list, tuple)):
        return Value.list_val([from_python(x) for x in obj])
    if isinstance(obj, dict):
        return Value.map_val({k: from_python(v) for k, v in obj.items()})
    if callable(obj):
        return wrap_python_function(obj)
    # Try to convert to string
    return Value.string_val(str(obj))


def wrap_python_function(fn: Callable) -> Value:
    """Wrap a Python function for TinyTalk."""
    from .runtime import TinyFunction
    
    def wrapper(args: List[Value]) -> Value:
        py_args = [to_python(a) for a in args]
        result = fn(*py_args)
        return from_python(result)
    
    tiny_fn = TinyFunction(
        name=getattr(fn, '__name__', '<python_fn>'),
        params=[],
        body=None,
        closure=None,
        is_native=True,
        native_fn=wrapper
    )
    return Value.function_val(tiny_fn)


# ═══════════════════════════════════════════════════════════════════════════════
# PYTHON INTEROP
# ═══════════════════════════════════════════════════════════════════════════════

def import_python(module_name: str, names: Optional[List[str]] = None) -> Dict[str, Value]:
    """Import a Python module."""
    global _ffi_config
    
    if not _ffi_config.allow_python:
        raise RuntimeError("Python FFI is disabled")
    
    # Security check
    if module_name not in _ffi_config.trusted_modules:
        if not any(module_name.startswith(m + '.') for m in _ffi_config.trusted_modules):
            raise RuntimeError(f"Module '{module_name}' is not in trusted list")
    
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise RuntimeError(f"Cannot import Python module '{module_name}': {e}")
    
    exports = {}
    
    if names:
        # Import specific names
        for name in names:
            if hasattr(module, name):
                obj = getattr(module, name)
                exports[name] = from_python(obj)
    else:
        # Import all public names
        for name in dir(module):
            if not name.startswith('_'):
                obj = getattr(module, name)
                if callable(obj) or not hasattr(obj, '__dict__'):
                    exports[name] = from_python(obj)
    
    return exports


class PythonModule:
    """Proxy for accessing Python modules."""
    
    def __init__(self, module):
        self._module = module
    
    def __getattr__(self, name: str) -> Value:
        if hasattr(self._module, name):
            obj = getattr(self._module, name)
            return from_python(obj)
        raise AttributeError(f"Module has no attribute '{name}'")


# ═══════════════════════════════════════════════════════════════════════════════
# JAVASCRIPT INTEROP (via Node.js)
# ═══════════════════════════════════════════════════════════════════════════════

def call_javascript(code: str, args: List[Value] = None) -> Value:
    """Execute JavaScript code and return result."""
    global _ffi_config
    
    if not _ffi_config.allow_javascript:
        raise RuntimeError("JavaScript FFI is disabled")
    
    # Prepare arguments
    js_args = json.dumps([to_python(a) for a in (args or [])])
    
    # Create JavaScript wrapper
    js_code = f"""
const args = {js_args};
const result = (function(args) {{
    {code}
}})(args);
console.log(JSON.stringify(result));
"""
    
    # Execute via Node.js
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            temp_path = f.name
        
        result = subprocess.run(
            ['node', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        os.unlink(temp_path)
        
        if result.returncode != 0:
            raise RuntimeError(f"JavaScript error: {result.stderr}")
        
        output = result.stdout.strip()
        if output:
            return from_python(json.loads(output))
        return Value.null_val()
        
    except FileNotFoundError:
        raise RuntimeError("Node.js is not installed or not in PATH")
    except subprocess.TimeoutExpired:
        raise RuntimeError("JavaScript execution timed out")


def import_javascript(module_path: str) -> Dict[str, Value]:
    """Import a JavaScript/Node.js module."""
    js_code = f"""
const mod = require('{module_path}');
const exports = {{}};
for (const [key, value] of Object.entries(mod)) {{
    if (typeof value === 'function') {{
        exports[key] = value.toString();
    }} else {{
        exports[key] = value;
    }}
}}
return exports;
"""
    result = call_javascript(js_code)
    return result.data if result.type == ValueType.MAP else {}


# ═══════════════════════════════════════════════════════════════════════════════
# C/RUST INTEROP (via ctypes/cffi)
# ═══════════════════════════════════════════════════════════════════════════════

def load_shared_library(path: str) -> 'CLibrary':
    """Load a C/Rust shared library."""
    import ctypes
    
    lib = ctypes.CDLL(path)
    return CLibrary(lib)


class CLibrary:
    """Wrapper for C shared libraries."""
    
    def __init__(self, lib):
        self._lib = lib
        self._functions = {}
    
    def declare(self, name: str, argtypes: List[str], restype: str):
        """Declare a function signature."""
        import ctypes
        
        type_map = {
            'int': ctypes.c_int,
            'long': ctypes.c_long,
            'float': ctypes.c_float,
            'double': ctypes.c_double,
            'char': ctypes.c_char,
            'void': None,
            'pointer': ctypes.c_void_p,
            'string': ctypes.c_char_p,
        }
        
        fn = getattr(self._lib, name)
        fn.argtypes = [type_map.get(t, ctypes.c_void_p) for t in argtypes]
        fn.restype = type_map.get(restype)
        self._functions[name] = fn
    
    def call(self, name: str, args: List[Value]) -> Value:
        """Call a declared function."""
        if name not in self._functions:
            raise RuntimeError(f"Function '{name}' not declared")
        
        fn = self._functions[name]
        py_args = [to_python(a) for a in args]
        result = fn(*py_args)
        return from_python(result)


# ═══════════════════════════════════════════════════════════════════════════════
# GO INTEROP (via cgo)
# ═══════════════════════════════════════════════════════════════════════════════

def call_go(code: str, args: List[Value] = None) -> Value:
    """Execute Go code and return result."""
    go_args = json.dumps([to_python(a) for a in (args or [])])
    
    go_code = f'''
package main

import (
    "encoding/json"
    "fmt"
)

func main() {{
    var args []interface{{}}
    json.Unmarshal([]byte(`{go_args}`), &args)
    
    result := func(args []interface{{}}) interface{{}} {{
        {code}
    }}(args)
    
    out, _ := json.Marshal(result)
    fmt.Println(string(out))
}}
'''
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
            f.write(go_code)
            temp_path = f.name
        
        result = subprocess.run(
            ['go', 'run', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        os.unlink(temp_path)
        
        if result.returncode != 0:
            raise RuntimeError(f"Go error: {result.stderr}")
        
        output = result.stdout.strip()
        if output:
            return from_python(json.loads(output))
        return Value.null_val()
        
    except FileNotFoundError:
        raise RuntimeError("Go is not installed or not in PATH")


# ═══════════════════════════════════════════════════════════════════════════════
# RUST INTEROP (via compilation)
# ═══════════════════════════════════════════════════════════════════════════════

def call_rust(code: str, args: List[Value] = None) -> Value:
    """Execute Rust code and return result."""
    rust_args = json.dumps([to_python(a) for a in (args or [])])
    
    rust_code = f'''
use serde_json::{{Value, json}};

fn main() {{
    let args: Vec<Value> = serde_json::from_str(r#"{rust_args}"#).unwrap();
    
    let result = (|| {{
        {code}
    }})();
    
    println!("{{}}", serde_json::to_string(&result).unwrap());
}}
'''
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            src_path = os.path.join(tmpdir, 'main.rs')
            with open(src_path, 'w') as f:
                f.write(rust_code)
            
            # Create Cargo.toml
            cargo_toml = '''
[package]
name = "tinytalk_rust"
version = "0.1.0"

[dependencies]
serde_json = "1.0"
'''
            cargo_path = os.path.join(tmpdir, 'Cargo.toml')
            with open(cargo_path, 'w') as f:
                f.write(cargo_toml)
            
            # Compile and run
            result = subprocess.run(
                ['cargo', 'run', '--quiet'],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Rust error: {result.stderr}")
            
            output = result.stdout.strip()
            if output:
                return from_python(json.loads(output))
            return Value.null_val()
            
    except FileNotFoundError:
        raise RuntimeError("Rust/Cargo is not installed or not in PATH")


# ═══════════════════════════════════════════════════════════════════════════════
# SHELL INTEROP
# ═══════════════════════════════════════════════════════════════════════════════

def call_shell(command: str, args: List[Value] = None) -> Value:
    """Execute a shell command."""
    global _ffi_config
    
    if not _ffi_config.allow_system:
        raise RuntimeError("System calls are disabled")
    
    if args:
        for arg in args:
            command += f" {to_python(arg)}"
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return Value.map_val({
            'stdout': Value.string_val(result.stdout),
            'stderr': Value.string_val(result.stderr),
            'code': Value.int_val(result.returncode),
        })
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Shell command timed out")


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP INTEROP
# ═══════════════════════════════════════════════════════════════════════════════

def http_get(url: str) -> Value:
    """Make HTTP GET request."""
    global _ffi_config
    
    if not _ffi_config.allow_network:
        raise RuntimeError("Network access is disabled")
    
    try:
        import urllib.request
        import urllib.error
        
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read().decode('utf-8')
            return Value.map_val({
                'status': Value.int_val(response.status),
                'body': Value.string_val(body),
                'headers': Value.map_val({
                    k: Value.string_val(v) for k, v in response.headers.items()
                }),
            })
    except urllib.error.URLError as e:
        raise RuntimeError(f"HTTP error: {e}")


def http_post(url: str, data: Value) -> Value:
    """Make HTTP POST request."""
    global _ffi_config
    
    if not _ffi_config.allow_network:
        raise RuntimeError("Network access is disabled")
    
    try:
        import urllib.request
        
        body = json.dumps(to_python(data)).encode('utf-8')
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = response.read().decode('utf-8')
            return Value.map_val({
                'status': Value.int_val(response.status),
                'body': Value.string_val(result),
            })
    except Exception as e:
        raise RuntimeError(f"HTTP error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# BUILTIN MODULES
# ═══════════════════════════════════════════════════════════════════════════════

BUILTIN_MODULES = {
    'math': lambda: import_python('math'),
    'json': lambda: import_python('json'),
    'datetime': lambda: import_python('datetime'),
    're': lambda: import_python('re'),
    'random': lambda: import_python('random'),
    'os': lambda: import_python('os') if _ffi_config.allow_filesystem else {},
    'sys': lambda: import_python('sys'),
    'collections': lambda: import_python('collections'),
    'itertools': lambda: import_python('itertools'),
    'functools': lambda: import_python('functools'),
    'statistics': lambda: import_python('statistics'),
}


def import_builtin(name: str, scope, names: Optional[List[str]] = None):
    """Import a built-in module."""
    from .runtime import Scope
    
    if name not in BUILTIN_MODULES:
        raise RuntimeError(f"Unknown built-in module: @{name}")
    
    exports = BUILTIN_MODULES[name]()
    
    if names:
        for n in names:
            if n in exports:
                scope.define(n, exports[n])
    else:
        # Create module namespace
        module_val = Value.map_val(exports)
        scope.define(name, module_val)


def import_external(module: str, scope, names: Optional[List[str]] = None, alias: Optional[str] = None):
    """Import an external module."""
    # Determine module type from path/name
    if module.endswith('.py') or '.' not in module:
        # Python module
        exports = import_python(module.replace('.py', '').replace('/', '.'))
    elif module.endswith('.js'):
        # JavaScript module
        exports = import_javascript(module)
    elif module.endswith('.so') or module.endswith('.dll') or module.endswith('.dylib'):
        # Shared library
        lib = load_shared_library(module)
        exports = {'lib': from_python(lib)}
    else:
        # Try Python first
        try:
            exports = import_python(module)
        except RuntimeError:
            raise RuntimeError(f"Cannot import module: {module}")
    
    if names:
        for n in names:
            if n in exports:
                scope.define(n, exports[n])
    else:
        module_name = alias or module.split('.')[-1].split('/')[-1].replace('.py', '')
        module_val = Value.map_val(exports)
        scope.define(module_name, module_val)


# ═══════════════════════════════════════════════════════════════════════════════
# FFI BUILTINS FOR TINYTALK
# ═══════════════════════════════════════════════════════════════════════════════

def builtin_python(args: List[Value]) -> Value:
    """Execute Python code: python("print('hello')")"""
    if not args:
        return Value.null_val()
    
    code = to_python(args[0])
    local_vars = {}
    
    if len(args) > 1 and args[1].type == ValueType.MAP:
        local_vars = {k: to_python(v) for k, v in args[1].data.items()}
    
    exec(code, {'__builtins__': __builtins__}, local_vars)
    
    if '_result' in local_vars:
        return from_python(local_vars['_result'])
    return Value.null_val()


def builtin_eval_python(args: List[Value]) -> Value:
    """Evaluate Python expression: eval_python("1 + 2")"""
    if not args:
        return Value.null_val()
    
    code = to_python(args[0])
    result = eval(code)
    return from_python(result)


def builtin_javascript(args: List[Value]) -> Value:
    """Execute JavaScript code: javascript("return 1 + 2")"""
    if not args:
        return Value.null_val()
    
    code = to_python(args[0])
    js_args = args[1:] if len(args) > 1 else []
    return call_javascript(code, js_args)


def builtin_shell(args: List[Value]) -> Value:
    """Execute shell command: shell("ls -la")"""
    if not args:
        return Value.null_val()
    
    command = to_python(args[0])
    return call_shell(command, args[1:])


def builtin_http_get(args: List[Value]) -> Value:
    """HTTP GET request: http_get("https://api.example.com")"""
    if not args:
        return Value.null_val()
    
    url = to_python(args[0])
    return http_get(url)


def builtin_http_post(args: List[Value]) -> Value:
    """HTTP POST request: http_post("url", data)"""
    if len(args) < 2:
        return Value.null_val()
    
    url = to_python(args[0])
    return http_post(url, args[1])


# Export FFI builtins
FFI_BUILTINS = {
    'python': builtin_python,
    'eval_python': builtin_eval_python,
    'javascript': builtin_javascript,
    'shell': builtin_shell,
    'http_get': builtin_http_get,
    'http_post': builtin_http_post,
}
