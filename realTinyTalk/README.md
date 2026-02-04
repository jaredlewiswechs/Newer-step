# TinyTalk

**The Verified General-Purpose Programming Language**

> Every loop bounded. Every operation traced. Every output proven.

TinyTalk is a Turing-complete programming language built on Newton's verified computation architecture. It combines the power of a modern general-purpose language with the safety guarantees of bounded, verifiable execution.

```
┌─────────────────────────────────────────────────────────────────┐
│                        TinyTalk Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│  Source → Lexer → Parser → Type Check → Verify → Execute        │
│                                              ↓                   │
│                                         Bounded                  │
│                                              ↓                   │
│                              Trace ← Ledger ← Result             │
└─────────────────────────────────────────────────────────────────┘
```

## Features

| Feature | Description |
|---------|-------------|
| **Verified Execution** | Every operation is bounded and traced |
| **Turing Complete** | Full loops, recursion, conditionals |
| **Type System** | Static typing with inference |
| **FFI** | Call Python, JavaScript, Go, Rust, C |
| **Functional** | First-class functions, lambdas, pipes |
| **Safe by Default** | No infinite loops, no stack overflow |

## Quick Start

### Hello World

```tinytalk
println("Hello, World!")
```

### Run Code

```python
from tinytalk import run

result = run('println("Hello!")')
```

### REPL

```python
from tinytalk import repl
repl()
```

## Language Reference

### Variables

```tinytalk
let x = 10
x = 20

const PI = 3.14159
```

### Functions

```tinytalk
fn add(a, b) {
    return a + b
}

let double = (x) => x * 2
```

### Control Flow

```tinytalk
if x > 0 {
    println("positive")
} elif x < 0 {
    println("negative")
} else {
    println("zero")
}

for i in range(10) {
    println(i)
}

while i < 10 {
    i = i + 1
}
```

### Collections

```tinytalk
let list = [1, 2, 3]
let map = {"a": 1, "b": 2}
```

## Standard Library

### Output
```tinytalk
print("no newline")
println("with newline")
```

### Type Functions
```tinytalk
len([1, 2, 3])
type(42)
str(123)
int("42")
float("3.14")
```

### Collections
```tinytalk
range(5)
append(list, item)
keys(map)
values(map)
contains(list, item)
reverse(list)
sort(list)
```

### Math
```tinytalk
sum([1, 2, 3])
min(1, 2, 3)
max([1, 2, 3])
abs(-5)
sqrt(16)
pow(2, 10)
```

## FFI (Foreign Function Interface)

```tinytalk
// Import Python module
import @math
let x = math.sqrt(16)

// Execute Python code
let result = eval_python("sum([1, 2, 3, 4, 5])")
```

## Verified Execution

```python
from tinytalk import run, ExecutionBounds

bounds = ExecutionBounds(
    max_ops=1_000_000,
    max_iterations=100_000,
    max_recursion=1000,
    timeout_seconds=30.0
)

result = run(source, bounds)
```

## Examples

### Fibonacci

```tinytalk
fn fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

println(fib(10))  // 55
```

### FizzBuzz

```tinytalk
fn fizzbuzz(n) {
    if n % 15 == 0 {
        return "FizzBuzz"
    }
    if n % 3 == 0 {
        return "Fizz"
    }
    if n % 5 == 0 {
        return "Buzz"
    }
    return n
}
```

## Architecture

```
tinytalk/
├── __init__.py      # Package exports, run(), repl()
├── kernel.py        # Newton verified execution kernel
├── lexer.py         # Tokenizer (~100 token types)
├── parser.py        # Recursive descent parser
├── types.py         # Type system
├── runtime.py       # Interpreter with bounded execution
├── ffi.py           # Foreign function interface
└── stdlib.py        # Standard library functions
```

## Philosophy

1. **The constraint IS the instruction**
2. **The verification IS the computation**
3. **The trace IS the proof**

---

*Built with Newton Supercomputer - Where 1 == 1*
