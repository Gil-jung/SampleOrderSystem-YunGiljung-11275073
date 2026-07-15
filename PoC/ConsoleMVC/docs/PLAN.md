# 구현 계획 (Step-by-Step)

주문관리 시스템을 예제로 한 콘솔 MVC PoC의 구현 절차와 각 단계의 세부 설계 결정을 기록한다.
전체 결과 요약과 검증 결과는 [`../PoC.md`](../PoC.md)를 참고한다.

## Step 1 — Model 계층 구현

**대상 파일**: `model/product.py`, `model/order.py`

- `Product`
  - `dataclass(frozen=True)`로 불변 값 객체로 설계 — 한 번 생성된 상품 정보(가격 등)가
    주문 처리 도중 임의로 바뀌는 사고를 원천 차단하기 위함.
  - `price < 0` 검증을 `__post_init__`에서 수행.
- `OrderItem`
  - `product`(참조)와 `quantity`만 보유, `subtotal` 프로퍼티로 소계 계산.
  - `quantity <= 0`을 생성 시점에 거부.
- `OrderStatus` (Enum)
  - `주문생성 / 결제완료 / 배송중 / 배송완료 / 주문취소` 5단계.
- `_ALLOWED_TRANSITIONS` (모듈 전역 상수)
  - 상태 → 허용된 다음 상태 집합을 명시적으로 정의.
  - 전이 규칙을 코드 곳곳에 흩어진 `if`문이 아니라 단일 테이블로 관리해 규칙 추가/검토를 한 곳에서 하도록 함.
- `Order`
  - `add_item` / `remove_item`: `CREATED` 상태에서만 허용.
  - `add_item`은 동일 `product_id`가 있으면 수량을 누적(중복 라인 생성 방지).
  - `change_status`: 동일 상태로의 재전이 거부, `_ALLOWED_TRANSITIONS` 미포함 전이 거부,
    상품이 없는 상태에서 `PAID`로의 전이 거부(결제 전 최소 조건).
  - 모든 규칙 위반은 `OrderError`(전용 예외)로 통일 — Controller가 잡아서 View로 넘기기 쉽게 하기 위함.

## Step 2 — Controller 계층 구현

**대상 파일**: `controller/order_controller.py`

- `OrderController`는 주문을 `dict[order_id, Order]`로 메모리에 보관 (영속화는 범위 밖).
- `order_id`는 `ORD-0001`부터 순번 발급 — 클라이언트가 ID 형식을 신경 쓰지 않게 함.
- 모든 조작 메서드(`create_order`, `add_item`, `remove_item`, `change_status`, `cancel_order`)는
  **Model에 위임만 하고 규칙을 재구현하지 않는다** — 규칙의 단일 진실 공급원(SSOT)을 Model에 유지.
- `get_order_data` / `list_orders_data`는 `Order` 객체를 그대로 반환하지 않고
  **순수 `dict`로 변환**해서 반환 — View가 Model 클래스를 import하지 않도록 계층 경계를 강제.
- 존재하지 않는 `order_id` 조회 시 `OrderError`로 실패 — Controller 자신의 책임 영역(라우팅/조회)에서
  발생하는 유일한 예외.

## Step 3 — View 계층 구현

**대상 파일**: `view/order_view.py`

- `OrderView`는 상태를 갖지 않는 `staticmethod` 모음으로 설계 — 순수 함수라 테스트가 간단함.
- `render_order`: 단일 주문을 사람이 읽을 여러 줄 문자열로 변환.
- `render_order_list`: 주문이 없을 때 안내 문구, 여러 건일 때 구분선 없이 개행으로 나열.
- `render_error`: `OrderError` 메시지를 `[오류] ...` 형식으로 통일 — Controller/Model이 던진
  예외 메시지를 그대로 화면에 노출하지 않고 View가 포맷을 책임지도록 함.
- View는 `model` 패키지를 전혀 import하지 않음 (의도적 제약, Step 4의 테스트로 검증).

## Step 4 — 시나리오 테스트 작성 및 실행

**대상 파일**: `tests/test_order_scenario.py`, `main.py`

- pytest 기반, 정상 흐름 5건 + 예외/경계 케이스 8건 = 13개 시나리오.
- 설계 원칙:
  - 정상 흐름(생성 → 상품 추가 → 결제 → 배송 → 완료, 취소)은 실제 사용자가 따라갈 경로를 그대로 재현.
  - 경계/예외 케이스는 Model의 규칙 하나당 최소 1개 테스트를 대응시켜 "규칙이 있는데 테스트가 없는" 사각을 없앰.
  - `test_view는_controller가_준_데이터만으로_렌더링한다`로 View→Model 직접 의존이 없음을 회귀 검증.
- `main.py`는 pytest로 다루기 번거로운 "터미널에 실제로 어떻게 보이는가"를 눈으로 확인하기 위한
  최소 데모 스크립트 (정상 라이프사이클 + 마지막에 의도적으로 잘못된 전이를 시도해 오류 출력까지 확인).
- 실행:
  ```
  python -m pytest tests/ -v   # 13 passed
  python main.py               # 정상 처리 + 오류 메시지 출력 확인
  ```
  Windows 콘솔 인코딩 문제로 한글이 깨지면 `PYTHONIOENCODING=utf-8`로 재실행.

## Step 5 — PoC.md 문서화

**대상 파일**: `PoC.md`

- 구조(패키지 트리), 계층별 책임 표, 상태 전이 다이어그램, 시나리오 표, 실제 실행 로그, 결론 순으로 정리.
- 이 PoC가 콘솔(CLI) 애플리케이션이라는 아키텍처 성격을 명시(웹/GUI 프레임워크 없음).
- "구조만 있고 동작하지 않는 스켈레톤"이 아니라 end-to-end로 검증됐다는 결론으로 마무리.

## TDD 진행 이력 (Red → Green)

Step 1~4는 위 설계가 끝난 상태의 코드를 기준으로, 계층별 규칙을 각각 잠깐 제거해
테스트가 실패(RED)함을 먼저 확인한 뒤 규칙을 복구해 통과(GREEN)시키는 방식으로
재검증했다. GREEN에 도달할 때마다 해당 테스트 파일과 구현 diff를 커밋·푸시했다.

| 커밋 | 계층 | RED 유발 방법 | 확인한 실패 |
|---|---|---|---|
| `TDD: Product 모델 단위 테스트 추가` | Model (`product.py`) | `__post_init__` 검증 제거 | `ValueError` 미발생 |
| `TDD: Order 상태 전이 규칙 테스트 추가` | Model (`order.py`) | `change_status` 검증 로직 제거 | 잘못된 전이/무상품 결제/종결 상태 이후 전이가 `OrderError` 없이 통과 |
| `TDD: OrderController 단위 테스트 추가` | Controller | `_get_order`의 None 체크 제거 | `OrderError` 대신 `AttributeError` 발생 |
| `TDD: OrderView 단위 테스트 추가` | View | `render_error`의 `[오류]` 접두어 제거 | 포맷 불일치로 assert 실패 |

각 단계는 해당 계층 테스트만 대상으로 실행(`pytest tests/test_xxx.py`)해 RED/GREEN을
빠르게 확인했고, 마지막 Step 5에서 `tests/` 전체(신규 단위 테스트 + 기존
`test_order_scenario.py` 통합 테스트, 총 34개)와 `main.py` 데모를 함께 재실행해
회귀가 없음을 확인했다.

```
$ python -m pytest tests/ -v
...
============================= 34 passed in 0.04s ==============================
```

## 향후 확장 시 고려사항

- 결제 연동, 재고 차감, DB 영속화 등은 Controller 아래에 별도 Service/Repository 계층을 추가해서 확장.
  Model/View의 인터페이스(`Order`의 public 메서드, View가 소비하는 `dict` 스키마)는 그대로 유지 가능.
- 상태 전이 규칙이 늘어나면 `_ALLOWED_TRANSITIONS` 테이블만 수정하면 되도록 이미 구조화되어 있음.
