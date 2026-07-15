# Step 2. `crud.py` — Create 기능 구현 (세부 구현사항)

`PLAN.md`의 Step 2 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 코드를 구현한다.

## 1. 목표

사용자로부터 신규 레코드 정보를 입력받아 `id`를 자동 채번한 뒤 `storage.py`를 통해 `data.json`에 저장하는
`create_item()` 함수를 `crud.py`에 구현한다.

## 2. 함수 시그니처 및 동작 정의

### `create_item() -> None`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 (내부에서 `input()`으로 대화형 입력) |
| 출력 | 없음 (완료 메시지 콘솔 출력) |
| 의존 | `storage.load_data()`, `storage.save_data()` |

동작 순서:

1. `storage.load_data()`로 기존 전체 데이터 로드
2. 신규 `id` 산출: `max(item["id"] for item in data, default=0) + 1`
   - 데이터가 없으면 `1`, 있으면 기존 최댓값 + 1 (삭제로 인한 중간 번호 결번은 허용, 재사용하지 않음)
3. `input()`으로 `name`, `email`을 입력받고 `strip()`으로 앞뒤 공백 제거
4. 신규 레코드 `dict`를 구성해 `data` 리스트에 `append`
5. `storage.save_data(data)`로 즉시 파일에 반영
6. `[생성 완료] id={new_id}` 형식으로 완료 메시지 출력

```python
from storage import load_data, save_data


def create_item():
    data = load_data()
    new_id = max((item["id"] for item in data), default=0) + 1

    name = input("이름: ").strip()
    email = input("이메일: ").strip()

    data.append({"id": new_id, "name": name, "email": email})
    save_data(data)
    print(f"[생성 완료] id={new_id}")
```

## 3. 고려한 예외/경계 케이스

- **최초 생성**: 데이터가 비어있는 상태(`[]`)에서 첫 호출 시 `id=1`이 부여되어야 한다.
- **연속 생성**: 여러 번 호출 시 `id`가 1씩 순차 증가해야 한다.
- **삭제 후 재생성**: 기존 레코드가 삭제되어 `id`에 결번이 생기더라도, 신규 `id`는 항상 "현재 남아있는 데이터의 최댓값 + 1"로 계산되므로 결번을 재사용하지 않는다. (Step 5 Delete와 연계되는 규칙이며, 이번 Step 테스트에서도 결번 상황을 가정해 검증한다.)
- **빈 입력값**: `name`/`email`을 빈 문자열로 입력해도 그대로 저장한다 (PoC 범위에서는 값 검증을 하지 않음 — `PoC.md` "향후 확장 고려 사항"에 명시된 대로 이번 Step 범위 밖).
- **`input()` 의존성 처리**: 콘솔 입력 함수를 직접 테스트하기 위해, `create_item()` 내부의 `input()` 호출을 pytest에서 `monkeypatch`로 대체한다 (아래 5절 참고).

## 4. 테스트 계획 (`tests/test_step2.py`, pytest)

`storage.DATA_FILE`을 `tmp_path`로 격리하고, `input()`을 `monkeypatch`로 미리 정해진 값을 순서대로 반환하도록 대체한다.

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_create_item_assigns_id_1_when_empty` | 데이터가 없는 상태에서 `create_item()` 호출 시 `id=1`로 저장되는지 확인 |
| `test_create_item_increments_id_sequentially` | 연속 2회 호출 시 `id`가 1, 2로 순차 부여되는지 확인 |
| `test_create_item_does_not_reuse_deleted_id` | `id=1,3`만 남아 중간 번호(`2`)가 결번인 상태에서 `create_item()` 호출 시, 결번(`2`)을 재사용하지 않고 현재 최댓값(`3`) + 1인 `4`가 부여되는지 확인 |
| `test_create_item_saves_stripped_input` | 입력값 앞뒤 공백이 제거되어 저장되는지 확인 (`"  홍길동  "` → `"홍길동"`) |
| `test_create_item_persists_to_storage` | `create_item()` 호출 후 `storage.load_data()`로 다시 읽었을 때 새 레코드가 실제로 반영되어 있는지 확인 |

`input()` 모킹 예시:

```python
def test_create_item_assigns_id_1_when_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    inputs = iter(["홍길동", "hong@example.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    crud.create_item()

    data = storage.load_data()
    assert data == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]
```

## 5. 검증 방법 (수동)

```bash
.venv/Scripts/python.exe -m pytest tests/test_step2.py -v
```

- 위 5개 테스트 모두 통과해야 Step 2 완료로 간주한다.
- 전체 회귀 확인을 위해 `tests/` 전체(`test_step0.py`, `test_step1.py`, `test_step2.py`)도 함께 실행한다.

## 6. 완료 기준

- [x] `crud.py`에 `create_item()` 구현 완료
- [x] `tests/test_step2.py` 작성 및 전체 통과 (기존 테스트 회귀 없음)
- [x] `docs/step2.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬

## 7. 구현 결과

`crud.py`는 3절에서 계획한 코드 그대로 구현되었다 (계획과 실제 구현 간 차이 없음).

`test_create_item_does_not_reuse_deleted_id` 테스트는 계획 문서 작성 시의 시나리오(`id=1,2` 중 `2` 삭제 → `3` 부여)가
실제 `max+1` 로직과 맞지 않아(남은 데이터가 `[1]`뿐이면 새 id는 `2`가 되어 오히려 결번을 재사용함) 검토 과정에서 발견,
`id=1,3`만 남아 중간 결번(`2`)이 있는 상태 → 새 id는 현재 최댓값(`3`) + 1인 `4`로 수정했다.
이는 "결번을 재사용하지 않는다"는 규칙이 삭제된 항목이 항상 최댓값이 아닐 때 성립함을 보여준다 (5절 표에 반영 완료).

### 7.1 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
tests/test_step0.py::test_skeleton_files_exist PASSED                    [  7%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [ 14%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [ 21%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [ 28%]
tests/test_step1.py::test_load_data_returns_empty_list_when_file_missing PASSED [ 35%]
tests/test_step1.py::test_save_then_load_round_trip PASSED               [ 42%]
tests/test_step1.py::test_save_data_preserves_korean_without_unicode_escape PASSED [ 50%]
tests/test_step1.py::test_save_data_writes_indented_json PASSED          [ 57%]
tests/test_step1.py::test_save_empty_list PASSED                         [ 64%]
tests/test_step2.py::test_create_item_assigns_id_1_when_empty PASSED     [ 71%]
tests/test_step2.py::test_create_item_increments_id_sequentially PASSED  [ 78%]
tests/test_step2.py::test_create_item_does_not_reuse_deleted_id PASSED   [ 85%]
tests/test_step2.py::test_create_item_saves_stripped_input PASSED        [ 92%]
tests/test_step2.py::test_create_item_persists_to_storage PASSED         [100%]

============================= 14 passed in 0.10s ==============================
```

Step 0~1 테스트 9건을 포함해 총 14건 모두 통과했다 (기존 테스트 회귀 없음).
