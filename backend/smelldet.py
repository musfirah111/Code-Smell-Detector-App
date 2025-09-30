#!/usr/bin/env python3
"""
Entry point script for the Code Smell Detector CLI.
This provides a convenient way to run the detector.
"""

import sys
from pathlib import Path

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from cli import main

if __name__ == '__main__':
    main()
