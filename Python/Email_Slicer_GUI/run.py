#!/usr/bin/env python3
"""Alternative entry point that handles imports better."""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main import main
    main()
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install dependencies using: pip install -r requirements.txt")
    sys.exit(1)