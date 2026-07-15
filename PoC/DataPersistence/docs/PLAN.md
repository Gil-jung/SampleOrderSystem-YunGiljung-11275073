# JSON CRUD 콘솔 애플리케이션 구현 계획 (PLAN)

`PoC.md`에서 정의한 구조와 방향을 그대로 따르는 단계별 구현 계획이다.
각 Step은 순서대로 진행하며, 이전 Step이 끝난 뒤 다음 Step으로 넘어간다.

## Step 0. 프로젝트 준비

- 대상 구조 생성
  ```
  jsonCRUD/
  ├── main.py
  ├── storage.py
  ├── crud.py
  ├── data.json      # 최초 실행 시 자동 생성되므로 미리 만들지 않음
  ├── PoC.md
  └── docs/
      └── PLAN.md
  ```
- Python 버전: 3.13 (`.venv` 기존 가상환경 사용)
- 외부 패키지 설치 불필요 (표준 라이브러리 `json`, `os`만 사용)

**완료 기준**: 위 파일들이 생성되고 `.venv` 인터프리터로 실행 가능한 상태.

---

## Step 1. `storage.py` — 데이터 영속화 계층 구현

파일 존재 여부와 무관하게 항상 안전하게 데이터를 읽고 쓸 수 있는 함수 2개를 구현한다.

- [ ] `DATA_FILE = "data.json"` 경로 상수 정의
- [ ] `load_data()`
  - 파일이 없으면 빈 리스트 `[]` 반환 (최초 실행 대응)
  - 있으면 `json.load()`로 파싱하여 반환
  - 인코딩은 `utf-8` 고정
- [ ] `save_data(data)`
  - `json.dump(data, f, ensure_ascii=False, indent=2)`로 기록
  - 한글 등 비 ASCII 문자가 유니코드 이스케이프 없이 저장되는지 확인

**검증 방법**: 파이썬 인터프리터에서 `load_data()` → `[]` 반환 확인, 임의 데이터로 `save_data()` 호출 후 `data.json` 내용을 직접 열어 들여쓰기/한글 표시 확인.

---

## Step 2. `crud.py` — Create 기능 구현

- [ ] `create_item()` 함수 작성
  - `storage.load_data()`로 기존 데이터 로드
  - 신규 `id` 산출: `max(item["id"] for item in data, default=0) + 1`
  - `input()`으로 `name`, `email` 입력받기 (공백 제거 `strip()`)
  - 새 레코드를 `dict`로 구성해 리스트에 `append`
  - `storage.save_data(data)` 호출로 즉시 저장
  - 완료 메시지 출력 (`[생성 완료] id={new_id}`)

**검증 방법**: 데이터가 없는 상태에서 최초 생성 시 `id=1` 부여 확인, 이후 연속 생성 시 `id`가 1씩 증가하는지 확인.

---

## Step 3. `crud.py` — Read 기능 구현 (전체 조회 / 단일 검색)

- [ ] `read_all()` 함수 작성
  - 데이터가 비어있으면 "데이터가 없습니다." 출력 후 종료
  - 있으면 각 레코드를 한 줄씩 출력
- [ ] `read_one()` 함수 작성
  - `id` 입력받아 문자열 비교(`str(item["id"]) == target_id`)로 검색
  - 일치하는 레코드 발견 시 출력 후 반환
  - 없으면 "id={target_id} 데이터를 찾을 수 없습니다." 출력

**검증 방법**: 여러 건 생성 후 전체 목록에 모두 표시되는지 확인, 존재하는/존재하지 않는 `id`로 각각 단일 검색 테스트.

---

## Step 4. `crud.py` — Update 기능 구현

- [ ] `update_item()` 함수 작성
  - `id` 입력받아 대상 레코드 탐색
  - 대상이 없으면 안내 메시지 출력 후 종료
  - 대상이 있으면 각 필드(`name`, `email`)에 대해 현재 값을 보여주고 새 값 입력받기
  - 입력이 빈 문자열이면 기존 값 유지, 값이 있으면 필드 갱신
  - 변경 후 `storage.save_data(data)` 호출
  - 완료 메시지 출력

**검증 방법**: 일부 필드만 수정(Enter로 스킵)했을 때 나머지 필드가 유지되는지 확인, 파일에 반영되는지 재조회로 확인.

---

## Step 5. `crud.py` — Delete 기능 구현 (안전 삭제)

- [ ] `delete_item()` 함수 작성
  - `id` 입력받아 대상 레코드 탐색
  - 대상이 없으면 안내 메시지 출력 후 종료
  - 대상이 있으면 삭제 전 확인 메시지 출력: `"'{item}' 항목을 삭제하시겠습니까? (y/n): "`
  - 입력이 `y`(소문자 변환 후 비교)인 경우에만 `data.remove(item)` 수행 후 저장
  - `y`가 아니면 "삭제가 취소되었습니다." 출력하고 데이터 변경 없음

**검증 방법**: 삭제 확인 단계에서 `n` 입력 시 데이터가 유지되는지, `y` 입력 시에만 파일에서 제거되는지 확인.

---

## Step 6. `main.py` — 메뉴 루프 및 통합

- [ ] `crud.py`에서 5개 함수(`create_item`, `read_all`, `read_one`, `update_item`, `delete_item`) import
- [ ] `print_menu()` 함수로 메뉴 출력
  ```
  1. Create  2. Read All  3. Read One  4. Update  5. Delete  6. Exit
  ```
- [ ] `main()` 함수에서 `while True` 루프로 사용자 입력을 받아 분기 처리
  - 1~5: 해당 CRUD 함수 호출
  - 6: 종료 메시지 출력 후 `break`
  - 그 외: "잘못된 입력입니다." 출력
- [ ] `if __name__ == "__main__": main()` 진입점 작성

**검증 방법**: `python main.py` 실행 후 각 메뉴 번호로 Create → Read All → Read One → Update → Read One(재확인) → Delete → Read All(재확인) → Exit 순서로 전체 시나리오 수동 테스트.

---

## Step 7. 통합 테스트 (End-to-End 시나리오)

아래 순서로 콘솔에서 직접 실행하며 확인한다.

1. `data.json`이 없는 상태에서 실행 → Read All 시 "데이터가 없습니다." 확인
2. Create로 2건 입력 (`id=1`, `id=2` 자동 부여 확인)
3. Read All로 2건 모두 출력되는지 확인
4. Read One으로 `id=1` 단건 검색 확인
5. Update로 `id=1`의 `email`만 변경 (name은 Enter로 스킵) → Read One으로 재확인
6. Delete로 `id=2` 삭제 시도 → `n` 입력 후 유지 확인 → 다시 시도 → `y` 입력 후 삭제 확인
7. Read All로 `id=1`만 남아있는지 최종 확인
8. `data.json` 파일을 직접 열어 위 시나리오 결과가 정확히 반영됐는지 확인 (인코딩, 들여쓰기 포함)

**완료 기준**: 위 8단계가 모두 예상대로 동작하고, `PoC.md`에 정의된 코드 구조(파일 분리, 함수 시그니처)가 그대로 유지된 상태.

---

## 산출물 요약

| 파일 | 역할 | 관련 Step |
|---|---|---|
| `storage.py` | JSON 파일 로드/저장 | Step 1 |
| `crud.py` | Create/Read/Update/Delete 함수 | Step 2~5 |
| `main.py` | 메뉴 루프, 진입점 | Step 6 |
| `data.json` | 실제 데이터 저장 파일 (자동 생성) | Step 1~7 |
