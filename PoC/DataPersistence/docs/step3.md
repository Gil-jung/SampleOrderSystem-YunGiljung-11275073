# Step 3. `crud.py` — Read 기능 구현 (전체 조회 / 단일 검색) (세부 구현사항)

`PLAN.md`의 Step 3 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 코드를 구현한다.

## 1. 목표

저장된 전체 데이터를 조회하는 `read_all()`과, `id`로 특정 레코드를 검색하는 `read_one()`을 `crud.py`에 구현한다.

## 2. 함수 시그니처 및 동작 정의

### 2.1 `read_all() -> None`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 |
| 출력 | 없음 (콘솔 출력) |
| 의존 | `storage.load_data()` |

동작 순서:

1. `storage.load_data()`로 전체 데이터 로드
2. 데이터가 비어있으면 `"데이터가 없습니다."` 출력 후 종료
3. 비어있지 않으면 각 레코드를 한 줄씩 출력

```python
def read_all():
    data = load_data()
    if not data:
        print("데이터가 없습니다.")
        return
    for item in data:
        print(item)
```

### 2.2 `read_one() -> None`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 (내부에서 `input()`으로 `id` 입력) |
| 출력 | 없음 (콘솔 출력) |
| 의존 | `storage.load_data()` |

동작 순서:

1. `storage.load_data()`로 전체 데이터 로드
2. `input()`으로 검색할 `id` 입력받기
3. 각 레코드를 순회하며 `str(item["id"]) == target_id`로 비교 (사용자 입력은 문자열이므로 `id`를 문자열로 변환해 비교)
4. 일치하는 레코드를 찾으면 출력 후 즉시 반환
5. 끝까지 찾지 못하면 `"id={target_id} 데이터를 찾을 수 없습니다."` 출력

```python
def read_one():
    data = load_data()
    target_id = input("조회할 id: ").strip()

    for item in data:
        if str(item["id"]) == target_id:
            print(item)
            return

    print(f"id={target_id} 데이터를 찾을 수 없습니다.")
```

## 3. 고려한 예외/경계 케이스

- **빈 데이터 상태**: `read_all()` 호출 시 데이터가 없으면 빈 목록 대신 안내 메시지를 출력해야 한다.
- **문자열/숫자 비교**: `id`는 내부적으로 정수(`int`)로 저장되지만, `input()`은 항상 문자열을 반환하므로 `str(item["id"])`로 변환 후 비교한다. 숫자가 아닌 값(`"abc"`)을 입력해도 예외 없이 "찾을 수 없음"으로 처리되어야 한다.
- **존재하지 않는 id 검색**: 빈 데이터 또는 없는 id로 검색 시 예외 없이 안내 메시지만 출력해야 한다.
- **입력값 공백 처리**: `read_one()`의 `id` 입력도 `strip()`으로 앞뒤 공백을 제거한다 (`create_item()`과의 일관성 유지).
- **출력 검증 방법**: `print()` 출력은 `capsys`(pytest 내장 fixture)로 캡처하여 검증한다.

## 4. 테스트 계획 (`tests/test_step3.py`, pytest)

`storage.DATA_FILE`을 `tmp_path`로 격리하고, `read_one()`의 `input()`은 `monkeypatch`로 대체한다. 콘솔 출력은 `capsys`로 캡처한다.

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_read_all_prints_message_when_empty` | 데이터가 없을 때 `read_all()` 호출 시 "데이터가 없습니다." 출력 확인 |
| `test_read_all_prints_all_items` | 2건 저장 후 `read_all()` 호출 시 두 레코드가 모두 출력에 포함되는지 확인 |
| `test_read_one_finds_existing_id` | 존재하는 `id`로 `read_one()` 호출 시 해당 레코드가 출력되는지 확인 |
| `test_read_one_reports_when_id_not_found` | 존재하지 않는 `id`로 `read_one()` 호출 시 "찾을 수 없습니다" 메시지 출력 확인 |
| `test_read_one_handles_non_numeric_input_gracefully` | 숫자가 아닌 입력(`"abc"`)에도 예외 없이 "찾을 수 없습니다" 메시지가 출력되는지 확인 |

```python
def test_read_one_finds_existing_id(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    monkeypatch.setattr("builtins.input", lambda _: "1")

    crud.read_one()

    captured = capsys.readouterr()
    assert "홍길동" in captured.out
```

## 5. 검증 방법 (수동)

```bash
.venv/Scripts/python.exe -m pytest tests/test_step3.py -v
```

- 위 5개 테스트 모두 통과해야 Step 3 완료로 간주한다.
- 전체 회귀 확인을 위해 `tests/` 전체(`test_step0.py`~`test_step3.py`)도 함께 실행한다.

## 6. 완료 기준

- [x] `crud.py`에 `read_all()`, `read_one()` 구현 완료
- [x] `tests/test_step3.py` 작성 및 전체 통과 (기존 테스트 회귀 없음)
- [x] `docs/step3.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬

## 7. 구현 결과

`crud.py`는 2절에서 계획한 코드 그대로 구현되었다 (계획과 실제 구현 간 차이 없음). `read_all`/`read_one`은
기존 `create_item` 아래에 이어서 추가했다.

### 7.1 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
tests/test_step0.py::test_skeleton_files_exist PASSED                    [  5%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [ 10%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [ 15%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [ 21%]
tests/test_step1.py::test_load_data_returns_empty_list_when_file_missing PASSED [ 26%]
tests/test_step1.py::test_save_then_load_round_trip PASSED               [ 31%]
tests/test_step1.py::test_save_data_preserves_korean_without_unicode_escape PASSED [ 36%]
tests/test_step1.py::test_save_data_writes_indented_json PASSED          [ 42%]
tests/test_step1.py::test_save_empty_list PASSED                         [ 47%]
tests/test_step2.py::test_create_item_assigns_id_1_when_empty PASSED     [ 52%]
tests/test_step2.py::test_create_item_increments_id_sequentially PASSED  [ 57%]
tests/test_step2.py::test_create_item_does_not_reuse_deleted_id PASSED   [ 63%]
tests/test_step2.py::test_create_item_saves_stripped_input PASSED        [ 68%]
tests/test_step2.py::test_create_item_persists_to_storage PASSED         [ 73%]
tests/test_step3.py::test_read_all_prints_message_when_empty PASSED      [ 78%]
tests/test_step3.py::test_read_all_prints_all_items PASSED               [ 84%]
tests/test_step3.py::test_read_one_finds_existing_id PASSED              [ 89%]
tests/test_step3.py::test_read_one_reports_when_id_not_found PASSED      [ 94%]
tests/test_step3.py::test_read_one_handles_non_numeric_input_gracefully PASSED [100%]

============================= 19 passed in 0.13s ==============================
```

Step 0~2 테스트 14건을 포함해 총 19건 모두 통과했다 (기존 테스트 회귀 없음).
