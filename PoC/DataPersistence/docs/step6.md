# Step 6. `main.py` — 메뉴 루프 및 통합 (세부 구현사항)

`PLAN.md`의 Step 6 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 코드를 구현한다.

## 1. 목표

Step 2~5에서 구현한 5개 CRUD 함수(`create_item`, `read_all`, `read_one`, `update_item`, `delete_item`)를
`main.py`의 메뉴 루프에서 호출하도록 통합하여, 실행 가능한 콘솔 애플리케이션을 완성한다.

## 2. 함수 시그니처 및 동작 정의

### 2.1 `print_menu() -> None`

메뉴를 콘솔에 출력하는 함수.

```python
def print_menu():
    print("\n=== JSON CRUD ===")
    print("1. Create  2. Read All  3. Read One  4. Update  5. Delete  6. Exit")
```

### 2.2 `main() -> None`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 (내부에서 `input()`으로 메뉴 번호 입력) |
| 출력 | 없음 (메뉴/결과 콘솔 출력) |
| 의존 | `crud.create_item`, `crud.read_all`, `crud.read_one`, `crud.update_item`, `crud.delete_item` |

동작 순서:

1. `while True` 루프 시작
2. `print_menu()` 호출로 메뉴 출력
3. `input("선택: ")`으로 메뉴 번호 입력받기 (`strip()` 적용)
4. 입력값에 따라 분기:
   - `"1"` → `create_item()`
   - `"2"` → `read_all()`
   - `"3"` → `read_one()`
   - `"4"` → `update_item()`
   - `"5"` → `delete_item()`
   - `"6"` → 종료 메시지 출력 후 `break`
   - 그 외 → `"잘못된 입력입니다."` 출력
5. `"6"`이 아니면 루프를 반복하여 다시 메뉴 출력

```python
from crud import create_item, read_all, read_one, update_item, delete_item


def print_menu():
    print("\n=== JSON CRUD ===")
    print("1. Create  2. Read All  3. Read One  4. Update  5. Delete  6. Exit")


def main():
    while True:
        print_menu()
        choice = input("선택: ").strip()

        if choice == "1":
            create_item()
        elif choice == "2":
            read_all()
        elif choice == "3":
            read_one()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            print("종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()
```

## 3. 고려한 예외/경계 케이스

- **잘못된 메뉴 입력**: 정의되지 않은 숫자(`"7"`)나 문자열(`"abc"`)을 입력해도 예외 없이 "잘못된 입력입니다." 출력 후 루프가 계속되어야 한다.
- **정상 종료**: `"6"` 입력 시 종료 메시지를 출력하고 루프를 즉시 빠져나와야 한다 (이후 다른 분기로 흐르지 않음).
- **여러 메뉴 연속 선택**: 한 번의 실행 세션에서 여러 메뉴를 순서대로 선택해도 각 CRUD 함수가 독립적으로 정상 동작해야 한다 (내부 상태를 공유하지 않고 매번 `storage.load_data()`로 최신 데이터를 다시 읽으므로 문제 없음).
- **입력값 공백 처리**: 메뉴 번호 입력도 다른 함수들과 일관되게 `strip()`으로 앞뒤 공백을 제거한다 (`" 1 "` → `"1"`로 정상 인식).
- **테스트 시 무한 루프 방지**: `main()`은 `while True`이므로, 테스트에서는 `input()`을 순서대로 값을 반환하는 이터레이터로 모킹하고 마지막에 반드시 `"6"`(종료)을 포함시켜 루프가 종료되도록 한다. 각 CRUD 함수는 이미 Step 2~5에서 개별 테스트로 검증되었으므로, 이번 Step 테스트는 **분기 로직(메뉴 번호 → 올바른 함수 호출)** 자체를 검증하는 데 집중하고, CRUD 함수들은 `monkeypatch`로 스텁(stub) 처리하여 실제 파일 I/O 없이 호출 여부만 확인한다.

## 4. 테스트 계획 (`tests/test_step6.py`, pytest)

`main.py`가 import하는 `create_item`, `read_all`, `read_one`, `update_item`, `delete_item` 5개 함수를 각각
`monkeypatch`로 호출 여부만 기록하는 스텁으로 교체한다. `input()`도 `monkeypatch`로 미리 정해진 시퀀스를 반환하도록 대체한다.

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_menu_1_calls_create_item` | `"1"` → `"6"` 입력 시 `create_item`이 정확히 1회 호출되고 종료되는지 확인 |
| `test_menu_2_calls_read_all` | `"2"` → `"6"` 입력 시 `read_all`이 호출되는지 확인 |
| `test_menu_3_calls_read_one` | `"3"` → `"6"` 입력 시 `read_one`이 호출되는지 확인 |
| `test_menu_4_calls_update_item` | `"4"` → `"6"` 입력 시 `update_item`이 호출되는지 확인 |
| `test_menu_5_calls_delete_item` | `"5"` → `"6"` 입력 시 `delete_item`이 호출되는지 확인 |
| `test_menu_6_exits_loop` | `"6"` 입력 시 즉시 루프 종료 및 "종료합니다." 출력 확인 (다른 CRUD 함수 미호출) |
| `test_menu_invalid_choice_shows_message_and_continues` | `"9"` → `"6"` 입력 시 "잘못된 입력입니다." 출력 후 정상 종료(무한 루프 없음)되는지 확인 |
| `test_menu_processes_multiple_choices_in_sequence` | `"1"` → `"2"` → `"6"` 순서 입력 시 `create_item`, `read_all`이 각각 1회씩 순서대로 호출되는지 확인 |

```python
def test_menu_1_calls_create_item(monkeypatch):
    calls = []
    monkeypatch.setattr(main, "create_item", lambda: calls.append("create"))
    inputs = iter(["1", "6"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    assert calls == ["create"]
```

## 5. 검증 방법 (수동)

```bash
.venv/Scripts/python.exe -m pytest tests/test_step6.py -v
```

- 위 8개 테스트 모두 통과해야 Step 6 완료로 간주한다.
- 전체 회귀 확인을 위해 `tests/` 전체(`test_step0.py`~`test_step6.py`)도 함께 실행한다.
- 추가로 `python main.py`를 직접 실행하여 실제 콘솔에서 1~6 메뉴가 정상 동작하는지 수동으로 한 번 확인한다 (Step 7의 E2E 시나리오와 일부 중복되므로 간단한 스모크 테스트 수준으로 진행).

## 6. 완료 기준

- [x] `main.py`에 `print_menu()`, `main()` 구현 완료
- [x] `tests/test_step6.py` 작성 및 전체 통과 (기존 테스트 회귀 없음)
- [x] `docs/step6.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬

## 7. 구현 결과

`main.py`는 2절에서 계획한 코드 그대로 구현되었다 (계획과 실제 구현 간 차이 없음).

### 7.1 기존 테스트(`tests/test_step0.py`) 조정 필요성 발견

`main.py`가 Step 0 시점에는 `pass`만 있던 placeholder였으나, 이번 Step에서 실제 `input()` 기반 메뉴 루프로 채워지면서
`tests/test_step0.py::test_main_runs_without_error`가 표준입력 없이 `main.py`를 subprocess로 실행해 `EOFError`로
실패하는 회귀가 발견되었다. 해당 테스트에 `subprocess.run(..., input="6\n", ...)`을 추가해 즉시 종료("6") 입력을
공급하도록 수정했다 (Step 0 완료 기준 자체는 변하지 않음 — "예외 없이 실행"을 여전히 검증).

### 7.2 수동 스모크 테스트

```bash
printf '1\ntestuser\ntest@example.com\n2\n6\n' | .venv/Scripts/python.exe main.py
```

- Create(`1`) → Read All(`2`) → Exit(`6`) 순서로 정상 동작, `data.json`에 입력한 레코드가 올바르게 저장됨을 확인했다.
- 한글 입력을 Git Bash `printf`로 파이핑했을 때 콘솔 코드페이지 불일치로 `UnicodeEncodeError`/깨진 문자가 발생했으나,
  이는 Windows 터미널 환경의 인코딩 문제이며 애플리케이션 로직의 결함이 아님을 확인했다 (pytest의 `monkeypatch`
  기반 `input()` 테스트는 실제 OS 파이프를 거치지 않으므로 이 문제와 무관하다).

### 7.3 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
============================= test session starts =============================
collected 38 items

tests/test_step0.py::test_skeleton_files_exist PASSED                    [  2%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [  5%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [  7%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [ 10%]
tests/test_step1.py (5 tests) PASSED
tests/test_step2.py (5 tests) PASSED
tests/test_step3.py (5 tests) PASSED
tests/test_step4.py (5 tests) PASSED
tests/test_step5.py (6 tests) PASSED
tests/test_step6.py::test_menu_1_calls_create_item PASSED                [ 81%]
tests/test_step6.py::test_menu_2_calls_read_all PASSED                   [ 84%]
tests/test_step6.py::test_menu_3_calls_read_one PASSED                   [ 86%]
tests/test_step6.py::test_menu_4_calls_update_item PASSED                [ 89%]
tests/test_step6.py::test_menu_5_calls_delete_item PASSED                [ 92%]
tests/test_step6.py::test_menu_6_exits_loop PASSED                       [ 94%]
tests/test_step6.py::test_menu_invalid_choice_shows_message_and_continues PASSED [ 97%]
tests/test_step6.py::test_menu_processes_multiple_choices_in_sequence PASSED [100%]

============================== 38 passed in 0.20s ==============================
```

Step 0~5 테스트(수정된 `test_main_runs_without_error` 포함) 30건을 포함해 총 38건 모두 통과했다.
이로써 `PoC.md`/`PLAN.md`에서 정의한 콘솔 CRUD 애플리케이션의 전체 기능이 통합 완료되었다.
