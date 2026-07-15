# json_CRUD_consol_app

JSON 파일을 저장소로 사용하는 CRUD(Create/Read/Update/Delete) 콘솔 애플리케이션이다.
별도의 DB 없이 로컬 `data.json` 파일에 데이터를 영속화하고, 콘솔 메뉴를 통해 데이터를 관리한다.

- 언어: Python 3.13
- 저장 형식: JSON (UTF-8, 표준 라이브러리 `json` 모듈만 사용)
- 실행 방식: 콘솔(터미널) 기반 대화형 메뉴

## 프로젝트 구조

```
jsonCRUD/
├── main.py            # 진입점, 메뉴 루프
├── storage.py          # data.json 읽기/쓰기 (load_data, save_data)
├── crud.py              # Create/Read/Update/Delete 함수
├── data.json            # 실제 데이터 저장 파일 (최초 실행 시 자동 생성, git 추적 제외)
├── pytest.ini
├── tests/                # pytest 테스트 (총 48건)
│   ├── test_step0.py     # 프로젝트 스켈레톤 검증
│   ├── test_step1.py     # storage.py (load_data/save_data)
│   ├── test_step2.py     # crud.py Create
│   ├── test_step3.py     # crud.py Read
│   ├── test_step4.py     # crud.py Update
│   ├── test_step5.py     # crud.py Delete
│   ├── test_step6.py     # main.py 메뉴 루프
│   ├── test_step7_e2e.py # 전체 CRUD 흐름 E2E 시나리오
│   └── test_step8_regression_safety.py # 회귀/안전성 테스트
├── PoC.md                # 초기 PoC 설계 문서
└── docs/
    ├── PLAN.md            # 단계별(Step 0~7) 구현 계획
    └── step0.md ~ step8.md # 각 단계 세부 구현/테스트 결과 기록
```

## 실행 방법

```bash
# 가상환경 활성화 후
python main.py
```

메뉴에서 번호를 입력해 기능을 선택한다.

```
=== JSON CRUD ===
1. Create  2. Read All  3. Read One  4. Update  5. Delete  6. Exit
선택:
```

| 번호 | 기능 | 설명 |
|---|---|---|
| 1 | Create | 이름/이메일을 입력받아 새 레코드를 생성 (id 자동 채번) |
| 2 | Read All | 전체 레코드 목록 조회 |
| 3 | Read One | id로 특정 레코드 검색 |
| 4 | Update | id로 레코드를 찾아 필드별로 수정 (빈 입력은 기존 값 유지) |
| 5 | Delete | id로 레코드를 찾아 확인(y/n) 후 삭제 (오삭제 방지) |
| 6 | Exit | 프로그램 종료 |

## 데이터 구조

`data.json`에 레코드 배열을 저장하며, 각 레코드는 고유 `id`를 가진다.

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "email": "hong@example.com"
  }
]
```

## 테스트

```bash
python -m pytest tests/ -v
```

각 CRUD 함수, 메뉴 분기 로직, 전체 CRUD 흐름을 잇는 E2E 시나리오, 그리고 회귀/안전성 검증까지
총 48건의 pytest 테스트로 검증한다. 실제 `data.json`을 건드리지 않도록 `monkeypatch`로 `storage.DATA_FILE`을
임시 경로로 격리해 테스트를 실행한다.

`test_step8_regression_safety.py`는 과거 발견했던 이슈(id 채번 로직, 실제 프로세스 실행 시의 인코딩 문제 등)의
재발을 막는 회귀 테스트와, 오삭제 방지(엄격한 `y` 확인), 존재하지 않는 id에 대한 불필요한 파일 쓰기 없음,
특수 문자 round-trip 무결성, 레코드 스키마 유지 등 안전성 테스트를 포함한다.

## 문서

- [`PoC.md`](PoC.md) — 초기 PoC 설계(라이브러리 선정, 데이터 구조, 코드 구조)
- [`docs/PLAN.md`](docs/PLAN.md) — Step 0~7 구현 계획
- [`docs/step0.md`](docs/step0.md) ~ [`docs/step7.md`](docs/step7.md) — 각 단계별 세부 구현 내용과 테스트 결과
- [`docs/step8.md`](docs/step8.md) — 회귀/안전성 테스트 세부 내용

## 향후 확장 고려 사항

- 입력값 검증(이메일 형식, 중복 체크 등)
- 파일 동시 접근 시 락(lock) 처리
- 손상된 JSON 파일(`json.JSONDecodeError`)에 대한 예외 처리
- 대용량 데이터 시 파일 전체 로드/저장 방식의 성능 한계 → DB 전환 검토
