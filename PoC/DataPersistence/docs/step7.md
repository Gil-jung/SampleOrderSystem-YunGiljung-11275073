# Step 7. 통합 테스트 (End-to-End 시나리오) (세부 구현사항)

`PLAN.md`의 Step 7 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 테스트/검증을 진행한다.

## 1. 목표

Step 0~6에서 개별적으로 검증한 각 기능(파일 영속화, Create, Read, Update, Delete, 메뉴 통합)을
**하나의 연속된 시나리오**로 이어 붙여, 실제 사용 흐름에서도 전체 애플리케이션이 예상대로 동작하는지 확인한다.
`PLAN.md`에 정의된 8단계 시나리오를 자동화된 pytest 테스트와 수동 콘솔 실행 양쪽으로 검증한다.

## 2. 검증 대상 시나리오 (PLAN.md 원문 기준)

1. `data.json`이 없는 상태에서 실행 → Read All 시 "데이터가 없습니다." 확인
2. Create로 2건 입력 (`id=1`, `id=2` 자동 부여 확인)
3. Read All로 2건 모두 출력되는지 확인
4. Read One으로 `id=1` 단건 검색 확인
5. Update로 `id=1`의 `email`만 변경 (name은 Enter로 스킵) → Read One으로 재확인
6. Delete로 `id=2` 삭제 시도 → `n` 입력 후 유지 확인 → 다시 시도 → `y` 입력 후 삭제 확인
7. Read All로 `id=1`만 남아있는지 최종 확인
8. `data.json` 파일을 직접 열어 위 시나리오 결과가 정확히 반영됐는지 확인 (인코딩, 들여쓰기 포함)

## 3. 구현 방식

### 3.1 자동화 E2E 테스트 (`tests/test_step7_e2e.py`, pytest)

Step 0~6의 단위 테스트는 각 함수를 개별적으로 격리해 검증했지만, 이번 Step은 **`main.main()` 진입점 하나를 통해**
전체 시나리오를 한 번의 실행 흐름으로 검증한다.

- `storage.DATA_FILE`을 `tmp_path`로 격리 (기존 Step들과 동일한 방식)
- 시나리오의 모든 사용자 입력(메뉴 번호 + 각 기능별 프롬프트 응답)을 순서대로 나열한 `input()` 이터레이터로 `monkeypatch`
- 마지막에는 반드시 메뉴 `"6"`(Exit)을 입력해 `main.main()`이 정상 종료되도록 함
- 시나리오 진행 중간중간 `storage.load_data()`를 직접 호출해 파일 상태를 단언(assert)
- 콘솔 출력은 `capsys`로 캡처해 "데이터가 없습니다.", "찾을 수 없습니다", "삭제가 취소되었습니다." 등 핵심 메시지 포함 여부도 함께 검증

```python
def test_full_crud_scenario_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))

    inputs = iter([
        "2",                                 # 1. Read All (데이터 없음 확인)
        "1", "홍길동", "hong@example.com",     # 2. Create id=1
        "1", "김철수", "kim@example.com",       # 2. Create id=2
        "2",                                 # 3. Read All (2건 확인)
        "3", "1",                             # 4. Read One id=1
        "4", "1", "", "new@example.com",       # 5. Update id=1 email만 변경
        "3", "1",                             # 5. Read One으로 재확인
        "5", "2", "n",                         # 6. Delete id=2 시도 → 취소
        "5", "2", "y",                         # 6. Delete id=2 재시도 → 삭제
        "2",                                 # 7. Read All (id=1만 남음)
        "6",                                  # 종료
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    captured = capsys.readouterr()
    assert "데이터가 없습니다." in captured.out
    assert "삭제가 취소되었습니다." in captured.out
    assert "[삭제 완료] id=2" in captured.out

    final_data = storage.load_data()
    assert final_data == [{"id": 1, "name": "홍길동", "email": "new@example.com"}]
```

### 3.2 수동 콘솔 검증 (8단계 원문 그대로)

자동화 테스트는 로직 정확성을 보장하지만, `data.json` 실제 파일의 **인코딩/들여쓰기까지 육안 확인**하는 8번 항목은
수동으로 별도 진행한다.

```bash
.venv/Scripts/python.exe main.py
```

- ASCII 값으로 먼저 흐름 확인 (Step 6에서 발견한 Windows 콘솔/파이프 한글 인코딩 이슈를 피하기 위해, 실제 터미널에서
  직접 타이핑하며 진행 — 파이프(`printf | python`)로 자동 입력하지 않음)
- 각 단계 진행 후 `data.json`을 텍스트 에디터로 열어 `ensure_ascii=False`(한글 그대로 표시), `indent=2`(들여쓰기)가
  적용되었는지 확인

## 4. 완료 기준

- [x] `tests/test_step7_e2e.py` 작성 및 통과
- [x] 전체 회귀 확인: `tests/` 전체(`test_step0.py`~`test_step7_e2e.py`) 통과
- [x] 수동 콘솔 시나리오 8단계 전체 수행 및 `data.json` 육안 확인 (한글 인코딩, 들여쓰기 포함)
- [x] `docs/step7.md`에 실제 실행 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬 (PoC.md/PLAN.md에 정의된 전체 CRUD 콘솔 애플리케이션 구현 완료 시점)

## 5. 구현 결과

### 5.1 자동화 E2E 테스트

`tests/test_step7_e2e.py`를 2절 계획대로 작성했다. `main.main()` 하나의 실행으로 전체 8단계 시나리오를
이어서 수행하고, 각 단계의 핵심 콘솔 메시지(`[생성 완료]`, `[수정 완료]`, `삭제가 취소되었습니다.`,
`[삭제 완료]`, `종료합니다.` 등)와 최종 저장 데이터(`{"id": 1, "name": "홍길동", "email": "new@example.com"}`만 남음)를
모두 단언했다.

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
============================= test session starts =============================
collected 39 items

tests/test_step0.py (4 tests) PASSED
tests/test_step1.py (5 tests) PASSED
tests/test_step2.py (5 tests) PASSED
tests/test_step3.py (5 tests) PASSED
tests/test_step4.py (5 tests) PASSED
tests/test_step5.py (6 tests) PASSED
tests/test_step6.py (8 tests) PASSED
tests/test_step7_e2e.py::test_full_crud_scenario_end_to_end PASSED       [100%]

============================== 39 passed in 0.22s ==============================
```

Step 0~6 테스트 38건을 포함해 총 39건 모두 통과했다.

### 5.2 수동 콘솔 검증

3.2절 계획 당시에는 파이프 자동 입력을 피하고 직접 타이핑하기로 했으나, Step 6에서 발견한 인코딩 문제의 원인이
Windows 콘솔 코드페이지임을 확인했으므로, `PYTHONUTF8=1` 환경변수를 설정해 파이프 입력으로도 동일하게 검증했다
(직접 타이핑과 동등한 결과를 더 재현 가능한 방식으로 확보 — 계획 대비 방법 변경).

```bash
export PYTHONUTF8=1
printf '2\n1\n홍길동\nhong@example.com\n1\n김철수\nkim@example.com\n2\n3\n1\n4\n1\n\nnew@example.com\n3\n1\n5\n2\nn\n5\n2\ny\n2\n6\n' \
  | .venv/Scripts/python.exe main.py
```

8단계 시나리오 전체가 예상대로 동작했다:

1. 데이터 없음 → "데이터가 없습니다." 출력 확인
2. Create 2건 → `id=1`(홍길동), `id=2`(김철수) 자동 채번 확인
3. Read All → 2건 모두 출력 확인
4. Read One(`id=1`) → 홍길동 레코드 출력 확인
5. Update(`id=1`, name은 Enter로 스킵, email만 변경) → Read One 재조회 시 `email`만 `new@example.com`으로 변경되고 `name`은 유지됨을 확인
6. Delete(`id=2`) → `n` 입력 시 "삭제가 취소되었습니다." 및 데이터 유지 확인 → 재시도 `y` 입력 시 "[삭제 완료] id=2" 확인
7. Read All → `id=1`(홍길동, new@example.com)만 남음을 확인
8. `data.json` 파일을 직접 읽어 육안 확인:

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "email": "new@example.com"
  }
]
```

한글이 `\uXXXX` 이스케이프 없이 그대로 저장되고(`ensure_ascii=False`), 2칸 들여쓰기(`indent=2`)가 적용되어 있음을
확인했다. 검증에 사용한 `data.json`은 `.gitignore`에 포함되어 있으며, 검증 후 삭제하여 저장소에는 남기지 않았다.

## 6. 결론

Step 0~7이 모두 완료되어, `PoC.md`/`PLAN.md`에서 정의한 JSON 파일 기반 CRUD 콘솔 애플리케이션의 구현과 검증이
완료되었다. 총 39건의 pytest 테스트와 수동 E2E 시나리오 8단계가 모두 통과했다.
