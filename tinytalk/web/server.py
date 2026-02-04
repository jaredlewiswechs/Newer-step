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
from tinytalk import run, ExecutionBounds
from tinytalk.runtime import TinyTalkError

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

@app.route('/api/examples')
def get_examples():
    """Get example programs."""
    examples = [
        {
            'name': 'Hello World',
            'code': 'println("Hello, TinyTalk!")'
        },
        {
            'name': 'Variables',
            'code': '''let x = 42
let y = 3.14
let name = "TinyTalk"

println("x = " + str(x))
println("y = " + str(y))
println("name = " + name)'''
        },
        {
            'name': 'Fibonacci',
            'code': '''fn fib(n) {
    if n <= 1 {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

println("Fibonacci sequence:")
for i in range(15) {
    println("fib(" + str(i) + ") = " + str(fib(i)))
}'''
        },
        {
            'name': 'FizzBuzz',
            'code': '''fn fizzbuzz(n) {
    if n % 15 == 0 {
        return "FizzBuzz"
    }
    if n % 3 == 0 {
        return "Fizz"
    }
    if n % 5 == 0 {
        return "Buzz"
    }
    return str(n)
}

println("FizzBuzz 1-20:")
for i in range(1, 21) {
    println(fizzbuzz(i))
}'''
        },
        {
            'name': 'Factorial',
            'code': '''fn factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

println("Factorials:")
for i in range(1, 11) {
    println(str(i) + "! = " + str(factorial(i)))
}'''
        },
        {
            'name': 'Prime Numbers',
            'code': '''fn is_prime(n) {
    if n < 2 {
        return false
    }
    let i = 2
    while i * i <= n {
        if n % i == 0 {
            return false
        }
        i = i + 1
    }
    return true
}

println("Prime numbers up to 50:")
for n in range(2, 51) {
    if is_prime(n) {
        println(n)
    }
}'''
        },
        {
            'name': 'Collections',
            'code': '''let numbers = [1, 2, 3, 4, 5]
let person = {"name": "Alice", "age": 30, "city": "NYC"}

println("List: " + str(numbers))
println("Length: " + str(len(numbers)))

println("")
println("Map: " + str(person))
println("Name: " + person["name"])
println("Age: " + str(person["age"]))'''
        },
        {
            'name': 'Loops',
            'code': '''// For loop with range
println("Counting 0-4:")
for i in range(5) {
    println("  " + str(i))
}

// For loop with list
println("")
println("Fruits:")
let fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
    println("  " + fruit)
}

// While loop
println("")
println("Powers of 2:")
let n = 1
while n < 100 {
    println("  " + str(n))
    n = n * 2
}'''
        },
        {
            'name': 'Quick Sort',
            'code': '''fn quicksort(arr) {
    if len(arr) <= 1 {
        return arr
    }
    
    let pivot = arr[0]
    let rest = slice(arr, 1, len(arr))
    
    let less = []
    let greater = []
    
    for x in rest {
        if x < pivot {
            append(less, x)
        } else {
            append(greater, x)
        }
    }
    
    return quicksort(less) + [pivot] + quicksort(greater)
}

let unsorted = [64, 34, 25, 12, 22, 11, 90, 5, 77, 30]
println("Unsorted: " + str(unsorted))

let sorted = quicksort(unsorted)
println("Sorted:   " + str(sorted))'''
        },
        {
            'name': 'Math Functions',
            'code': '''println("Math in TinyTalk")
println("================")

println("sqrt(16) = " + str(sqrt(16)))
println("pow(2, 10) = " + str(pow(2, 10)))
println("abs(-42) = " + str(abs(-42)))
println("floor(3.7) = " + str(floor(3.7)))
println("ceil(3.2) = " + str(ceil(3.2)))
println("round(3.5) = " + str(round(3.5)))

let nums = [1, 2, 3, 4, 5]
println("")
println("List: " + str(nums))
println("sum = " + str(sum(nums)))
println("min = " + str(min(nums)))
println("max = " + str(max(nums)))'''
        }
    ]
    return jsonify(examples)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    TinyTalk Web IDE                           ║
║                                                               ║
║  The Verified General-Purpose Programming Language            ║
║  Every loop bounded. Every operation traced.                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    print("Starting server at http://localhost:5555")
    print("Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5555, debug=True)
