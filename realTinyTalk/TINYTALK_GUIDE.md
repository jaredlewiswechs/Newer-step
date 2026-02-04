# The realTinyTalk Programming Language

## A Complete Guide

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║               r e a l T i n y T A L K                         ║
║                                                               ║
║              The Friendliest Programming Language             ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Version 1.0** — February 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Quick Tutorial](#quick-tutorial-learn-tinytalk-in-5-minutes) ⭐
4. [Values and Types](#3-values-and-types)
5. [Variables and Constants](#4-variables-and-constants)
6. [Operators](#5-operators)
7. [Natural Comparisons](#natural-comparisons) ✨ NEW!
8. [Step Chains](#step-chains) ✨ NEW!
9. [Control Flow](#6-control-flow)
10. [Functions](#7-functions)
11. [Collections](#8-collections)
12. [Property Conversions](#9-property-conversions)
13. [String Properties](#string-properties) ✨ NEW!
14. [Blueprints (Classes)](#10-blueprints-classes)
15. [Built-in Functions](#11-built-in-functions)
16. [Error Handling](#12-error-handling)
17. [Style Guide](#13-style-guide)
18. [Complete Examples](#14-complete-examples)

---

## 1. Introduction

### What is realTinyTalk?

realTinyTalk is a general-purpose programming language designed for clarity and friendliness. Inspired by Smalltalk's elegance and dplyr's data pipelines, realTinyTalk removes unnecessary ceremony while maintaining expressive power.

### Design Philosophy

1. **Readable over clever** — Code should read like English
2. **Minimal symbols** — Fewer brackets, fewer sigils
3. **Safe by default** — Bounded loops, recursion limits, null safety
4. **Auto-coercion** — Types convert when intent is clear

### Hello World

```tinytalk
show("Hello, World!")
```

That's it. No imports, no main function, no semicolons required.

### The Friendliest Syntax

realTinyTalk has **space-separated arguments** — no commas or `+` needed:

```tinytalk
let name = "Alice"
let age = 25

show("Hello" name)              // Hello Alice
show("You are" age "years old")  // You are 25 years old
```

Compare to other languages:
```python
# Python
print(f"Hello {name}")
print("You are", age, "years old")
```

realTinyTalk reads like English.

---

## 2. Getting Started

### The Web IDE

Open http://localhost:5555 to access the realTinyTalk IDE with:
- Syntax highlighting with 4 beautiful themes (Dark, Light, Monokai, Nord)
- Curated example programs
- Instant execution (Ctrl+Enter)
- Theme preference saved automatically

### Running Programs

**From the IDE:**
Write code and press `Ctrl+Enter` or click Run.

**From command line:**
```bash
python -m realTinyTalk run program.tt
```

### Comments

```tinytalk
// This is a single-line comment

/* This is a
   multi-line comment */
```

---

## Quick Tutorial: Learn realTinyTalk in 5 Minutes

### Lesson 1: Hello World

```tinytalk
show("Hello World!")
```

That's it! `show()` prints to the screen.

### Lesson 2: Variables

```tinytalk
let name = "Alice"          // Mutable variable
when PI = 3.14159           // Immutable constant

name = "Bob"                // OK - let can change
// PI = 3.0                 // ERROR - when cannot change
```

### Lesson 3: Printing with show()

tinyTalk's `show()` is special — space-separated args, no commas needed:

```tinytalk
let name = "Newton"
let age = 384

// These all work:
show("Hello" name)                  // Hello Newton
show(name "is" age "years old")     // Newton is 384 years old

// For expressions, use a variable or parentheses after a space
let sum = 1 + 2
show("1 + 2 =" sum)                 // 1 + 2 = 3
```

### Lesson 4: Property Conversions

No need for `str()` or `int()` functions — use properties:

```tinytalk
let num = 42
let text = "3.14"

show(num.str)       // "42"
show(num.type)      // "int"
show(text.num)      // 3.14
show(text.int)      // 3

// String properties
let s = "  HELLO  "
show(s.trim)        // "HELLO"
show(s.lowcase)     // "  hello  "
show(s.len)         // 9
show(s.reversed)    // "  OLLEH  "
```

### Lesson 5: Functions

Two types: `law` (pure) and `forge` (with side effects):

```tinytalk
// LAW - pure function, no side effects
law square(x)
    reply x * x
end

// FORGE - action, can have side effects
forge greet(name)
    show("Hello" name "!")
end

show(square(5))     // 25
greet("World")      // Hello World !
```

### Lesson 6: Control Flow

```tinytalk
// If statement
if age >= 18 {
    show("Adult")
} else {
    show("Minor")
}

// For loop
for i in range(5) {
    show(i)         // 0, 1, 2, 3, 4
}

// While loop
let x = 1
while x < 10 {
    show(x)
    x = x * 2
}
```

### Lesson 7: Collections

```tinytalk
// Lists
let fruits = ["apple", "banana", "cherry"]
show(fruits[0])         // apple
show(fruits.first)      // apple
show(fruits.last)       // cherry

// Maps
let person = {"name": "Alice", "age": 30}
show(person.name)       // Alice
show(person["age"])     // 30
```

**You're ready!** Explore the examples in the IDE for more.

---

## 3. Values and Types

### Primitive Types

| Type | Examples | Description |
|------|----------|-------------|
| `int` | `42`, `-7`, `0` | Arbitrary precision integers |
| `float` | `3.14`, `-0.5`, `1e10` | 64-bit floating point |
| `string` | `"hello"`, `'world'` | UTF-8 text |
| `bool` | `true`, `false` | Boolean values |
| `null` | `null` | Absence of value |

### Integers

```tinytalk
let small = 42
let big = 2 ** 100          // Arbitrary precision
let negative = -17
let hex = 0xFF              // 255
```

### Floats

```tinytalk
let pi = 3.14159
let tiny = 1e-10
let huge = 1e100
```

### Strings

```tinytalk
let greeting = "Hello"
let name = 'Alice'          // Single or double quotes

// Escape sequences
let multiline = "Line 1\nLine 2"
let tabbed = "Col1\tCol2"
let quoted = "She said \"Hi\""
```

### Booleans

```tinytalk
let yes = true
let no = false
```

### Null

```tinytalk
let nothing = null
```

---

## 4. Variables and Constants

### Mutable Variables (let)

Use `let` for values that may change:

```tinytalk
let count = 0
count = count + 1       // OK
count = 10              // OK
```

### Immutable Constants (when)

Use `when` for facts that never change:

```tinytalk
when PI = 3.14159
when GRAVITY = 9.81
when APP_NAME = "MyApp"

// PI = 3.0             // ERROR: Cannot reassign constant
```

**When to use which:**
- `when` — Configuration, mathematical constants, known facts
- `let` — Counters, accumulators, state that changes

---

## 5. Operators

### Arithmetic

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `5 + 3` → `8` |
| `-` | Subtraction | `5 - 3` → `2` |
| `*` | Multiplication | `5 * 3` → `15` |
| `/` | Division | `5 / 2` → `2.5` |
| `//` | Integer division | `5 // 2` → `2` |
| `%` | Modulo | `5 % 2` → `1` |
| `**` | Exponentiation | `2 ** 8` → `256` |

### Comparison

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equal | `5 == 5` → `true` |
| `!=` | Not equal | `5 != 3` → `true` |
| `<` | Less than | `3 < 5` → `true` |
| `>` | Greater than | `5 > 3` → `true` |
| `<=` | Less or equal | `3 <= 3` → `true` |
| `>=` | Greater or equal | `5 >= 5` → `true` |

**Note:** Float comparison uses tolerance. `0.1 + 0.2 == 0.3` is `true`.

### Logical

| Operator | Description | Example |
|----------|-------------|---------|
| `and` | Logical AND | `true and false` → `false` |
| `or` | Logical OR | `true or false` → `true` |
| `not` | Logical NOT | `not true` → `false` |

### String Concatenation

```tinytalk
let full = "Hello" + " " + "World"    // "Hello World"
let repeated = "ha" * 3                // "hahaha"
```

### Compound Assignment

```tinytalk
let x = 10
x += 5      // x = 15
x -= 3      // x = 12
x *= 2      // x = 24
x /= 4      // x = 6
```

### Ternary Operator

```tinytalk
let status = age >= 18 ? "adult" : "minor"
```

---

## Natural Comparisons

realTinyTalk includes natural-language comparison operators that read like English:

### is / isnt — Natural Equality

```tinytalk
let name = "Alice"

show(name is "Alice")      // true
show(name isnt "Bob")      // true
show(5 is 5)               // true
show(5 isnt 6)             // true
```

### has / hasnt — Container Checks

Check if a collection contains an element:

```tinytalk
let numbers = [1, 2, 3, 4, 5]
let text = "Hello World"

show(numbers has 3)        // true
show(numbers hasnt 99)     // true
show(text has "World")     // true
show(text hasnt "Goodbye") // true
```

### isin — Element Membership

Check if an element is in a collection (reverse of `has`):

```tinytalk
let numbers = [1, 2, 3, 4, 5]

show(3 isin numbers)       // true
show(99 isin numbers)      // false
```

### islike — Pattern Matching

Match strings with wildcards (`*` for any chars, `?` for single char):

```tinytalk
show("Alice" islike "A*")      // true  (starts with A)
show("Alice" islike "*ice")    // true  (ends with ice)
show("Alice" islike "Al?ce")   // true  (? = any char)
show("Bob" islike "A*")        // false
```

---

## Step Chains

realTinyTalk's killer feature: **dplyr-style data pipelines** using underscore-prefixed steps!

Chain operations together for clean, readable data manipulation:

```tinytalk
let numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]

// Chain: sort, reverse, take top 3
let top3 = numbers _sort _reverse _take(3)
show(top3)  // [9, 8, 7]
```

### Available Steps

| Step | Description | Example |
|------|-------------|---------|
| `_sort` | Sort ascending | `[3,1,2] _sort` → `[1,2,3]` |
| `_reverse` | Reverse order | `[1,2,3] _reverse` → `[3,2,1]` |
| `_take(n)` | Take first n | `[1,2,3,4] _take(2)` → `[1,2]` |
| `_drop(n)` | Drop first n | `[1,2,3,4] _drop(2)` → `[3,4]` |
| `_first` | First element | `[1,2,3] _first` → `1` |
| `_last` | Last element | `[1,2,3] _last` → `3` |
| `_unique` | Remove duplicates | `[1,1,2,2] _unique` → `[1,2]` |
| `_flatten` | Flatten nested | `[[1,2],[3]] _flatten` → `[1,2,3]` |

### Aggregation Steps

| Step | Description | Example |
|------|-------------|---------|
| `_count` | Count elements | `[1,2,3] _count` → `3` |
| `_sum` | Sum all | `[1,2,3] _sum` → `6` |
| `_avg` | Average | `[1,2,3] _avg` → `2` |
| `_min` | Minimum | `[3,1,2] _min` → `1` |
| `_max` | Maximum | `[3,1,2] _max` → `3` |

### Transform Steps

| Step | Description | Example |
|------|-------------|---------|
| `_filter(fn)` | Keep matching | `[1,2,3,4] _filter(is_even)` |
| `_map(fn)` | Transform each | `[1,2,3] _map(double)` |
| `_group(fn)` | Group by key | `[1,2,3,4] _group(is_even)` |
| `_chunk(n)` | Split into chunks | `[1,2,3,4] _chunk(2)` |
| `_zip(list)` | Pair with another | `[1,2] _zip([3,4])` |

### Complete Example

```tinytalk
let data = [5, 2, 8, 1, 9, 3, 7, 4, 6]

// Define filter function
law is_big(x)
    reply x > 3
end

// Define transform function  
law squared(x)
    reply x * x
end

// Pipeline: filter big numbers, sort, square them, sum
let result = data _filter(is_big) _sort _map(squared) _sum
show(result)  // 5² + 6² + 7² + 8² + 9² = 255

// Quick stats
show("Count:" data _count)
show("Sum:" data _sum)
show("Avg:" data _avg)
show("Min:" data _min)
show("Max:" data _max)
```

---

## 6. Control Flow

### If Statements

```tinytalk
if condition {
    // code
}

if condition {
    // code
} else {
    // code
}

if condition1 {
    // code
} elif condition2 {
    // code
} else {
    // code
}
```

**Example:**

```tinytalk
let score = 85

if score >= 90 {
    show("A")
} elif score >= 80 {
    show("B")
} elif score >= 70 {
    show("C")
} else {
    show("F")
}
```

### For Loops

**Iterating over a range:**

```tinytalk
for i in range(5) {
    show(i)             // 0, 1, 2, 3, 4
}

for i in range(1, 6) {
    show(i)             // 1, 2, 3, 4, 5
}

for i in range(0, 10, 2) {
    show(i)             // 0, 2, 4, 6, 8
}

for i in range(5, 0, -1) {
    show(i)             // 5, 4, 3, 2, 1
}
```

**Iterating over collections:**

```tinytalk
let fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
    show(fruit)
}

let person = {"name": "Alice", "age": 30}
for key in person {
    show(key, "=", person[key])
}
```

### While Loops

```tinytalk
let count = 0
while count < 5 {
    show(count)
    count += 1
}
```

### Break and Continue

```tinytalk
// Break exits the loop
for i in range(10) {
    if i == 5 {
        break
    }
    show(i)         // 0, 1, 2, 3, 4
}

// Continue skips to next iteration
for i in range(5) {
    if i == 2 {
        continue
    }
    show(i)         // 0, 1, 3, 4
}
```

### Safety Limits

Loops are bounded to prevent infinite execution:

```tinytalk
// This will stop after 100,000 iterations
while true {
    // ...
}
// Error: Exceeded maximum iterations (100000)
```

---

## 7. Functions

tinyTalk has two kinds of functions:

| Keyword | Purpose | Side Effects | Best For |
|---------|---------|--------------|----------|
| `law` | Pure computation | None allowed | Math, transforms, queries |
| `forge` | Actions | Allowed | I/O, state changes, mutations |

### Pure Functions (law)

A `law` is a pure function — same inputs always produce same outputs:

```tinytalk
law square(x)
    reply x * x
end

law add(a, b)
    reply a + b
end

show(square(5))         // 25
show(add(3, 4))         // 7
```

**Early return:**

```tinytalk
law factorial(n)
    if n <= 1 { reply 1 }
    reply n * factorial(n - 1)
end
```

**Multiple parameters:**

```tinytalk
law greet(name, greeting)
    reply greeting + ", " + name + "!"
end

show(greet("Alice", "Hello"))   // "Hello, Alice!"
```

### Actions (forge)

A `forge` can have side effects like printing or modifying state:

```tinytalk
forge say_hello(name)
    show("Hello,", name)
    reply "greeted"
end

forge countdown(n)
    while n > 0 {
        show(n)
        n = n - 1
    }
    show("Liftoff!")
end

say_hello("World")
countdown(3)
```

### Higher-Order Functions

Functions are first-class values:

```tinytalk
law apply_twice(f, x)
    reply f(f(x))
end

law double(n)
    reply n * 2
end

show(apply_twice(double, 5))    // 20
```

### Closures

Functions capture their environment:

```tinytalk
law make_counter(start)
    let count = start
    forge increment()
        count = count + 1
        reply count
    end
    reply increment
end

let counter = make_counter(0)
show(counter())     // 1
show(counter())     // 2
show(counter())     // 3
```

### Recursion

```tinytalk
law fib(n)
    if n <= 1 { reply n }
    reply fib(n - 1) + fib(n - 2)
end

for i in range(10) {
    show("fib(" + i.str + ") =", fib(i))
}
```

Recursion is bounded to prevent stack overflow.

---

## 8. Collections

### Lists

**Creating lists:**

```tinytalk
let empty = []
let numbers = [1, 2, 3, 4, 5]
let mixed = [1, "two", 3.0, true]
let nested = [[1, 2], [3, 4]]
```

**Accessing elements:**

```tinytalk
let fruits = ["apple", "banana", "cherry"]

show(fruits[0])         // "apple"
show(fruits[-1])        // "cherry" (last element)
show(fruits[1])         // "banana"
```

**Modifying lists:**

```tinytalk
let nums = [1, 2, 3]
nums[0] = 10            // [10, 2, 3]
nums = nums + [4, 5]    // [10, 2, 3, 4, 5]
```

**List properties:**

```tinytalk
let items = [1, 2, 3, 4, 5]

show(items.len)         // 5
show(items.first)       // 1
show(items.last)        // 5
show(items.empty)       // false
show([].empty)          // true
```

### Maps (Dictionaries)

**Creating maps:**

```tinytalk
let empty = {}
let person = {"name": "Alice", "age": 30}
let config = {
    "host": "localhost",
    "port": 8080,
    "debug": true
}
```

**Accessing values:**

```tinytalk
let person = {"name": "Alice", "age": 30}

show(person["name"])    // "Alice"
show(person.name)       // "Alice" (dot notation)
show(person.city)       // null (missing key)
```

**Modifying maps:**

```tinytalk
let person = {"name": "Alice"}
person["age"] = 30      // Add new key
person.city = "NYC"     // Dot notation works too
```

**Map properties:**

```tinytalk
let data = {"a": 1, "b": 2}
show(data.len)          // 2
```

---

## 9. Property Conversions

tinyTalk provides property-style type conversions — no function calls needed:

### Type Conversions

| Property | Description | Example |
|----------|-------------|---------|
| `.str` | Convert to string | `42.str` → `"42"` |
| `.num` | Convert to number | `"3.14".num` → `3.14` |
| `.int` | Convert to integer | `"42".int` → `42` |
| `.float` | Convert to float | `"3.14".float` → `3.14` |
| `.bool` | Convert to boolean | `1.bool` → `true` |
| `.type` | Get type name | `42.type` → `"int"` |

**Examples:**

```tinytalk
let num = 42
let text = "3.14"

show(num.str)           // "42"
show(num.type)          // "int"
show(text.num)          // 3.14
show(text.int)          // 3
show(0.bool)            // false
show(1.bool)            // true
show("".bool)           // false
show("hello".bool)      // true
```

### String Properties

| Property | Description | Example |
|----------|-------------|---------|
| `.len` | Length | `"hello".len` → `5` |
| `.upper` | Uppercase | `"hello".upper` → `"HELLO"` |
| `.lower` | Lowercase | `"HELLO".lower` → `"hello"` |
| `.trim` | Remove whitespace | `"  hi  ".trim` → `"hi"` |

**Chaining:**

```tinytalk
let messy = "  HELLO WORLD  "
show(messy.trim.lowcase)    // "hello world"
```

### List Properties

| Property | Description | Example |
|----------|-------------|---------|
| `.len` | Length | `[1,2,3].len` → `3` |
| `.first` | First element | `[1,2,3].first` → `1` |
| `.last` | Last element | `[1,2,3].last` → `3` |
| `.empty` | Is empty? | `[].empty` → `true` |

### String Concatenation with .str

```tinytalk
let age = 25
show("I am " + age.str + " years old")
```

---

## String Properties

realTinyTalk provides rich string manipulation through properties:

### Case Conversion

| Property | Description | Example |
|----------|-------------|---------|
| `.upcase` | All uppercase | `"hello".upcase` → `"HELLO"` |
| `.lowcase` | All lowercase | `"HELLO".lowcase` → `"hello"` |

### Splitting

| Property | Description | Example |
|----------|-------------|---------|
| `.chars` | Split to characters | `"abc".chars` → `["a","b","c"]` |
| `.words` | Split by spaces | `"hello world".words` → `["hello","world"]` |
| `.lines` | Split by newlines | `"a\nb".lines` → `["a","b"]` |

### Transformations

| Property | Description | Example |
|----------|-------------|---------|
| `.reversed` | Reverse string | `"hello".reversed` → `"olleh"` |
| `.trim` | Remove whitespace | `"  hi  ".trim` → `"hi"` |
| `.len` | Length | `"hello".len` → `5` |

### Complete Example

```tinytalk
let text = "  Hello World  "

show("Original:" text)
show("Trimmed:" text.trim)
show("Uppercase:" text.upcase)
show("Lowercase:" text.lowcase)
show("Reversed:" text.reversed)
show("Length:" text.len)

// Split and manipulate
let words = text.trim.words
show("Words:" words)
show("First word:" words.first)
show("Word count:" words _count)

// Combine with step chains!
let chars = "hello".chars
show("Sorted chars:" chars _sort)
show("Unique chars:" "mississippi".chars _unique _sort)
```

---

## 10. Blueprints (Classes)

### Defining a Blueprint

```tinytalk
blueprint Point
    field x
    field y
    
    law distance_from_origin()
        reply (self.x ** 2 + self.y ** 2) ** 0.5
    end
    
    law move(dx, dy)
        reply Point(self.x + dx, self.y + dy)
    end
end
```

### Creating Instances

```tinytalk
let p = Point(3, 4)
show(p.x)                       // 3
show(p.y)                       // 4
show(p.distance_from_origin())  // 5.0

let p2 = p.move(1, 1)
show(p2.x, p2.y)               // 4 5
```

### Complete Example

```tinytalk
blueprint Rectangle
    field width
    field height
    
    law area()
        reply self.width * self.height
    end
    
    law perimeter()
        reply 2 * (self.width + self.height)
    end
    
    law is_square()
        reply self.width == self.height
    end
end

let rect = Rectangle(10, 5)
show("Area:", rect.area())           // 50
show("Perimeter:", rect.perimeter()) // 30
show("Square?", rect.is_square())    // false

let square = Rectangle(5, 5)
show("Square?", square.is_square())  // true
```

---

## 11. Built-in Functions

### Output

| Function | Description |
|----------|-------------|
| `show(args...)` | Print values with spaces, newline at end |

**Space-separated arguments (preferred):**
```tinytalk
show("Hello" name)          // Hello Alice
show("x =" 42)               // x = 42
show(1 2 3)                  // 1 2 3
show("Sum:" a "+" b "=" (a + b))  // Sum: 3 + 4 = 7
```

**Comma-separated also works:**
```tinytalk
show("Hello", name)         // Hello Alice
show("x =", 42)              // x = 42
```

No `+` or `.str` needed — `show()` auto-converts everything!

### Type Functions

| Function | Description |
|----------|-------------|
| `type(x)` | Get type as string |
| `int(x)` | Convert to integer |
| `float(x)` | Convert to float |
| `str(x)` | Convert to string |
| `bool(x)` | Convert to boolean |

### Math Functions

| Function | Description |
|----------|-------------|
| `abs(x)` | Absolute value |
| `min(a, b)` | Minimum |
| `max(a, b)` | Maximum |
| `round(x)` | Round to nearest integer |
| `floor(x)` | Round down |
| `ceil(x)` | Round up |

### Collection Functions

| Function | Description |
|----------|-------------|
| `len(x)` | Length of string, list, or map |
| `range(n)` | List [0, 1, ..., n-1] |
| `range(a, b)` | List [a, a+1, ..., b-1] |
| `range(a, b, step)` | List with step |
| `keys(map)` | List of map keys |
| `values(map)` | List of map values |

### String Functions

| Function | Description |
|----------|-------------|
| `split(s, sep)` | Split string by separator |
| `join(list, sep)` | Join list with separator |
| `replace(s, old, new)` | Replace substring |

---

## 12. Error Handling

### Common Errors

**Division by zero:**
```tinytalk
show(1 / 0)
// Error: Division by zero
```

**Index out of bounds:**
```tinytalk
let list = [1, 2, 3]
show(list[10])
// Error: Index 10 out of bounds
```

**Undefined variable:**
```tinytalk
show(undefined_var)
// Error: Undefined variable 'undefined_var'
```

**Null arithmetic:**
```tinytalk
show(null + 1)
// Error: Cannot perform arithmetic on null
```

**Constant reassignment:**
```tinytalk
when X = 10
X = 20
// Error: Cannot reassign constant 'X'
```

### Result Pattern

For recoverable errors, return a result object:

```tinytalk
law safe_divide(a, b)
    if b == 0 {
        reply {"ok": false, "error": "division by zero"}
    }
    reply {"ok": true, "value": a / b}
end

let result = safe_divide(10, 0)
if result.ok {
    show("Result:", result.value)
} else {
    show("Error:", result.error)
}
```

---

## 13. Style Guide

### Naming Conventions

```tinytalk
// Variables and functions: snake_case
let user_count = 0
law calculate_total(items)

// Constants: UPPER_SNAKE_CASE
when MAX_RETRIES = 3
when API_URL = "https://api.example.com"

// Blueprints: PascalCase
blueprint UserAccount
blueprint HttpRequest
```

### Indentation

Use 4 spaces for indentation:

```tinytalk
law process(items)
    for item in items {
        if item.valid {
            show(item)
        }
    }
end
```

### Line Length

Keep lines under 80 characters when practical.

### Comments

```tinytalk
// Use comments to explain WHY, not WHAT
// Bad: increment counter
// Good: retry after transient failure
count += 1
```

### Function Design

- `law` for pure computations (math, transforms, queries)
- `forge` for side effects (I/O, mutations)
- Keep functions small and focused
- Use descriptive names

---

## 14. Complete Examples

### FizzBuzz

```tinytalk
law fizzbuzz(n)
    if n % 15 == 0 { reply "FizzBuzz" }
    if n % 3 == 0 { reply "Fizz" }
    if n % 5 == 0 { reply "Buzz" }
    reply n
end

for i in range(1, 21) {
    show(fizzbuzz(i))
}
```

### Prime Numbers

```tinytalk
law is_prime(n)
    if n < 2 { reply false }
    for i in range(2, n) {
        if n % i == 0 { reply false }
    }
    reply true
end

show("Primes up to 50:")
for n in range(2, 51) {
    if is_prime(n) {
        show(n)
    }
}
```

### Quicksort

```tinytalk
law quicksort(arr)
    if arr.len <= 1 { reply arr }
    
    let pivot = arr[0]
    let less = []
    let greater = []
    
    for i in range(1, arr.len) {
        if arr[i] < pivot {
            less = less + [arr[i]]
        } else {
            greater = greater + [arr[i]]
        }
    }
    
    reply quicksort(less) + [pivot] + quicksort(greater)
end

let unsorted = [64, 34, 25, 12, 22, 11, 90]
show("Before:", unsorted)
show("After:", quicksort(unsorted))
```

### Binary Tree Sum

```tinytalk
// Trees as nested maps
let tree = {
    "value": 10,
    "left": {
        "value": 5,
        "left": {"value": 2, "left": null, "right": null},
        "right": {"value": 7, "left": null, "right": null}
    },
    "right": {
        "value": 15,
        "left": null,
        "right": {"value": 20, "left": null, "right": null}
    }
}

law tree_sum(node)
    if node == null { reply 0 }
    reply node.value + tree_sum(node.left) + tree_sum(node.right)
end

show("Tree sum:", tree_sum(tree))   // 59
```

### Simple Calculator

```tinytalk
law add(a, b)      reply a + b end
law subtract(a, b) reply a - b end
law multiply(a, b) reply a * b end

law divide(a, b)
    if b == 0 { reply {"error": "division by zero"} }
    reply a / b
end

show("Calculator Demo:")
show("10 + 5 =", add(10, 5))
show("10 - 5 =", subtract(10, 5))
show("10 * 5 =", multiply(10, 5))
show("10 / 5 =", divide(10, 5))
show("10 / 0 =", divide(10, 0))
```

### Word Counter

```tinytalk
law count_words(text)
    let words = {}
    let current = ""
    
    for char in text + " " {
        if char == " " or char == "\n" {
            if current.len > 0 {
                let word = current.lower
                if words[word] == null {
                    words[word] = 0
                }
                words[word] = words[word] + 1
                current = ""
            }
        } else {
            current = current + char
        }
    }
    
    reply words
end

let text = "the quick brown fox jumps over the lazy dog the fox"
let counts = count_words(text)
show("Word counts:", counts)
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════╗
║                  tinyTalk Quick Reference                     ║
╠═══════════════════════════════════════════════════════════════╣
║ VARIABLES                                                     ║
║   let x = 10          Mutable variable                        ║
║   when Y = 20         Immutable constant                      ║
║                                                               ║
║ TYPES                                                         ║
║   42, 3.14, "hi", true, false, null, [], {}                  ║
║                                                               ║
║ OPERATORS                                                     ║
║   + - * / // % **     Arithmetic                              ║
║   == != < > <= >=     Comparison                              ║
║   and or not          Logical                                 ║
║   ? :                 Ternary                                 ║
║                                                               ║
║ CONTROL FLOW                                                  ║
║   if cond { } elif { } else { }                               ║
║   for x in collection { }                                     ║
║   while cond { }                                              ║
║   break, continue                                             ║
║                                                               ║
║ FUNCTIONS                                                     ║
║   law name(args)      Pure function                           ║
║       reply value                                             ║
║   end                                                         ║
║                                                               ║
║   forge name(args)    Action (side effects OK)                ║
║       reply value                                             ║
║   end                                                         ║
║                                                               ║
║ PROPERTY CONVERSIONS                                          ║
║   x.str  x.int  x.float  x.bool  x.type                      ║
║   s.len  s.upper  s.lower  s.trim                            ║
║   list.len  list.first  list.last  list.empty                ║
║                                                               ║
║ COLLECTIONS                                                   ║
║   [1, 2, 3]           List                                    ║
║   {"a": 1, "b": 2}    Map                                     ║
║   list[0]  list[-1]   Indexing                                ║
║   map.key  map["key"] Map access                              ║
║                                                               ║
║ OUTPUT                                                        ║
║   show(a, b, c)       Print with spaces                       ║
║                                                               ║
║ BLUEPRINTS                                                    ║
║   blueprint Name                                              ║
║       field x                                                 ║
║       law method() reply self.x end                          ║
║   end                                                         ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Appendix: Reserved Words

```
and       blueprint   break     continue   elif
else      end         false     field      for
forge     if          in        law        let
not       null        or        reply      self
super     true        when      while
```

---

*tinyTalk — Write code that reads like prose.*
