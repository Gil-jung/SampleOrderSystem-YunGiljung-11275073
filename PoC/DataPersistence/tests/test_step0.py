import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_skeleton_files_exist():
    assert (PROJECT_ROOT / "main.py").is_file()
    assert (PROJECT_ROOT / "storage.py").is_file()
    assert (PROJECT_ROOT / "crud.py").is_file()


def test_storage_module_is_importable_and_defines_data_file():
    import storage

    assert storage.DATA_FILE == "data.json"


def test_crud_module_is_importable():
    import crud  # noqa: F401 (Step 0 시점에는 placeholder만 존재)


def test_main_runs_without_error():
    # Step 6부터 main.py가 메뉴 입력을 요구하므로, 즉시 종료("6")를 표준입력으로 제공한다.
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py")],
        input="6\n",
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    assert result.returncode == 0
    assert result.stderr == ""
