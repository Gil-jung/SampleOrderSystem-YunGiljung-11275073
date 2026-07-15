# JSON CRUD 콘솔 애플리케이션 PoC

## 1. 개요

JSON 파일을 저장소로 사용하는 데이터 관리 콘솔 애플리케이션의 PoC(Proof of Concept)이다.
별도의 DB 없이 로컬 JSON 파일에 데이터를 영속화하고, 콘솔 메뉴를 통해 CRUD(Create/Read/Update/Delete) 기능을 제공하는 것을 목표로 한다.

- 언어: Python 3.13
- 저장 형식: JSON (UTF-8)
- 실행 방식: 콘솔(터미널) 기반 대화형 메뉴

## 2. JSON 파싱 / 저장 라이브러리

Python 표준 라이브러리인 `json` 모듈을 사용한다. 별도 외부 패키지 설치 없이 바로 사용 가능하다.

| 기능 | 함수 | 설명 |
|---|---|---|
| 파일 → 파이썬 객체 | `json.load(fp)` | 파일 객체를 읽어 dict/list로 파싱 |
| 문자열 → 파이썬 객체 | `json.loads(s)` | 문자열을 파싱 |
| 파이썬 객체 → 파일 | `json.dump(obj, fp)` | 파이썬 객체를 파일에 기록 |
| 파이썬 객체 → 문자열 | `json.dumps(obj)` | 파이썬 객체를 문자열로 직렬화 |

예시:

```python
import json

# 읽기
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 쓰기
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

`ensure_ascii=False` : 한글 등 비 ASCII 문자를 유니코드 이스케이프(`\uXXXX`) 없이 그대로 저장.
`indent=2` : 사람이 읽기 좋은 형태로 들여쓰기 저장.

## 3. 데이터 구조

`data.json` 파일 하나에 레코드 배열을 저장한다. 각 레코드는 고유 `id` 필드를 가진다.

```json
[
  {
    "id": 1,
    "name": "홍길동",
    "email": "hong@example.com"
  },
  {
    "id": 2,
    "name": "김철수",
    "email": "kim@example.com"
  }
]
```

- `id`는 자동 증가(auto-increment)로 부여한다. (기존 레코드 중 최댓값 + 1)
- 필드 구성은 예시이며, 실제 도메인에 맞게 조정 가능하다.

## 4. 프로그램 구조 (PoC 코드 구조)

단일 파일 또는 최소 모듈 구성으로 유지하며, 아래 구조를 CRUD 구현 시에도 그대로 따른다.

```
jsonCRUD/
├── main.py          # 진입점, 메뉴 루프
├── storage.py        # JSON 파일 읽기/쓰기 담당 (load_data, save_data)
├── crud.py            # Create/Read/Update/Delete 함수
└── data.json          # 실제 데이터 저장 파일 (최초 실행 시 자동 생성)
```

### 4.1 storage.py

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

### 4.2 main.py (메뉴 루프)

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

## 5. CRUD 기능 구현 상세

### 5.1 Create — 신규 데이터 입력 및 저장

- 사용자로부터 필드 값을 입력받는다.
- `id`는 자동 채번(기존 데이터 중 최댓값 + 1, 데이터가 없으면 1).
- 리스트에 append 후 `save_data()`로 파일에 즉시 반영.

```python
def create_item():
    data = load_data()
    new_id = max([item["id"] for item in data], default=0) + 1
    name = input("이름: ").strip()
    email = input("이메일: ").strip()

    data.append({"id": new_id, "name": name, "email": email})
    save_data(data)
    print(f"[생성 완료] id={new_id}")
```

### 5.2 Read — 전체 목록 조회 / ID 검색

- 전체 목록: 저장된 모든 레코드를 표 형태로 출력.
- 단일 검색: `id` 입력 → 일치하는 레코드 출력, 없으면 안내 메시지.

```python
def read_all():
    data = load_data()
    if not data:
        print("데이터가 없습니다.")
        return
    for item in data:
        print(item)

def read_one():
    data = load_data()
    target_id = input("조회할 id: ").strip()
    for item in data:
        if str(item["id"]) == target_id:
            print(item)
            return
    print(f"id={target_id} 데이터를 찾을 수 없습니다.")
```

### 5.3 Update — 기존 데이터 필드 수정

- `id`로 대상 레코드를 먼저 조회.
- 존재하면 수정할 필드(예: name, email)를 선택 후 새 값 입력, 빈 입력은 변경하지 않음.
- 수정 후 `save_data()`로 즉시 반영.

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

### 5.4 Delete — 특정 데이터 안전 삭제

- `id`로 대상 레코드 조회 후 존재 여부 확인.
- 삭제 전 사용자에게 확인(y/n)을 받아 오삭제를 방지 (안전한 삭제).
- 확인되면 리스트에서 제거하고 파일에 저장.

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

## 6. 향후 확장 고려 사항 (PoC 범위 밖)

- 입력값 검증(이메일 형식, 중복 체크 등)
- 파일 동시 접근 시 락(lock) 처리
- 대용량 데이터 시 파일 전체 로드/저장 방식의 성능 한계 → DB 전환 검토
- 예외 처리(파일 손상, 권한 오류 등) 보강
