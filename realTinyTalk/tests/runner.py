"""
═══════════════════════════════════════════════════════════════════════════════
realTinyTalk CONFORMANCE TEST RUNNER
v1.0 Test Suite - Locks language behavior for regression prevention
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import io
import re
import time
import traceback
from pathlib import Path
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import List, Optional, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from realTinyTalk import run
from realTinyTalk.runtime import TinyTalkError


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    expected: str
    actual: str
    error: Optional[str] = None
    time_ms: float = 0.0


@dataclass
class SuiteResult:
    """Result of a test suite."""
    name: str
    results: List[TestResult]
    time_ms: float = 0.0
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)


def parse_test_file(content: str) -> List[Tuple[str, str, str]]:
    """
    Parse a .tt test file.
    
    Format:
    // TEST: test name
    // EXPECT: expected output
    code here
    // END
    
    Returns list of (name, code, expected_output)
    """
    tests = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for TEST marker
        if line.startswith('// TEST:'):
            name = line[8:].strip()
            expected_lines = []
            code_lines = []
            
            i += 1
            # Collect EXPECT lines
            while i < len(lines) and lines[i].strip().startswith('// EXPECT:'):
                expected_lines.append(lines[i].strip()[10:].strip())
                i += 1
            
            # Also handle multi-line expects
            while i < len(lines) and lines[i].strip().startswith('//   '):
                expected_lines.append(lines[i].strip()[5:])
                i += 1
            
            # Collect code until END
            while i < len(lines) and not lines[i].strip().startswith('// END'):
                code_lines.append(lines[i])
                i += 1
            
            expected = '\n'.join(expected_lines)
            code = '\n'.join(code_lines)
            tests.append((name, code, expected))
        
        i += 1
    
    return tests


def run_test(name: str, code: str, expected: str) -> TestResult:
    """Run a single test and return result."""
    start = time.time()
    
    stdout_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture):
            run(code)
        
        actual = stdout_capture.getvalue().strip()
        expected = expected.strip()
        
        # Normalize whitespace for comparison
        actual_norm = ' '.join(actual.split())
        expected_norm = ' '.join(expected.split())
        
        passed = actual_norm == expected_norm
        
        return TestResult(
            name=name,
            passed=passed,
            expected=expected,
            actual=actual,
            time_ms=(time.time() - start) * 1000
        )
    
    except Exception as e:
        actual = stdout_capture.getvalue().strip()
        
        # Check if we expected an error
        if expected.startswith('ERROR:'):
            expected_error = expected[6:].strip()
            if expected_error in str(e):
                return TestResult(
                    name=name,
                    passed=True,
                    expected=expected,
                    actual=f"ERROR: {e}",
                    time_ms=(time.time() - start) * 1000
                )
        
        return TestResult(
            name=name,
            passed=False,
            expected=expected,
            actual=actual,
            error=str(e),
            time_ms=(time.time() - start) * 1000
        )


def run_suite(path: Path) -> SuiteResult:
    """Run all tests in a file."""
    start = time.time()
    
    content = path.read_text(encoding='utf-8')
    tests = parse_test_file(content)
    
    results = []
    for name, code, expected in tests:
        result = run_test(name, code, expected)
        results.append(result)
    
    return SuiteResult(
        name=path.stem,
        results=results,
        time_ms=(time.time() - start) * 1000
    )


def print_results(suites: List[SuiteResult], verbose: bool = False):
    """Print test results."""
    total_passed = 0
    total_failed = 0
    total_time = 0.0
    
    print()
    print("=" * 60)
    print("  realTinyTalk v1.0 CONFORMANCE TEST RESULTS")
    print("=" * 60)
    print()
    
    for suite in suites:
        status = "[PASS]" if suite.failed == 0 else "[FAIL]"
        
        print(f"{status} {suite.name}: {suite.passed}/{suite.total} passed ({suite.time_ms:.1f}ms)")
        
        if verbose or suite.failed > 0:
            for result in suite.results:
                if not result.passed or verbose:
                    status = "[PASS]" if result.passed else "[FAIL]"
                    print(f"    {status} {result.name}")
                    
                    if not result.passed:
                        print(f"        Expected: {result.expected[:50]}...")
                        print(f"        Actual:   {result.actual[:50]}...")
                        if result.error:
                            print(f"        Error:    {result.error[:50]}...")
        
        total_passed += suite.passed
        total_failed += suite.failed
        total_time += suite.time_ms
    
    print()
    print("-" * 60)
    
    if total_failed == 0:
        print(f"[OK] ALL {total_passed} TESTS PASSED ({total_time:.1f}ms)")
    else:
        print(f"[!!] {total_failed} FAILED, {total_passed} passed ({total_time:.1f}ms)")
    
    print("=" * 60)
    print()
    
    return total_failed == 0


def main():
    """Run all conformance tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='realTinyTalk Conformance Test Runner')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show all test results')
    parser.add_argument('files', nargs='*', help='Specific test files to run')
    args = parser.parse_args()
    
    tests_dir = Path(__file__).parent
    
    if args.files:
        test_files = [tests_dir / f for f in args.files]
    else:
        test_files = sorted(tests_dir.glob('*.tt'))
    
    if not test_files:
        print("No test files found!")
        return 1
    
    suites = []
    for path in test_files:
        if path.exists():
            suite = run_suite(path)
            suites.append(suite)
        else:
            print(f"Warning: {path} not found")
    
    success = print_results(suites, args.verbose)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
