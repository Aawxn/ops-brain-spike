"""
conftest.py - Pytest path configuration.
"""
import sys
from pathlib import Path

# Add project root to sys.path so tests can import modules directly
spike_root = Path(__file__).resolve().parent.parent
if str(spike_root) not in sys.path:
    sys.path.insert(0, str(spike_root))
