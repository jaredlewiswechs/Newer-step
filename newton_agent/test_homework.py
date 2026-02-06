#!/usr/bin/env python3
"""
Test homework-style questions against Newton's knowledge base.
"""
import requests

BASE_URL = "http://localhost:8091"

HOMEWORK_QUESTIONS = [
    # Biology
    ("What is the mitochondria?", "powerhouse"),
    ("What does DNA stand for?", "deoxyribonucleic"),
    ("What is photosynthesis?", "glucose"),
    
    # Chemistry
    ("What is the atomic number of carbon?", "6"),
    ("What element has symbol Au?", "gold"),
    ("What does H2O mean?", "hydrogen"),
    
    # Physics
    ("What is Newton's first law?", "rest"),
    ("What is Ohm's law?", "V = IR"),
    ("What is the unit of force?", "newton"),
    
    # Math
    ("What is the quadratic formula?", "±"),
    ("What does sigma mean in math?", "sum"),
    
    # Previous working questions
    ("What is the capital of France?", "Paris"),
    ("What is the speed of light?", "299792458"),
]

def test_question(question: str, expected_substring: str) -> bool:
    """Test a single question."""
    try:
        r = requests.post(f"{BASE_URL}/chat", json={"message": question}, timeout=30)
        data = r.json()
        content = data.get("content", "").lower()
        verified = data.get("verified", False)
        
        found = expected_substring.lower() in content
        
        status = "✓ PASS" if (found and verified) else "○ PARTIAL" if found else "✗ FAIL"
        
        # Truncate content for display
        content_short = content[:80] + "..." if len(content) > 80 else content
        
        print(f"{status}  {question}")
        print(f"       Expected: '{expected_substring}' | Found: {found} | Verified: {verified}")
        if not found:
            print(f"       Response: {content_short}")
        
        return found and verified
    except Exception as e:
        print(f"✗ ERROR  {question}")
        print(f"       {e}")
        return False


def main():
    print("=" * 70)
    print("NEWTON HOMEWORK TEST")
    print("=" * 70)
    print()
    
    passed = 0
    total = len(HOMEWORK_QUESTIONS)
    
    for question, expected in HOMEWORK_QUESTIONS:
        if test_question(question, expected):
            passed += 1
        print()
    
    print("=" * 70)
    print(f"RESULTS: {passed}/{total} ({100*passed/total:.0f}%)")
    print("=" * 70)


if __name__ == "__main__":
    main()
