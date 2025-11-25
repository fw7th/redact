import sys
from pathlib import Path

# Add parent directory to sys.path so 'redact' package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))
