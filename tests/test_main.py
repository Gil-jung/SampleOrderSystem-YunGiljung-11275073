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


def test_시료_관리_메뉴에서_등록한_시료가_목록_조회에_표시된다():
    user_input = "\n".join(
        [
            "1",  # 메인 메뉴 -> 시료 관리
            "1",  # 시료 등록
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "2",  # 시료 목록 조회
            "0",  # 시료 관리 메뉴에서 뒤로가기
            "0",  # 메인 메뉴 종료
            "",
        ]
    )

    result = subprocess.run(
        [sys.executable, "main.py"],
        input=user_input,
        capture_output=True,
        text=True,
        cwd=SRC_DIR,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "Wafer-A" in result.stdout
    assert "SMP-001" in result.stdout


def test_시료_관리_메뉴에서_검색어로_필터링된_결과만_표시된다():
    user_input = "\n".join(
        [
            "1",  # 메인 메뉴 -> 시료 관리
            "1",  # 등록: Wafer-A
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "1",  # 등록: Other-B
            "SMP-002",
            "Other-B",
            "1.0",
            "0.8",
            "3",  # 검색
            "Wafer",
            "0",  # 시료 관리 메뉴에서 뒤로가기
            "0",  # 메인 메뉴 종료
            "",
        ]
    )

    result = subprocess.run(
        [sys.executable, "main.py"],
        input=user_input,
        capture_output=True,
        text=True,
        cwd=SRC_DIR,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    assert "Wafer-A" in result.stdout
    assert "Other-B" not in result.stdout
