# Step 0. 프로젝트 준비 — 구현 문서

`PLAN.md`의 Step 0 항목을 실제로 수행한 내용을 기록한다.

## 1. 목표

`PoC.md`에서 정의한 파일 구조를 실제 프로젝트에 만들고, 이후 Step 1~7에서 각 파일의 내용을 채워나갈 수 있는 상태로 준비한다.

## 2. 수행 내용

### 2.1 파일 구조 생성

기존에 존재하던 `.idea/`, `.venv/`, `PoC.md`, `docs/` 외에 아래 3개 파일을 신규 생성했다.

```
jsonCRUD/
├── main.py        # 신규 생성 (스켈레톤)
├── storage.py      # 신규 생성 (스켈레톤)
├── crud.py          # 신규 생성 (스켈레톤)
├── PoC.md
└── docs/
    ├── PLAN.md
    └── step0.md      # 본 문서
```

`data.json`은 PLAN.md에 명시된 대로 최초 실행 시 자동 생성되므로 이 단계에서는 만들지 않았다.

### 2.2 각 파일 내용

**storage.py** — 이후 Step 1에서 구현할 `load_data()` / `save_data()`를 위한 상수만 선언.

```python
import json
import os

DATA_FILE = "data.json"
```

**crud.py** — 이후 Step 2~5에서 채워질 CRUD 함수 자리를 남겨둔 placeholder.

```python
# Create/Read/Update/Delete 함수는 Step 2~5에서 구현 예정
```

**main.py** — 이후 Step 6에서 채워질 메뉴 루프 자리를 남겨둔 placeholder. 이 시점에는 아무 동작 없이 정상 종료되어야 한다.

```python
# 메뉴 루프 및 진입점은 Step 6에서 구현 예정

if __name__ == "__main__":
    pass
```

`crud.py`가 `storage.py`의 함수를 아직 import하지 않도록 주석 처리했다. Step 1에서 `load_data`/`save_data`가 구현된 이후에 `crud.py`에서 import하도록 순서를 맞췄다 (Step 0 시점에 import하면 `ImportError` 발생하므로 방지).

## 3. 검증

```bash
.venv/Scripts/python.exe --version
# Python 3.13.9

.venv/Scripts/python.exe main.py
# (정상 종료, 출력 없음, 에러 없음)
```

- 가상환경(`.venv`, Python 3.13.9)의 인터프리터로 `main.py`가 예외 없이 실행됨을 확인했다.
- 외부 패키지 설치 없이 표준 라이브러리(`json`, `os`)만으로 구성되어 있음을 확인했다.

## 4. 결과

| 항목 | 상태 |
|---|---|
| `main.py` / `storage.py` / `crud.py` 생성 | 완료 |
| `.venv` 인터프리터로 실행 가능 | 완료 (에러 없이 종료 확인) |
| 외부 패키지 의존성 없음 | 완료 (`json`, `os`만 사용) |

**PLAN.md Step 0 완료 기준 충족.** 다음 단계는 `docs/PLAN.md`의 Step 1 — `storage.py`에 `load_data()` / `save_data()` 구현이다.

## 5. 테스트 (pytest)

`tests/` 폴더에 Step 0 완료 기준을 검증하는 `tests/test_step0.py`를 작성했다.

### 5.1 테스트 환경 설정

- `pytest.ini`에 `pythonpath = .` 설정을 추가하여, `tests/` 하위에서도 프로젝트 루트의 `storage.py` / `crud.py` / `main.py`를 바로 `import`할 수 있도록 했다.
- pytest 버전: 9.1.1 (`.venv`에 기 설치됨, 별도 설치 불필요).

### 5.2 테스트 케이스

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_skeleton_files_exist` | `main.py`, `storage.py`, `crud.py`가 프로젝트 루트에 실제로 존재하는지 확인 |
| `test_storage_module_is_importable_and_defines_data_file` | `storage` 모듈이 import 가능하고 `DATA_FILE == "data.json"`인지 확인 |
| `test_crud_module_is_importable` | `crud` 모듈이 (Step 0 시점의 placeholder 상태로도) import 시 에러가 없는지 확인 |
| `test_main_runs_without_error` | `subprocess`로 `main.py`를 실제 실행하여 종료 코드 0, `stderr` 빈 문자열인지 확인 (Step 0 완료 기준인 "예외 없이 실행"을 자동화) |

### 5.3 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/test_step0.py -v
```

```
tests/test_step0.py::test_skeleton_files_exist PASSED                    [ 25%]
tests/test_step0.py::test_storage_module_is_importable_and_defines_data_file PASSED [ 50%]
tests/test_step0.py::test_crud_module_is_importable PASSED               [ 75%]
tests/test_step0.py::test_main_runs_without_error PASSED                 [100%]

============================== 4 passed in 0.06s ==============================
```

4개 테스트 모두 통과하여 Step 0 완료 기준이 자동화된 테스트로도 검증되었다.
