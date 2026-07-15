import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"


def test_main_실행_시_0_입력하면_정상_종료된다():
    result = subprocess.run(
        [sys.executable, "main.py"],
        input="0\n",
        capture_output=True,
        text=True,
        cwd=SRC_DIR,
    )

    assert result.returncode == 0
    assert result.stderr == ""
