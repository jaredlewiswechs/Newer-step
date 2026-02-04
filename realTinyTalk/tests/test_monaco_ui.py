#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
MONACO UI TEST BOT
Automated testing of the realTinyTalk web IDE
═══════════════════════════════════════════════════════════════════════════════
"""

import requests
import json
import time
import sys
from dataclasses import dataclass
from typing import Optional, List, Tuple

BASE_URL = "http://localhost:5555"

@dataclass
class TestCase:
    """A single test case for the Monaco UI."""
    name: str
    code: str
    expected_output: Optional[str] = None  # Expected in output
    expected_contains: Optional[List[str]] = None  # Output should contain all
    expected_result: Optional[str] = None  # Final result value
    should_succeed: bool = True
    js_should_contain: Optional[List[str]] = None  # JS transpile checks
    py_should_contain: Optional[List[str]] = None  # Python transpile checks


# ═══════════════════════════════════════════════════════════════════════════════
# TEST CASES
# ═══════════════════════════════════════════════════════════════════════════════

TEST_CASES = [
    # ── Hello World & Basics ──
    TestCase(
        name="Hello World",
        code='show("Hello World!")',
        expected_contains=["Hello World!"],
        js_should_contain=['tt.show("Hello World!")'],
        py_should_contain=['tt.show("Hello World!")']
    ),
    
    TestCase(
        name="Variable Declaration",
        code='let name = "Newton"\nshow(name)',
        expected_contains=["Newton"],
        js_should_contain=['let name = "Newton"'],
        py_should_contain=['name = "Newton"']
    ),
    
    TestCase(
        name="Multiple Args (no commas)",
        code='show("Hello" "World" 42)',
        expected_contains=["Hello", "World", "42"],
    ),
    
    # ── Properties ──
    TestCase(
        name=".upcase Property",
        code='show("hello".upcase)',
        expected_contains=["HELLO"],
        js_should_contain=['.toUpperCase()'],
        py_should_contain=['.upper()']
    ),
    
    TestCase(
        name=".lowcase Property",
        code='show("HELLO".lowcase)',
        expected_contains=["hello"],
    ),
    
    TestCase(
        name=".len Property",
        code='show("hello".len)',
        expected_contains=["5"],
        js_should_contain=['.length'],
        py_should_contain=['len(']
    ),
    
    TestCase(
        name=".reversed Property",
        code='show("hello".reversed)',
        expected_contains=["olleh"],
    ),
    
    TestCase(
        name=".trim Property",
        code='show("  hello  ".trim)',
        expected_contains=["hello"],
    ),
    
    TestCase(
        name=".str Conversion",
        code='let n = 42\nshow(n.str)',
        expected_contains=["42"],
        py_should_contain=['str(']
    ),
    
    # ── Arrays ──
    TestCase(
        name="Array Literal",
        code='let nums = [1, 2, 3]\nshow(nums)',
        expected_contains=["1", "2", "3"],
        js_should_contain=['[1, 2, 3]'],
        py_should_contain=['[1, 2, 3]']
    ),
    
    TestCase(
        name="Array Index",
        code='let nums = [10, 20, 30]\nshow(nums[1])',
        expected_contains=["20"],
    ),
    
    TestCase(
        name="Array .first",
        code='show([5, 10, 15].first)',
        expected_contains=["5"],
    ),
    
    TestCase(
        name="Array .last",
        code='show([5, 10, 15].last)',
        expected_contains=["15"],
    ),
    
    # ── Step Chains ──
    TestCase(
        name="_sort Step",
        code='show([3, 1, 4, 1, 5] _sort)',
        expected_contains=["1", "1", "3", "4", "5"],
        js_should_contain=['.sort('],
        py_should_contain=['sort()'] 
    ),
    
    TestCase(
        name="_reverse Step",
        code='show([1, 2, 3] _reverse)',
        expected_contains=["3", "2", "1"],
    ),
    
    TestCase(
        name="_sum Terminal",
        code='show([1, 2, 3, 4, 5] _sum)',
        expected_contains=["15"],
    ),
    
    TestCase(
        name="_take Step",
        code='show([1, 2, 3, 4, 5] _take(3))',
        expected_contains=["1", "2", "3"],
    ),
    
    TestCase(
        name="_unique Step",
        code='show([1, 1, 2, 2, 3] _unique)',
        expected_contains=["1", "2", "3"],
    ),
    
    TestCase(
        name="Chained Steps",
        code='show([5, 2, 8, 1, 9] _sort _reverse _take(3))',
        expected_contains=["9", "8", "5"],
    ),
    
    # ── Arithmetic ──
    TestCase(
        name="Addition",
        code='show(2 + 3)',
        expected_contains=["5"],
    ),
    
    TestCase(
        name="All Operators",
        code='show(10 + 5)\nshow(10 - 5)\nshow(10 * 5)\nshow(10 / 5)\nshow(10 % 3)\nshow(2 ** 3)',
        expected_contains=["15", "5", "50", "2", "1", "8"],
    ),
    
    # ── Comparisons ──
    TestCase(
        name="Comparison Operators",
        code='show(5 > 3)\nshow(5 < 3)\nshow(5 == 5)\nshow(5 != 3)',
        expected_contains=["true", "false", "true", "true"],
    ),
    
    # ── TinyTalk Operators ──
    TestCase(
        name="is Operator",
        code='show(5 is 5)\nshow("hello" is "hello")',
        expected_contains=["true", "true"],
        js_should_contain=['tt.is('],
        py_should_contain=['tt.is_(']
    ),
    
    TestCase(
        name="has Operator (dict)",
        code='let person = {"name": "Alice", "age": 30}\nshow(person has "name")',
        expected_contains=["true"],
    ),
    
    TestCase(
        name="has Operator (array)",
        code='let nums = [1, 2, 3]\nshow(nums has 2)',
        expected_contains=["true"],
    ),
    
    TestCase(
        name="islike Operator",
        code='show("hello.txt" islike "*.txt")\nshow("hello.py" islike "*.txt")',
        expected_contains=["true", "false"],
        js_should_contain=['tt.islike('],
        py_should_contain=['tt.islike(']
    ),
    
    # ── Control Flow ──
    TestCase(
        name="If Statement",
        code='if 5 > 3 {\n  show("yes")\n}',
        expected_contains=["yes"],
    ),
    
    TestCase(
        name="If-Else Statement",
        code='if 5 < 3 {\n  show("yes")\n} else {\n  show("no")\n}',
        expected_contains=["no"],
    ),
    
    TestCase(
        name="For Loop",
        code='for i in range(3) {\n  show(i)\n}',
        expected_contains=["0", "1", "2"],
    ),
    
    TestCase(
        name="While Loop",
        code='let i = 0\nwhile i < 3 {\n  show(i)\n  i = i + 1\n}',
        expected_contains=["0", "1", "2"],
    ),
    
    TestCase(
        name="For-in Array",
        code='for x in [10, 20, 30] {\n  show(x)\n}',
        expected_contains=["10", "20", "30"],
    ),
    
    # ── Functions ──
    TestCase(
        name="Function Definition",
        code='fn greet(name) {\n  return "Hello " + name\n}\nshow(greet("World"))',
        expected_contains=["Hello World"],
    ),
    
    TestCase(
        name="Law Definition",
        code='law double(x)\n  x * 2\nend\nshow(double(5))',
        expected_contains=["10"],
    ),
    
    TestCase(
        name="Fibonacci",
        code='fn fib(n) {\n  if n <= 1 { return n }\n  return fib(n-1) + fib(n-2)\n}\nshow(fib(10))',
        expected_contains=["55"],
    ),
    
    # ── Structs ──
    TestCase(
        name="Object/Map Literal",
        code='let person = {"name": "Alice", "age": 30}\nshow(person["name"])\nshow(person["age"])',
        expected_contains=["Alice", "30"],
    ),
    
    # ── Complex Examples ──
    TestCase(
        name="FizzBuzz",
        code='''for i in range(1, 6) {
  if i % 3 == 0 {
    show("Fizz")
  } else {
    show(i)
  }
}''',
        expected_contains=["1", "2", "Fizz", "4", "5"],
    ),
    
    TestCase(
        name="Pipeline Processing",
        code='let data = [5, 2, 8, 1, 9, 3, 7, 4, 6]\nlet result = data _sort _reverse _take(5) _sum\nshow("Top 5 sum:" result)',
        expected_contains=["Top 5 sum:", "35"],
    ),
    
    # ── Error Cases ──
    TestCase(
        name="Syntax Error",
        code='let x = ',
        should_succeed=False,
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
# TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

class TestRunner:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.passed = 0
        self.failed = 0
        self.results: List[Tuple[str, bool, str]] = []
    
    def run_code(self, code: str) -> dict:
        """Run TinyTalk code via API."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/run",
                json={"code": code},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}
    
    def transpile_js(self, code: str) -> dict:
        """Transpile to JavaScript via API."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/transpile/js",
                json={"code": code, "include_runtime": True},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e), "code": ""}
    
    def transpile_python(self, code: str) -> dict:
        """Transpile to Python via API."""
        try:
            resp = requests.post(
                f"{self.base_url}/api/transpile/python",
                json={"code": code, "include_runtime": True},
                timeout=10
            )
            return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e), "code": ""}
    
    def test_case(self, tc: TestCase) -> bool:
        """Run a single test case."""
        errors = []
        
        # Test execution
        result = self.run_code(tc.code)
        
        if tc.should_succeed:
            if not result.get("success"):
                errors.append(f"Execution failed: {result.get('error')}")
            else:
                output = result.get("output", "")
                
                if tc.expected_output and tc.expected_output not in output:
                    errors.append(f"Expected output '{tc.expected_output}' not found")
                
                if tc.expected_contains:
                    for expected in tc.expected_contains:
                        if expected not in output:
                            errors.append(f"Expected '{expected}' not in output: {output[:100]}")
        else:
            if result.get("success"):
                errors.append("Expected failure but succeeded")
        
        # Test JS transpilation
        if tc.js_should_contain and tc.should_succeed:
            js_result = self.transpile_js(tc.code)
            if js_result.get("success"):
                js_code = js_result.get("code", "")
                for expected in tc.js_should_contain:
                    if expected not in js_code:
                        errors.append(f"JS: Expected '{expected}' not found")
            else:
                errors.append(f"JS transpile failed: {js_result.get('error')}")
        
        # Test Python transpilation
        if tc.py_should_contain and tc.should_succeed:
            py_result = self.transpile_python(tc.code)
            if py_result.get("success"):
                py_code = py_result.get("code", "")
                for expected in tc.py_should_contain:
                    if expected not in py_code:
                        errors.append(f"Python: Expected '{expected}' not found")
            else:
                errors.append(f"Python transpile failed: {py_result.get('error')}")
        
        passed = len(errors) == 0
        self.results.append((tc.name, passed, "; ".join(errors) if errors else ""))
        return passed
    
    def run_all(self, verbose: bool = True) -> Tuple[int, int]:
        """Run all test cases."""
        print("═" * 70)
        print("MONACO UI TEST BOT")
        print("═" * 70)
        print()
        
        # Check server is up
        try:
            requests.get(f"{self.base_url}/", timeout=5)
        except:
            print("❌ Server not running at", self.base_url)
            print("   Start with: python realTinyTalk/web/server.py")
            return 0, 1
        
        print(f"✓ Server running at {self.base_url}")
        print()
        
        categories = {}
        for tc in TEST_CASES:
            # Group by first word of name
            cat = tc.name.split()[0] if " " in tc.name else "General"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tc)
        
        for cat, tests in categories.items():
            print(f"── {cat} ──")
            for tc in tests:
                passed = self.test_case(tc)
                if passed:
                    self.passed += 1
                    if verbose:
                        print(f"  ✅ {tc.name}")
                else:
                    self.failed += 1
                    error_msg = self.results[-1][2]
                    print(f"  ❌ {tc.name}")
                    if verbose and error_msg:
                        print(f"     └─ {error_msg[:80]}")
            print()
        
        print("═" * 70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("═" * 70)
        
        return self.passed, self.failed
    
    def generate_report(self, filename: str = "test_report.json"):
        """Generate a JSON report of all tests."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "total_tests": len(TEST_CASES),
            "passed": self.passed,
            "failed": self.failed,
            "tests": [
                {"name": name, "passed": passed, "error": error}
                for name, passed, error in self.results
            ]
        }
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {filename}")
        return report


def demo_transpile_output():
    """Show sample transpiled output for verification."""
    print("\n" + "═" * 70)
    print("TRANSPILED OUTPUT SAMPLES")
    print("═" * 70)
    
    samples = [
        ('show("Hello!")', "Hello World"),
        ('let nums = [3,1,2] _sort\nshow(nums)', "Sort array"),
        ('show("test" islike "t*")', "islike operator"),
        ('let x = [1,2,3]\nshow(x has 2)', "has operator"),
    ]
    
    for code, name in samples:
        print(f"\n── {name} ──")
        print(f"TinyTalk: {code}")
        
        try:
            js = requests.post(f"{BASE_URL}/api/transpile/js", 
                             json={"code": code, "include_runtime": False}, timeout=5).json()
            py = requests.post(f"{BASE_URL}/api/transpile/python", 
                             json={"code": code, "include_runtime": False}, timeout=5).json()
            
            if js.get("success"):
                print(f"JavaScript:\n{js['code']}")
            else:
                print(f"JS Error: {js.get('error')}")
            
            if py.get("success"):
                print(f"Python:\n{py['code']}")
            else:
                print(f"Python Error: {py.get('error')}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    runner = TestRunner()
    passed, failed = runner.run_all(verbose=True)
    
    if "--report" in sys.argv:
        runner.generate_report()
    
    if "--demo" in sys.argv:
        demo_transpile_output()
    
    sys.exit(0 if failed == 0 else 1)
