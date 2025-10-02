import sys
from pathlib import Path

MBTI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = MBTI_ROOT.parent

for path in (REPO_ROOT, MBTI_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
