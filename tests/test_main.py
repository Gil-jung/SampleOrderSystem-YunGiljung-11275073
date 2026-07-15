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


def test_모니터링_메뉴에서_주문량_조회_시_상태별_건수가_출력된다():
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
            "0",
            "3",  # 모니터링
            "1",  # 주문량 조회
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
    assert "RESERVED: 1" in result.stdout


def test_모니터링_메뉴에서_재고량_조회_시_시료별_상태가_출력된다():
    user_input = "\n".join(
        [
            "1",  # 시료 관리
            "1",  # 등록
            "SMP-001",
            "Wafer-A",
            "2.5",
            "0.9",
            "0",
            "3",  # 모니터링
            "2",  # 재고량 조회
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
    assert "SMP-001" in result.stdout
    assert "여유" in result.stdout


def test_생산_라인_메뉴에서_생산_완료_처리하면_CONFIRMED로_전환된다():
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
            "1",  # 예약 (재고 0 -> 승인 시 PRODUCING)
            "SMP-001",
            "홍길동",
            "9",
            "3",  # 승인
            "ORD-0001",
            "0",
            "5",  # 생산 라인
            "3",  # 생산 완료 처리
            "0",
            "3",  # 모니터링
            "1",  # 주문량 조회
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
    assert "CONFIRMED: 1" in result.stdout
    assert "PRODUCING: 0" in result.stdout


def test_출고_메뉴에서_CONFIRMED_목록을_조회하면_고객명이_출력된다():
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
            "1",  # 예약 (재고 0 -> 승인 시 PRODUCING)
            "SMP-001",
            "홍길동",
            "9",
            "3",  # 승인
            "ORD-0001",
            "0",
            "5",  # 생산 라인
            "3",  # 생산 완료 처리 -> CONFIRMED
            "0",
            "4",  # 출고 처리
            "1",  # CONFIRMED 목록 조회
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


def test_출고_메뉴에서_출고_실행하면_RELEASE로_전환된다():
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
            "1",  # 예약 (재고 0 -> 승인 시 PRODUCING)
            "SMP-001",
            "홍길동",
            "9",
            "3",  # 승인
            "ORD-0001",
            "0",
            "5",  # 생산 라인
            "3",  # 생산 완료 처리 -> CONFIRMED
            "0",
            "4",  # 출고 처리
            "2",  # 출고 실행
            "ORD-0001",
            "0",
            "3",  # 모니터링
            "1",  # 주문량 조회
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
    assert "RELEASE: 1" in result.stdout
    assert "CONFIRMED: 0" in result.stdout


def test_생산_라인_메뉴에서_생산_현황을_조회하면_실_생산량이_출력된다():
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
            "1",  # 예약 (재고 0 -> 승인 시 PRODUCING)
            "SMP-001",
            "홍길동",
            "9",
            "3",  # 승인
            "ORD-0001",
            "0",
            "5",  # 생산 라인
            "1",  # 생산 현황 조회
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
    assert "ORD-0001" in result.stdout
    assert "10" in result.stdout  # ceil(9/0.9) = 10 (실 생산량)


def test_생산_라인_메뉴에서_대기_큐를_조회하면_주문ID_목록이_출력된다():
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
            "1",  # 예약 1 (재고 0 -> 승인 시 PRODUCING)
            "SMP-001",
            "홍길동",
            "9",
            "1",  # 예약 2
            "SMP-001",
            "김철수",
            "3",
            "3",  # 승인
            "ORD-0001",
            "3",  # 승인
            "ORD-0002",
            "0",
            "5",  # 생산 라인
            "2",  # 대기 큐 조회
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
    # 두 주문 ID 모두 "예약 완료" 메시지에서 한 번씩 출력되므로, 큐 목록 출력이 실제로
    # 동작해야만 각 ID가 2번씩(예약 완료 + 큐 목록) 등장한다. 등장 횟수까지 확인해야
    # 큐 조회 분기가 실행되었음을 진짜로 검증할 수 있다 (그렇지 않으면 예약 순서가
    # 우연히 같아 순서 비교만으로는 위양성이 발생한다).
    assert result.stdout.count("ORD-0001") == 2
    assert result.stdout.count("ORD-0002") == 2
    ord1_last_index = result.stdout.rindex("ORD-0001")
    ord2_last_index = result.stdout.rindex("ORD-0002")
    assert ord1_last_index < ord2_last_index
