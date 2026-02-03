#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
ADAN PORTABLE - RUN SCRIPT
Self-verifying autonomous agent with kinematic semantics
═══════════════════════════════════════════════════════════════════════════════

Usage:
    python run.py              # Start Adan server + open UI in browser
    python run.py --no-browser # Start server without opening browser
    python run.py --wiki       # Start Adanpedia on port 8085
    python run.py --test       # Run integration tests
    python run.py --acid       # Run ACID test
    
© 2026 Jared Lewis · Ada Computing Company · Houston, Texas
"""

import sys
import os
import webbrowser
import threading

# Add this directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_server(open_browser=True):
    """Run the main Adan server with UI."""
    import uvicorn
    from adan.server import app
    
    print("Starting Adan on http://localhost:8080")
    print("UI available at http://localhost:8080/")
    
    if open_browser:
        # Open browser after a short delay to let server start
        def open_ui():
            import time
            time.sleep(1.5)
            webbrowser.open("http://localhost:8080")
        threading.Thread(target=open_ui, daemon=True).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8080)


def run_wiki():
    """Run Adanpedia server."""
    import uvicorn
    # Import wiki server
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "wiki_server", 
        os.path.join(os.path.dirname(__file__), "adan", "wiki", "server.py")
    )
    wiki = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wiki)
    print("Starting Adanpedia on http://localhost:8085")
    uvicorn.run(wiki.app, host="0.0.0.0", port=8085)


def run_tests():
    """Run integration tests."""
    print("Running Adan integration tests...")
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "adan/test_integration.py", "-v"],
        cwd=os.path.dirname(__file__)
    )
    return result.returncode


def run_acid():
    """Run ACID test."""
    print("Running ACID test...")
    from adan.identity import get_identity
    from adan.knowledge_base import get_knowledge_base
    from adan.ada import get_ada
    from adan.meta_newton import get_meta_newton
    
    passed = 0
    total = 4
    
    # Test 1: Identity
    print("\n1. IDENTITY TEST")
    identity = get_identity()
    if identity.name == "Newton" and identity.creator == "Jared Lewis":
        print("   ✓ Identity verified")
        passed += 1
    else:
        print("   ✗ Identity failed")
    
    # Test 2: Knowledge Base
    print("\n2. KNOWLEDGE BASE TEST")
    kb = get_knowledge_base()
    result = kb.query("What is the capital of France?")
    if result and "paris" in result.fact.lower():
        print(f"   ✓ KB works: {result.fact}")
        passed += 1
    else:
        print("   ✗ KB failed")
    
    # Test 3: Ada Sentinel
    print("\n3. ADA SENTINEL TEST")
    ada = get_ada()
    if ada:
        print("   ✓ Ada is watching")
        passed += 1
    else:
        print("   ✗ Ada not available")
    
    # Test 4: Meta Newton
    print("\n4. META NEWTON TEST")
    meta = get_meta_newton()
    if meta:
        print("   ✓ Meta Newton verifying")
        passed += 1
    else:
        print("   ✗ Meta Newton not available")
    
    print(f"\n{'='*50}")
    print(f"ACID TEST: {passed}/{total} passed")
    if passed == total:
        print("✓ ALL TESTS PASSED - Adan is operational")
    else:
        print("✗ Some tests failed")
    print(f"{'='*50}")
    
    return 0 if passed == total else 1


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--wiki":
            run_wiki()
        elif arg == "--test":
            sys.exit(run_tests())
        elif arg == "--acid":
            sys.exit(run_acid())
        elif arg == "--no-browser":
            run_server(open_browser=False)
        elif arg == "--help" or arg == "-h":
            print(__doc__)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage")
    else:
        run_server(open_browser=True)


if __name__ == "__main__":
    main()
