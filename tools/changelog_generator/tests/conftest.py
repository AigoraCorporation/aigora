import sys
from pathlib import Path

# Add tools/ to sys.path so that `changelog_generator` is importable as a package.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
