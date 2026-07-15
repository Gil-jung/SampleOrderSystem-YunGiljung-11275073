# Step 5. `crud.py` — Delete 기능 구현 (안전 삭제) (세부 구현사항)

`PLAN.md`의 Step 5 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 코드를 구현한다.

## 1. 목표

`id`로 대상 레코드를 찾아 삭제 전 사용자 확인(y/n)을 거친 뒤에만 실제로 제거하는 `delete_item()`을
`crud.py`에 구현한다. 확인 없이 즉시 삭제되지 않도록 하여 오삭제를 방지한다.

## 2. 함수 시그니처 및 동작 정의

### `delete_item() -> None`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 (내부에서 `input()`으로 `id` 및 확인 여부 입력) |
| 출력 | 없음 (완료/취소/실패 메시지 콘솔 출력) |
| 의존 | `storage.load_data()`, `storage.save_data()` |

동작 순서:

1. `storage.load_data()`로 전체 데이터 로드
2. `input()`으로 삭제할 `id` 입력받기 (`strip()` 적용, 기존 함수들과 동일하게 문자열 비교)
3. `id`가 일치하는 레코드를 찾지 못하면 `"id={target_id} 데이터를 찾을 수 없습니다."` 출력 후 종료
4. 일치하는 레코드를 찾으면 삭제 확인 메시지 출력: `"'{item}' 항목을 삭제하시겠습니까? (y/n): "`
5. 입력값을 소문자로 변환(`.strip().lower()`) 후 `"y"`와 비교
   - `"y"`인 경우에만 `data.remove(item)` 수행 후 `storage.save_data(data)` 호출, `[삭제 완료] id={target_id}` 출력
   - `"y"`가 아닌 모든 입력(`"n"`, 빈 문자열, 오타 등)은 `"삭제가 취소되었습니다."` 출력, 데이터/파일 변경 없음

```python
def delete_item():
    data = load_data()
    target_id = input("삭제할 id: ").strip()

    for item in data:
        if str(item["id"]) == target_id:
            confirm = input(f"'{item}' 항목을 삭제하시겠습니까? (y/n): ").strip().lower()
            if confirm == "y":
                data.remove(item)
                save_data(data)
                print(f"[삭제 완료] id={target_id}")
            else:
                print("삭제가 취소되었습니다.")
            return

    print(f"id={target_id} 데이터를 찾을 수 없습니다.")
```

## 3. 고려한 예외/경계 케이스

- **존재하지 않는 id**: 데이터가 없거나 대상 `id`가 없으면 확인 절차 없이 바로 안내 메시지만 출력한다.
- **확인 거부(`n`)**: 대상을 찾았더라도 `y`가 아니면 삭제하지 않고 취소 메시지만 출력, `save_data()`는 호출되지 않는다.
- **대소문자 무시**: `Y`, `y` 모두 삭제로 인정되도록 `.lower()`로 정규화한다.
- **애매한 입력**: `"yes"`처럼 `"y"`가 아닌 다른 문자열은 모두 취소로 처리한다 (엄격하게 `"y"`만 인정).
- **다른 레코드에 영향 없음**: 여러 레코드가 있을 때 대상이 아닌 레코드는 삭제 후에도 그대로 남아 있어야 한다.
- **삭제 후 파일 반영**: 삭제가 확정된 경우에만 `storage.save_data()`로 즉시 파일에 반영되어야 한다.

## 4. 테스트 계획 (`tests/test_step5.py`, pytest)

`storage.DATA_FILE`을 `tmp_path`로 격리하고, `input()`은 `monkeypatch`로 순서대로 값을 반환하도록 대체한다.
콘솔 출력 검증은 `capsys`를 사용한다.

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_delete_item_reports_when_id_not_found` | 존재하지 않는 `id` 입력 시 "찾을 수 없습니다" 메시지 출력, 데이터 변경 없음 확인 |
| `test_delete_item_cancels_when_not_confirmed` | 대상은 존재하나 확인 입력이 `n`인 경우 "삭제가 취소되었습니다." 출력, 데이터가 그대로 유지되는지 확인 |
| `test_delete_item_removes_when_confirmed` | 확인 입력이 `y`인 경우 대상 레코드가 실제로 제거되고 `[삭제 완료]` 메시지가 출력되는지 확인 |
| `test_delete_item_confirmation_is_case_insensitive` | 확인 입력이 `Y`(대문자)여도 삭제가 수행되는지 확인 |
| `test_delete_item_does_not_affect_other_records` | 레코드 2건 중 1건만 삭제(`y`) 시 나머지 레코드는 그대로 남아있는지 확인 |
| `test_delete_item_persists_removal_to_storage` | 삭제 후 `storage.load_data()`로 재조회 시 실제로 제거되어 있는지 확인 |

```python
def test_delete_item_cancels_when_not_confirmed(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    inputs = iter(["1", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.delete_item()

    captured = capsys.readouterr()
    assert "삭제가 취소되었습니다." in captured.out
    assert storage.load_data() == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]
```

## 5. 검증 방법 (수동)

```bash
.venv/Scripts/python.exe -m pytest tests/test_step5.py -v
```

- 위 6개 테스트 모두 통과해야 Step 5 완료로 간주한다.
- 전체 회귀 확인을 위해 `tests/` 전체(`test_step0.py`~`test_step5.py`)도 함께 실행한다.

## 6. 완료 기준

- [x] `crud.py`에 `delete_item()` 구현 완료
- [x] `tests/test_step5.py` 작성 및 전체 통과 (기존 테스트 회귀 없음)
- [x] `docs/step5.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬

## 7. 구현 결과

`crud.py`는 2절에서 계획한 코드 그대로 구현되었다 (계획과 실제 구현 간 차이 없음). `delete_item`은
기존 `update_item` 아래에 이어서 추가했다. 이로써 `PoC.md`에서 정의한 5개 CRUD 함수
(`create_item`, `read_all`, `read_one`, `update_item`, `delete_item`)가 모두 `crud.py`에 구현 완료되었다.

### 7.1 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
tests/test_step0.py::test_skeleton_files_exist PASSED                    [  3%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [  6%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [ 10%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [ 13%]
tests/test_step1.py::test_load_data_returns_empty_list_when_file_missing PASSED [ 16%]
tests/test_step1.py::test_save_then_load_round_trip PASSED               [ 20%]
tests/test_step1.py::test_save_data_preserves_korean_without_unicode_escape PASSED [ 23%]
tests/test_step1.py::test_save_data_writes_indented_json PASSED          [ 26%]
tests/test_step1.py::test_save_empty_list PASSED                         [ 30%]
tests/test_step2.py::test_create_item_assigns_id_1_when_empty PASSED     [ 33%]
tests/test_step2.py::test_create_item_increments_id_sequentially PASSED  [ 36%]
tests/test_step2.py::test_create_item_does_not_reuse_deleted_id PASSED   [ 40%]
tests/test_step2.py::test_create_item_saves_stripped_input PASSED        [ 43%]
tests/test_step2.py::test_create_item_persists_to_storage PASSED         [ 46%]
tests/test_step3.py::test_read_all_prints_message_when_empty PASSED      [ 50%]
tests/test_step3.py::test_read_all_prints_all_items PASSED               [ 53%]
tests/test_step3.py::test_read_one_finds_existing_id PASSED              [ 56%]
tests/test_step3.py::test_read_one_reports_when_id_not_found PASSED      [ 60%]
tests/test_step3.py::test_read_one_handles_non_numeric_input_gracefully PASSED [ 63%]
tests/test_step4.py::test_update_item_reports_when_id_not_found PASSED   [ 66%]
tests/test_step4.py::test_update_item_updates_both_fields PASSED         [ 70%]
tests/test_step4.py::test_update_item_keeps_existing_value_when_input_blank PASSED [ 73%]
tests/test_step4.py::test_update_item_persists_to_storage PASSED         [ 76%]
tests/test_step4.py::test_update_item_does_not_affect_other_records PASSED [ 80%]
tests/test_step5.py::test_delete_item_reports_when_id_not_found PASSED   [ 83%]
tests/test_step5.py::test_delete_item_cancels_when_not_confirmed PASSED  [ 86%]
tests/test_step5.py::test_delete_item_removes_when_confirmed PASSED      [ 90%]
tests/test_step5.py::test_delete_item_confirmation_is_case_insensitive PASSED [ 93%]
tests/test_step5.py::test_delete_item_does_not_affect_other_records PASSED [ 96%]
tests/test_step5.py::test_delete_item_persists_removal_to_storage PASSED [100%]

============================= 30 passed in 0.18s ==============================
```

Step 0~4 테스트 24건을 포함해 총 30건 모두 통과했다 (기존 테스트 회귀 없음).
