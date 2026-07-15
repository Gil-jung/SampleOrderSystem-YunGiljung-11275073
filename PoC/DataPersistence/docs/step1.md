# Step 1. `storage.py` — 데이터 영속화 계층 구현 (세부 구현사항)

`PLAN.md`의 Step 1 항목에 대한 세부 구현 계획이다. **구현 전 검토용 문서**이며,
검토 완료 후 이 문서를 기준으로 실제 코드를 구현한다.

## 1. 목표

파일이 없어도 안전하게 동작하는 JSON 파일 읽기/쓰기 함수 2개(`load_data`, `save_data`)를 `storage.py`에 구현한다.
이후 모든 CRUD 함수(Step 2~5)는 이 두 함수만을 통해 데이터에 접근한다.

## 2. 함수 시그니처 및 동작 정의

### 2.1 `load_data() -> list`

| 항목 | 내용 |
|---|---|
| 입력 | 없음 (내부적으로 `DATA_FILE` 상수 사용) |
| 출력 | `list[dict]` — 저장된 레코드 목록 |
| 파일 없음 | `data.json`이 존재하지 않으면 예외를 던지지 않고 빈 리스트 `[]` 반환 (최초 실행 대응) |
| 파일 있음 | `json.load()`로 파싱하여 그대로 반환 |
| 인코딩 | `utf-8` 고정 |

```python
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
```

### 2.2 `save_data(data: list) -> None`

| 항목 | 내용 |
|---|---|
| 입력 | `data`: 저장할 `list[dict]` |
| 출력 | 없음 (파일에 기록) |
| 인코딩 옵션 | `ensure_ascii=False` — 한글 등 비 ASCII 문자를 유니코드 이스케이프 없이 저장 |
| 포맷 옵션 | `indent=2` — 사람이 읽기 좋은 들여쓰기 |

```python
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## 3. 고려한 예외/경계 케이스

- **파일 미존재**: `load_data()` 최초 호출 시 `data.json`이 없는 상태 → `[]` 반환. (PoC.md/PLAN.md에 명시된 요구사항)
- **빈 리스트 저장**: `save_data([])` 호출 시 `data.json`에 `[]`가 정상적으로 기록되어야 함 (Delete로 마지막 레코드까지 삭제된 경우 대비).
- **한글 데이터**: `save_data`로 한글 필드를 저장한 뒤 다시 `load_data`로 읽었을 때 원본과 동일해야 함(round-trip 무결성).
- **손상된 JSON 파일 처리(`json.JSONDecodeError`)는 이번 Step 범위에 포함하지 않는다.** PLAN.md의 "향후 확장 고려 사항"에 명시된 대로 이후 단계 과제로 남긴다.

## 4. 최종 `storage.py` 구현 예정 내용

```python
import json
import os

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

## 5. 테스트 계획 (`tests/test_step1.py`, pytest)

`data.json`은 프로젝트 루트에 실제로 생성/삭제되는 파일이므로, 테스트 간 간섭을 막기 위해 `pytest`의 `tmp_path` /
`monkeypatch`로 `storage.DATA_FILE`을 임시 경로로 바꿔가며 테스트한다 (실제 `data.json`을 건드리지 않음).

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_load_data_returns_empty_list_when_file_missing` | 파일이 없는 상태에서 `load_data()` 호출 시 `[]` 반환 확인 |
| `test_save_then_load_round_trip` | `save_data`로 저장 후 `load_data`로 읽었을 때 원본 데이터와 동일한지 확인 |
| `test_save_data_preserves_korean_without_unicode_escape` | 한글 필드를 저장한 파일을 직접 열어 `\uXXXX` 이스케이프 없이 한글 그대로 기록됐는지 확인 (`ensure_ascii=False` 검증) |
| `test_save_data_writes_indented_json` | 저장된 파일 내용에 줄바꿈/들여쓰기가 포함되어 있는지 확인 (`indent=2` 검증) |
| `test_save_empty_list` | 빈 리스트 저장 후 `load_data()`로 다시 읽었을 때 `[]`인지 확인 |

`monkeypatch.setattr(storage, "DATA_FILE", tmp_path / "data.json")` 방식으로 각 테스트를 격리한다.

## 6. 검증 방법 (수동)

```bash
.venv/Scripts/python.exe -m pytest tests/test_step1.py -v
```

- 위 5개 테스트 모두 통과해야 Step 1 완료로 간주한다.
- 추가로 인터프리터에서 직접 `load_data()` / `save_data()`를 호출해 `data.json` 파일 내용을 육안으로 확인한다.

## 7. 완료 기준

- [x] `storage.py`에 `load_data`, `save_data` 구현 완료
- [x] `tests/test_step1.py` 작성 및 전체 통과
- [x] `docs/step1.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] 커밋 & 푸쉬

## 8. 구현 결과

`storage.py`는 4절에서 계획한 코드 그대로 구현되었다 (계획과 실제 구현 간 차이 없음).

### 8.1 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
tests/test_step0.py::test_skeleton_files_exist PASSED                    [ 11%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [ 22%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [ 33%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [ 44%]
tests/test_step1.py::test_load_data_returns_empty_list_when_file_missing PASSED [ 55%]
tests/test_step1.py::test_save_then_load_round_trip PASSED               [ 66%]
tests/test_step1.py::test_save_data_preserves_korean_without_unicode_escape PASSED [ 77%]
tests/test_step1.py::test_save_data_writes_indented_json PASSED          [ 88%]
tests/test_step1.py::test_save_empty_list PASSED                         [100%]

============================== 9 passed in 0.08s ==============================
```

Step 0 테스트 4건을 포함해 총 9건 모두 통과했다. `monkeypatch`로 `storage.DATA_FILE`을 `tmp_path` 하위 경로로 교체했기 때문에,
테스트 실행 후 프로젝트 루트에 실제 `data.json`이 생성되지 않은 것도 확인했다 (테스트 격리 검증).
