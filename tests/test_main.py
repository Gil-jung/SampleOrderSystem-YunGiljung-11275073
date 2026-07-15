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


def test_주문_메뉴에서_예약하면_주문ID가_출력된다():
    user_input = "\n".join(
        [
            "1",  # 메인 메뉴 -> 시료 관리
            "1",  # 등록
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "0",  # 시료 관리 메뉴 뒤로가기
            "2",  # 메인 메뉴 -> 주문
            "1",  # 예약
            "SMP-001",
            "홍길동",
            "5",
            "0",  # 주문 메뉴 뒤로가기
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
    assert "ORD-" in result.stdout


def test_주문_메뉴에서_접수된_목록을_조회하면_고객명이_출력된다():
    user_input = "\n".join(
        [
            "1",  # 시료 관리
            "1",  # 등록
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "0",
            "2",  # 주문
            "1",  # 예약
            "SMP-001",
            "홍길동",
            "5",
            "2",  # 접수된 목록 조회
            "0",
            "0",
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
    assert "홍길동" in result.stdout


def test_주문_메뉴에서_승인하면_접수된_목록에서_사라진다():
    user_input = "\n".join(
        [
            "1",  # 시료 관리
            "1",  # 등록
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "0",
            "2",  # 주문
            "1",  # 예약
            "SMP-001",
            "홍길동",
            "5",
            "3",  # 승인
            "ORD-0001",
            "2",  # 접수된 목록 조회
            "0",
            "0",
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
    assert "주문이 없습니다." in result.stdout


def test_주문_메뉴에서_거절하면_접수된_목록에서_사라진다():
    user_input = "\n".join(
        [
            "1",  # 시료 관리
            "1",  # 등록
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "0",
            "2",  # 주문
            "1",  # 예약
            "SMP-001",
            "홍길동",
            "5",
            "4",  # 거절
            "ORD-0001",
            "2",  # 접수된 목록 조회
            "0",
            "0",
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
    assert "주문이 없습니다." in result.stdout
