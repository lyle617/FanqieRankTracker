import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_build_latest_direct_entrypoint_can_import_repo_config():
    result = subprocess.run(
        [sys.executable, "scripts/build_latest.py", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "--dataset" in result.stdout
