#!/usr/bin/env python3
"""
OpenClaw LLM Preset Switcher v2.0
CLI Entrypoint - Backward compatible wrapper
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import main

if __name__ == '__main__':
    main()
