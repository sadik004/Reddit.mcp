"""
Pytest fixtures and configuration for Reddit MCP test suite.
"""

import sys
from pathlib import Path

# Add src to sys.path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
