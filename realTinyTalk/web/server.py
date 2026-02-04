"""
TinyTalk Web IDE Server
Monaco-powered editor with live execution
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, request, jsonify, send_from_directory
from realTinyTalk import run, ExecutionBounds
from realTinyTalk.runtime import TinyTalkError

app = Flask(__name__, static_folder='static')

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the main IDE page."""
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)

@app.route('/api/run', methods=['POST'])
def run_code():
    """Execute TinyTalk code and return results."""
    data = request.get_json()
    code = data.get('code', '')
    
    # Capture print output
    import io
    from contextlib import redirect_stdout
    
    stdout_capture = io.StringIO()
    
    start_time = time.time()
    
    try:
        bounds = ExecutionBounds(
            max_ops=1_000_000,
            max_iterations=100_000,
            max_recursion=500,
            timeout_seconds=10.0
        )
        
        with redirect_stdout(stdout_capture):
            result = run(code, bounds)
        
        elapsed = (time.time() - start_time) * 1000
        output = stdout_capture.getvalue()
        
        # Format result
        result_str = str(result) if result.type.value != 'null' else ''
        
        return jsonify({
            'success': True,
            'output': output,
            'result': result_str,
            'elapsed_ms': round(elapsed, 2)
        })
        
    except TinyTalkError as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': str(e),
            'output': stdout_capture.getvalue(),
            'elapsed_ms': round(elapsed, 2)
        })
    except SyntaxError as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"Syntax Error: {e}",
            'output': stdout_capture.getvalue(),
            'elapsed_ms': round(elapsed, 2)
        })
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'output': stdout_capture.getvalue(),
            'elapsed_ms': round(elapsed, 2)
        })


@app.route('/api/transpile/js', methods=['POST'])
def transpile_to_js():
    """Transpile TinyTalk code to JavaScript."""
    data = request.get_json()
    code = data.get('code', '')
    include_runtime = data.get('include_runtime', True)
    
    start_time = time.time()
    
    try:
        from realTinyTalk.lexer import Lexer
        from realTinyTalk.parser import Parser
        from realTinyTalk.backends.js.emitter import JSEmitter
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        emitter = JSEmitter(include_runtime=include_runtime)
        js_code = emitter.emit(ast)
        
        elapsed = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'code': js_code,
            'language': 'javascript',
            'elapsed_ms': round(elapsed, 2)
        })
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'elapsed_ms': round(elapsed, 2)
        })


@app.route('/api/transpile/python', methods=['POST'])
def transpile_to_python():
    """Transpile TinyTalk code to Python."""
    data = request.get_json()
    code = data.get('code', '')
    include_runtime = data.get('include_runtime', True)
    
    start_time = time.time()
    
    try:
        from realTinyTalk.lexer import Lexer
        from realTinyTalk.parser import Parser
        from realTinyTalk.backends.python.emitter import PythonEmitter
        
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        emitter = PythonEmitter(include_runtime=include_runtime)
        py_code = emitter.emit(ast)
        
        elapsed = (time.time() - start_time) * 1000
        
        return jsonify({
            'success': True,
            'code': py_code,
            'language': 'python',
            'elapsed_ms': round(elapsed, 2)
        })
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        return jsonify({
            'success': False,
            'error': f"{type(e).__name__}: {e}",
            'elapsed_ms': round(elapsed, 2)
        })


@app.route('/api/examples')
def get_examples():
    """Get example programs - using ultra-clean tinyTalk syntax."""
    examples = [
        {
            'name': '👋 Hello World',
            'code': '''// ═══════════════════════════════════════════════════════════
// Welcome to realTinyTalk!
// The friendliest programming language
// ═══════════════════════════════════════════════════════════

show("Hello World!")

// Space-separated args - no commas needed!
let name = "Newton"
show("Welcome" name "to realTinyTalk!")

// Property magic - no parentheses needed!
show("Uppercase:" name.upcase)
show("Length:" name.len)
show("Reversed:" name.reversed)'''
        },
        {
            'name': '📖 Tutorial: Basics',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 1: The Basics
// ═══════════════════════════════════════

// Variables with 'let'
let greeting = "Hello"
let number = 42
let pi = 3.14159

// show() prints anything - space-separated args
show("greeting:" greeting)
show("number:" number)
show("pi:" pi)

// Math just works
show("")
show("=== Math ===")
let sum = 2 + 3
let product = 10 * 4
let power = 2 ** 8
show("2 + 3 =" sum)
show("10 * 4 =" product)
show("2 ** 8 =" power)

// Strings
show("")
show("=== Strings ===")
let name = "Alice"
show("Hello" name "!")
show("Length:" name.len)
show("Uppercase:" name.upcase)
show("Reversed:" name.reversed)'''
        },
        {
            'name': '📖 Tutorial: Functions',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 2: Functions
// ═══════════════════════════════════════

// LAW = pure function (no side effects)
law square(x)
    reply x * x
end

law greet(name)
    reply "Hello " + name + "!"
end

show("square(5) =" square(5))
show(greet("World"))

// Functions can call functions
law sum_of_squares(a, b)
    reply square(a) + square(b)
end

show("sum_of_squares(3, 4) =" sum_of_squares(3, 4))

// Recursion works too
law factorial(n)
    if n <= 1 { reply 1 }
    reply n * factorial(n - 1)
end

show("")
show("=== Factorials ===")
for i in range(1, 8) {
    show(i.str + "! =" factorial(i))
}'''
        },
        {
            'name': '📖 Tutorial: Collections',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 3: Lists & Maps
// ═══════════════════════════════════════

// Lists
let fruits = ["apple", "banana", "cherry"]
show("Fruits:" fruits)
show("First:" fruits.first)
show("Last:" fruits.last)
show("Length:" fruits.len)

// Loop through lists
show("")
show("=== Each fruit ===")
for fruit in fruits {
    show("-" fruit)
}

// Maps (like dictionaries)
let person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

show("")
show("=== Person ===")
show("Name:" person.name)
show("Age:" person.age)
show("City:" person.city)

// Add to map
person.country = "USA"
show("Country:" person.country)'''
        },
        {
            'name': '📖 Tutorial: Control Flow',
            'code': '''// ═══════════════════════════════════════
// TUTORIAL 4: Control Flow
// ═══════════════════════════════════════

// If statements
let age = 25

if age >= 18 {
    show("You are an adult")
} else {
    show("You are a minor")
}

// For loops
show("")
show("=== Countdown ===")
for i in range(5, 0, -1) {
    show(i)
}
show("Liftoff!")

// While loops
show("")
show("=== Doubling ===")
let x = 1
while x < 100 {
    show(x)
    x = x * 2
}

// Break and continue
show("")
show("=== Skip evens, stop at 7 ===")
for i in range(10) {
    if i % 2 == 0 { continue }
    if i > 7 { break }
    show(i)
}'''
        },
        {
            'name': '🔧 Property Magic',
            'code': '''// Property conversions - no parentheses needed!
// .str   -> convert to string
// .int   -> convert to integer
// .float -> convert to float  
// .bool  -> convert to boolean
// .type  -> get type name
// .len   -> get length

let num = 42
let text = "3.14"

show("=== Type Conversions ===")
show("num.str:" num.str)
show("text.float:" text.float)
show("text.int:" text.int)
show("num.type:" num.type)

show("")
show("=== String Properties ===")
let msg = "  hello world  "
show("original:" msg)
show("trimmed:" msg.trim)
show("upcase:" msg.upcase)
show("lowcase:" msg.lowcase)
show("len:" msg.len)
show("reversed:" msg.reversed)

show("")
show("=== List Properties ===")
let items = [1, 2, 3, 4, 5]
show("items:" items)
show("first:" items.first)
show("last:" items.last)
show("empty:" items.empty)
show("len:" items.len)'''
        },
        {
            'name': '📜 when (Constants)',
            'code': '''// WHEN - Declares immutable facts
// (Cannot be changed after creation)

when PI = 3.14159
when GRAVITY = 9.81
when APP_NAME = "MyApp"

show("PI:" PI)
show("Gravity:" GRAVITY)
show("App:" APP_NAME)

// Calculate with constants
law circle_area(radius)
    reply PI * radius * radius
end

show("")
show("=== Circle Areas ===")
for r in range(1, 6) {
    show("radius" r "-> area" circle_area(r))
}

// Try uncommenting this - you'll get an error!
// PI = 3.0  // ERROR: Cannot reassign constant'''
        },
        {
            'name': '🔨 forge (Actions)',
            'code': '''// FORGE - Actions that can change state
// Use when you need side effects

forge greet(name)
    show("Hello" name "!")
    reply "greeted"
end

forge countdown(n)
    while n > 0 {
        show(n)
        n = n - 1
    }
    show("Liftoff!")
end

greet("World")
show("")
countdown(5)'''
        },
        {
            'name': '⚖️ when/do/finfr (NEW!)',
            'code': '''// The NEW way to define functions!
// when name(params)
//   do expression
// finfr  (fin for real!)

when square(x)
  do x * x
finfr

when double(x)
  do x * 2
finfr

when add(a, b)
  do a + b
finfr

show("square(5):" square(5))
show("double(21):" double(21))
show("add(10, 32):" add(10, 32))

// With conditionals
when factorial(n)
  if n <= 1 { do 1 }
  do n * factorial(n - 1)
finfr

show("")
show("=== Factorials ===")
for i in range(1, 8) {
    show(i.str "! =" factorial(i))
}

// when also works for constants!
when PI = 3.14159
show("")
show("PI =" PI)'''
        },
        {
            'name': '⚖️ law/reply/end (classic)',
            'code': '''// Classic function syntax (still works!)
// law name(params)
//   reply expression
// end

law square(x)
    reply x * x
end

law factorial(n)
    if n <= 1 { reply 1 }
    reply n * factorial(n - 1)
end

law is_even(n)
    reply n % 2 == 0
end

show("square(5):" square(5))
show("factorial(6):" factorial(6))
show("is_even(4):" is_even(4))
show("is_even(7):" is_even(7))'''
        },
        {
            'name': '🔢 Fibonacci',
            'code': '''// Fibonacci - clean and simple

law fib(n)
    if n <= 1 { reply n }
    reply fib(n - 1) + fib(n - 2)
end

show("=== Fibonacci Sequence ===")
for i in range(12) {
    show("fib(" i.str ") =" fib(i))
}'''
        },
        {
            'name': '🎯 FizzBuzz',
            'code': '''// The classic interview question

law fizzbuzz(n)
    if n % 15 == 0 { reply "FizzBuzz" }
    if n % 3 == 0 { reply "Fizz" }
    if n % 5 == 0 { reply "Buzz" }
    reply n
end

show("=== FizzBuzz 1-20 ===")
for i in range(1, 21) {
    show(fizzbuzz(i))
}'''
        },
        {
            'name': '🔍 Prime Numbers',
            'code': '''// Find prime numbers

law is_prime(n)
    if n < 2 { reply false }
    for i in range(2, n) {
        if n % i == 0 { reply false }
    }
    reply true
end

show("=== Primes up to 50 ===")
let primes = []
for n in range(2, 51) {
    if is_prime(n) {
        primes = primes + [n]
    }
}
show(primes)
show("")
show("Found" primes.len "primes")'''
        },
        {
            'name': '📊 Quicksort',
            'code': '''// Quicksort algorithm

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
show("Unsorted:" unsorted)
show("Sorted:" quicksort(unsorted))'''
        },
        {
            'name': '🧮 Calculator',
            'code': '''// Simple calculator with error handling

law add(a, b)
    reply a + b
end

law subtract(a, b)
    reply a - b
end

law multiply(a, b)
    reply a * b
end

law divide(a, b)
    if b == 0 { 
        reply {"error": "division by zero", "value": null}
    }
    reply {"error": null, "value": a / b}
end

show("=== Calculator ===")
show("10 + 5 =" add(10, 5))
show("10 - 5 =" subtract(10, 5))
show("10 * 5 =" multiply(10, 5))

let result = divide(10, 5)
show("10 / 5 =" result.value)

let bad = divide(10, 0)
show("10 / 0 =" bad.error)'''
        },
        {
            'name': '🔗 Step Chains (NEW!)',
            'code': '''// dplyr-style data manipulation
// Chain operations with _underscore steps!

let numbers = [5, 2, 8, 1, 9, 3, 7, 4, 6]
show("Numbers:" numbers)

// Chain multiple steps: sort, take top 3
let top3 = numbers _sort _reverse _take(3)
show("Top 3:" top3)

// Filter and count
law is_even(x)
    reply x % 2 == 0
end

let evens = numbers _filter(is_even)
show("Evens:" evens)
show("Even count:" numbers _filter(is_even) _count)

// Sum and average
show("Sum:" numbers _sum)
show("Average:" numbers _avg)
show("Min:" numbers _min)
show("Max:" numbers _max)

// Transform with _map
law doubled(x)
    reply x * 2
end

show("Doubled:" numbers _map(doubled))

// Combine operations: filter > 3, sort, take 3
show("")
show("=== Complex Chain ===")
law big(x)
    reply x > 3
end

let result = numbers _filter(big) _sort _take(3)
show("filter(>3) + sort + take(3):" result)'''
        },
        {
            'name': '💬 Natural Comparisons',
            'code': '''// Natural language comparisons!
// is, isnt, has, hasnt, isin, islike

let name = "Alice"
let numbers = [1, 2, 3, 4, 5]
let text = "Hello World"

// is / isnt - natural equality
show("=== is / isnt ===")
show("name is Alice:" (name is "Alice"))
show("name isnt Bob:" (name isnt "Bob"))
show("5 is 5:" (5 is 5))
show("5 isnt 6:" (5 isnt 6))

// has / hasnt - container checks
show("")
show("=== has / hasnt ===")
show("numbers has 3:" (numbers has 3))
show("numbers hasnt 99:" (numbers hasnt 99))
show("text has World:" (text has "World"))
show("text hasnt Goodbye:" (text hasnt "Goodbye"))

// isin - element membership
show("")
show("=== isin ===")
show("3 isin numbers:" (3 isin numbers))
show("99 isin numbers:" (99 isin numbers))

// islike - pattern matching (* and ?)
show("")
show("=== islike (wildcards) ===")
show("Alice islike A*:" ("Alice" islike "A*"))
show("Alice islike *ice:" ("Alice" islike "*ice"))
show("Alice islike Al?ce:" ("Alice" islike "Al?ce"))
show("Bob islike A*:" ("Bob" islike "A*"))'''
        },
        {
            'name': '✨ String Properties',
            'code': '''// String properties - no parentheses needed!

let msg = "  Hello World  "

show("=== String Properties ===")
show("original:" msg)
show("trimmed:" msg.trim)
show("upcase:" msg.upcase)
show("lowcase:" msg.lowcase)
show("reversed:" msg.reversed)
show("len:" msg.len)

// Split into parts
show("")
show("=== Split Operations ===")
let sentence = "the quick brown fox"
show("words:" sentence.words)
show("chars:" sentence.chars)

// Works with step chains!
show("")
show("=== String + Steps ===")
let words = sentence.words
show("first 2 words:" words _take(2))
show("sorted words:" words _sort)
show("unique chars:" sentence.chars _unique _sort)'''
        },
        {
            'name': '🏗️ Blueprints (OOP)',
            'code': '''// Blueprints = Classes in realTinyTalk
// Define types with fields and methods

blueprint Counter
    field value
    
    forge inc()
        self.value = self.value + 1
        reply self.value
    end
    
    forge add(n)
        self.value = self.value + n
        reply self.value
    end
    
    forge reset()
        self.value = 0
        reply self.value
    end
end

// Create instances
let c = Counter(0)
show("Initial:" c.value)

// Call methods
show("After inc():" c.inc())
show("After inc():" c.inc())
show("After add(10):" c.add(10))
show("After reset():" c.reset())

// Bound methods preserve self!
let increment = c.inc
show("Calling bound method:" increment())
show("Again:" increment())'''
        },
        {
            'name': '🔄 Higher-Order Functions',
            'code': '''// Pass functions to other functions!

let numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

// Define transforms
law doubled(x)
    reply x * 2
end

law squared(x)
    reply x * x
end

// Define predicates
law is_even(x)
    reply x % 2 == 0
end

law is_odd(x)
    reply x % 2 == 1
end

law greater_than_5(x)
    reply x > 5
end

show("=== Transform with _map ===")
show("Numbers:" numbers)
show("Doubled:" numbers _map(doubled))
show("Squared:" numbers _map(squared))

show("")
show("=== Filter with predicates ===")
show("Evens:" numbers _filter(is_even))
show("Odds:" numbers _filter(is_odd))

show("")
show("=== Chain them! ===")
// Filter to odds, square each, sum
let result = numbers _filter(is_odd) _map(squared) _sum
show("Sum of squared odds:" result)

// Filter >5, double, take 3
show("Big doubled top 3:" numbers _filter(greater_than_5) _map(doubled) _take(3))

show("")
show("=== Functions are values ===")
law apply_twice(func, x)
    reply func(func(x))
end

show("apply_twice(doubled, 3):" apply_twice(doubled, 3))
show("apply_twice(squared, 2):" apply_twice(squared, 2))'''
        },
    ]
    return jsonify(examples)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  realTinyTalk Web IDE")
    print("  The Verified General-Purpose Programming Language")
    print("  Every loop bounded. Every operation traced.")
    print("=" * 60 + "\n")
    print("Starting server at http://localhost:5555")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5555, debug=False, use_reloader=False, threaded=True)
