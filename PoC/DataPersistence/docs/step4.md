# Step 4. `crud.py` — Update 기능 구현 (세부 구현사항)

`PLAN.md`의 Step 4 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 코드를 구현한다.

## 1. 목표

`id`로 대상 레코드를 찾아 `name`/`email` 필드를 선택적으로 수정하는 `update_item()`을 `crud.py`에 구현한다.
빈 입력은 "변경하지 않음"으로 처리해 일부 필드만 수정할 수 있도록 한다.

## 2. 함수 시그니처 및 동작 정의

### `update_item() -> None`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 (내부에서 `input()`으로 `id` 및 필드 값 입력) |
| 출력 | 없음 (완료/실패 메시지 콘솔 출력) |
| 의존 | `storage.load_data()`, `storage.save_data()` |

동작 순서:

1. `storage.load_data()`로 전체 데이터 로드
2. `input()`으로 수정할 `id` 입력받기 (`strip()` 적용, `read_one()`과 동일하게 문자열 비교)
3. `id`가 일치하는 레코드를 찾지 못하면 `"id={target_id} 데이터를 찾을 수 없습니다."` 출력 후 종료
4. 일치하는 레코드를 찾으면:
   - 현재 값을 프롬프트에 보여주며 새 값 입력받기 (`"이름 ({현재값}, 그대로면 Enter): "`)
   - 입력이 빈 문자열(`""`)이면 기존 값 유지, 값이 있으면 해당 필드 갱신
   - `name`, `email` 순서로 반복
5. `storage.save_data(data)`로 즉시 반영
6. `[수정 완료] id={target_id}` 출력

```python
def update_item():
    data = load_data()
    target_id = input("수정할 id: ").strip()

    for item in data:
        if str(item["id"]) == target_id:
            new_name = input(f"이름 ({item['name']}, 그대로면 Enter): ").strip()
            new_email = input(f"이메일 ({item['email']}, 그대로면 Enter): ").strip()

            if new_name:
                item["name"] = new_name
            if new_email:
                item["email"] = new_email

            save_data(data)
            print(f"[수정 완료] id={target_id}")
            return

    print(f"id={target_id} 데이터를 찾을 수 없습니다.")
```

## 3. 고려한 예외/경계 케이스

- **존재하지 않는 id**: 데이터가 없거나 대상 `id`가 없으면 저장 없이 안내 메시지만 출력한다.
- **일부 필드만 수정**: `name`은 새 값을 입력하고 `email`은 빈 입력(Enter)만 하면, `email`은 기존 값이 그대로 유지되어야 한다.
- **전체 필드 미변경**: 두 필드 모두 빈 입력이면 레코드 내용은 변경되지 않지만, `save_data()`는 여전히 호출되어 `[수정 완료]` 메시지가 출력된다 (PLAN.md 명세상 별도의 "변경 없음" 분기는 두지 않음).
- **공백만 입력한 경우**: `"   "`처럼 공백만 입력해도 `strip()` 후 빈 문자열이 되므로 "변경하지 않음"으로 처리된다.
- **다른 레코드에 영향 없음**: 여러 레코드가 있을 때 대상 `id`가 아닌 레코드는 값이 변하지 않아야 한다.
- **id 자체는 수정 대상이 아님**: 이번 Step에서는 `name`/`email`만 수정 가능하고 `id`는 변경하지 않는다.

## 4. 테스트 계획 (`tests/test_step4.py`, pytest)

`storage.DATA_FILE`을 `tmp_path`로 격리하고, `input()`은 `monkeypatch`로 순서대로 값을 반환하도록 대체한다.
콘솔 출력 검증은 `capsys`를 사용한다.

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_update_item_reports_when_id_not_found` | 존재하지 않는 `id` 입력 시 "찾을 수 없습니다" 메시지 출력, 데이터 변경 없음 확인 |
| `test_update_item_updates_both_fields` | `name`, `email` 모두 새 값 입력 시 두 필드 모두 갱신되는지 확인 |
| `test_update_item_keeps_existing_value_when_input_blank` | `name`만 새 값 입력하고 `email`은 빈 입력(Enter) 시 `email`이 기존 값으로 유지되는지 확인 |
| `test_update_item_persists_to_storage` | `update_item()` 호출 후 `storage.load_data()`로 재조회 시 변경 사항이 실제로 반영되어 있는지 확인 |
| `test_update_item_does_not_affect_other_records` | 레코드 2건 중 1건만 수정 시 나머지 레코드는 그대로인지 확인 |

```python
def test_update_item_keeps_existing_value_when_input_blank(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "박영희", ""])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.update_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": "박영희", "email": "hong@example.com"}]
```

## 5. 검증 방법 (수동)

```bash
.venv/Scripts/python.exe -m pytest tests/test_step4.py -v
```

- 위 5개 테스트 모두 통과해야 Step 4 완료로 간주한다.
- 전체 회귀 확인을 위해 `tests/` 전체(`test_step0.py`~`test_step4.py`)도 함께 실행한다.

## 6. 완료 기준

- [x] `crud.py`에 `update_item()` 구현 완료
- [x] `tests/test_step4.py` 작성 및 전체 통과 (기존 테스트 회귀 없음)
- [x] `docs/step4.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬

## 7. 구현 결과

`crud.py`는 2절에서 계획한 코드 그대로 구현되었다 (계획과 실제 구현 간 차이 없음). `update_item`은
기존 `read_one` 아래에 이어서 추가했다.

### 7.1 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
tests/test_step0.py::test_skeleton_files_exist PASSED                    [  4%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [  8%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [ 12%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [ 16%]
tests/test_step1.py::test_load_data_returns_empty_list_when_file_missing PASSED [ 20%]
tests/test_step1.py::test_save_then_load_round_trip PASSED               [ 25%]
tests/test_step1.py::test_save_data_preserves_korean_without_unicode_escape PASSED [ 29%]
tests/test_step1.py::test_save_data_writes_indented_json PASSED          [ 33%]
tests/test_step1.py::test_save_empty_list PASSED                         [ 37%]
tests/test_step2.py::test_create_item_assigns_id_1_when_empty PASSED     [ 41%]
tests/test_step2.py::test_create_item_increments_id_sequentially PASSED  [ 45%]
tests/test_step2.py::test_create_item_does_not_reuse_deleted_id PASSED   [ 50%]
tests/test_step2.py::test_create_item_saves_stripped_input PASSED        [ 54%]
tests/test_step2.py::test_create_item_persists_to_storage PASSED         [ 58%]
tests/test_step3.py::test_read_all_prints_message_when_empty PASSED      [ 62%]
tests/test_step3.py::test_read_all_prints_all_items PASSED               [ 66%]
tests/test_step3.py::test_read_one_finds_existing_id PASSED              [ 70%]
tests/test_step3.py::test_read_one_reports_when_id_not_found PASSED      [ 75%]
tests/test_step3.py::test_read_one_handles_non_numeric_input_gracefully PASSED [ 79%]
tests/test_step4.py::test_update_item_reports_when_id_not_found PASSED   [ 83%]
tests/test_step4.py::test_update_item_updates_both_fields PASSED         [ 87%]
tests/test_step4.py::test_update_item_keeps_existing_value_when_input_blank PASSED [ 91%]
tests/test_step4.py::test_update_item_persists_to_storage PASSED         [ 95%]
tests/test_step4.py::test_update_item_does_not_affect_other_records PASSED [100%]

============================= 24 passed in 0.16s ==============================
```

Step 0~3 테스트 19건을 포함해 총 24건 모두 통과했다 (기존 테스트 회귀 없음).
