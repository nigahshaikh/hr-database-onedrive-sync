"""
Quick test runner - Execute with: python run_tests.py
This script makes it easy to run different test configurations
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def run_command(cmd, description):
    """Run a command and handle output"""
    print(f"▶ {description}")
    print(f"  Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def check_api_running():
    """Check if API is running"""
    print("Checking API status...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result == 0:
        print("✓ API is running on http://localhost:8000\n")
        return True
    else:
        print("✗ API is not running")
        print("  Start it with: python -m uvicorn api:app --reload\n")
        return False

def main():
    """Main menu"""
    print_header("FA Glass HR API - Test Runner")
    
    options = [
        ("1", "Run all pytest tests (verbose)", ["pytest", "test_api.py", "-v", "-s"]),
        ("2", "Run pytest with coverage", ["pytest", "test_api.py", "-v", "--cov=api", "--cov-report=term-missing"]),
        ("3", "Run specific test class", None),
        ("4", "Run interactive manual tests", ["python", "test_api_manual.py"]),
        ("5", "Quick smoke test", ["pytest", "test_api.py::TestMetadataAndHealth", "-v", "-s"]),
        ("6", "Run data presence tests", ["pytest", "test_api.py::TestDataPresence", "-v", "-s"]),
        ("7", "Install test requirements", ["pip", "install", "-r", "test_requirements.txt"]),
        ("0", "Exit", None),
    ]
    
    while True:
        print("\nSelect test option:")
        for option, description, _ in options:
            print(f"  {option}. {description}")
        
        choice = input("\nEnter choice (0-7): ").strip()
        
        if choice == "0":
            print("Exiting...")
            sys.exit(0)
        
        if choice == "3":
            # Specific test class
            test_class = input("Enter test class name (e.g., TestSearchEmployees): ").strip()
            if test_class:
                cmd = ["pytest", f"test_api.py::{test_class}", "-v", "-s"]
                run_command(cmd, f"Running {test_class}")
        elif choice in [str(i) for i in range(1, 8)]:
            for opt, desc, cmd in options:
                if opt == choice and cmd:
                    # Check if manual test requires API
                    if "manual" in desc.lower():
                        if not check_api_running():
                            print("Start the API first!")
                            break
                    
                    run_command(cmd, desc)
                    break
        
        again = input("\nRun another test? (y/n): ").strip().lower()
        if again != 'y':
            print("Exiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
