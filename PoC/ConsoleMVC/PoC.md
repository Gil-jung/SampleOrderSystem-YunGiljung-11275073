# MVC 패턴 PoC — 주문관리 시스템

## 1. 목적

Model / View / Controller 세 계층의 역할을 명확히 분리한 스켈레톤을 만들고,
"주문관리 시스템"이라는 구체적인 시나리오로 각 계층의 동작을 검증하여
빠짐(누락) 없이 동작하는 MVC 구현임을 증명한다.

> **아키텍처 성격**: 본 PoC는 웹 프레임워크나 GUI 없이 순수 Python으로 동작하는
> **콘솔(CLI) 애플리케이션**이다. `View`는 HTML/템플릿이 아닌 표준 출력(stdout)으로
> 렌더링되는 텍스트 문자열이며, `Controller`는 HTTP 요청이 아닌 `main.py`의 함수 호출과
> pytest 테스트 코드로 트리거된다. MVC의 계층 분리 원칙 자체를 검증하는 것이 목적이므로
> 입출력 방식(콘솔)은 최소한으로 단순화했다.

## 2. 패키지 구조

```
MVC/
├── model/
│   ├── product.py           # Product (불변 값 객체)
│   └── order.py             # Order, OrderItem, OrderStatus, OrderError
├── view/
│   └── order_view.py        # OrderView (렌더링 전담, 로직 없음)
├── controller/
│   └── order_controller.py  # OrderController (유스케이스 조율)
├── tests/
│   └── test_order_scenario.py
├── main.py                  # 데모 실행 진입점
└── PoC.md
```

## 3. 계층별 역할 분리

| 계층 | 책임 | 하지 않는 일 |
|---|---|---|
| **Model** (`model/`) | 주문 데이터와 비즈니스 규칙(상태 전이 유효성, 합계 계산, 수량 검증)을 스스로 보장한다. | 출력 포맷, 사용자 입력 처리 |
| **Controller** (`controller/`) | 사용자 유스케이스(주문 생성/상품 추가/상태 변경)를 Model에 위임하고, View에는 순수 `dict` 형태의 데이터만 넘긴다. | 문자열 포맷팅, 상태 전이 규칙 자체의 구현(그건 Model의 책임) |
| **View** (`view/`) | Controller가 준 데이터를 사람이 읽을 문자열로 변환한다. | 주문 상태를 직접 변경하거나 Model 객체를 참조하는 일 |

의존 방향은 `Controller → Model`, `Controller → View` 단방향이며,
`View`는 `Model`을 알지 못하고 `dict` 스키마만 안다 (`test_view는_controller가_준_데이터만으로_렌더링한다`로 검증).

### 상태 전이 규칙 (Model, `model/order.py`)

```
주문생성 → 결제완료 → 배송중 → 배송완료
   └────────→ 주문취소
결제완료 ──────→ 주문취소
```

- 상품이 없는 주문은 결제 불가
- `배송완료`/`주문취소` 상태는 종결 상태로 더 이상 전이 불가
- `주문생성` 상태가 아니면 상품 추가/제거 불가

## 4. 시나리오 검증 (`tests/test_order_scenario.py`)

pytest 13개 통합 시나리오로 각 계층의 기능을 교차 검증했다. 이와 별개로 계층별
단위 테스트(`test_product.py`, `test_order.py`, `test_order_controller.py`,
`test_order_view.py`)를 TDD(Red→Green) 방식으로 추가해 총 34개 테스트가 통과한다.
TDD 진행 과정과 각 RED 단계에서 확인한 실패 내용은 [`docs/PLAN.md`](docs/PLAN.md)의
"TDD 진행 이력" 절에 정리했다.

| # | 시나리오 | 검증 계층 |
|---|---|---|
| 1 | 주문 생성 후 상품 추가 → 합계 계산 | Model + Controller |
| 2 | 동일 상품 재추가 시 수량 누적 | Model |
| 3 | 상품 제거 | Model |
| 4 | 정상 상태 전이(생성→결제→배송→완료) | Model |
| 5 | 주문 취소 | Model |
| 6 | 완료된 주문은 취소 불가 (종결 상태 보호) | Model |
| 7 | 상품 없는 주문은 결제 불가 | Model |
| 8 | 취소된 주문에는 상품 추가 불가 | Model |
| 9 | 잘못된 상태 전이(생성→배송 건너뛰기) 거부 | Model |
| 10 | 존재하지 않는 주문 조회 시 예외 | Controller |
| 11 | 0 이하 수량 추가 거부 | Model |
| 12 | View가 Controller의 데이터만으로 정상 렌더링 | View |
| 13 | 여러 주문 목록 렌더링 | View + Controller |

### 실행 결과

```
$ python -m pytest tests/ -v
============================= test session starts =============================
collected 13 items

test_주문_생성_및_상품_추가_후_합계_계산 PASSED
test_동일_상품_추가시_수량이_누적된다 PASSED
test_상품_제거 PASSED
test_정상적인_상태_전이_흐름 PASSED
test_주문_취소 PASSED
test_완료된_주문은_취소할_수_없다 PASSED
test_상품이_없는_주문은_결제할_수_없다 PASSED
test_취소된_주문에는_상품을_추가할_수_없다 PASSED
test_잘못된_상태_전이는_거부된다 PASSED
test_존재하지_않는_주문_조회시_예외 PASSED
test_음수_또는_0_수량은_거부된다 PASSED
test_view는_controller가_준_데이터만으로_렌더링한다 PASSED
test_주문_목록_렌더링 PASSED

============================= 13 passed in 0.04s ==============================
```

### 데모 실행 (`main.py`)

```
$ python main.py
[주문번호 ORD-0001] 고객: 홍길동 | 상태: 주문생성
  - 아메리카노 x 2 = 9,000원
  - 카페라떼 x 1 = 5,000원
  합계: 14,000원
[주문번호 ORD-0001] 고객: 홍길동 | 상태: 배송완료
  - 아메리카노 x 2 = 9,000원
  - 카페라떼 x 1 = 5,000원
  합계: 14,000원
[오류] '배송완료' 상태에서 '주문취소' 상태로 전이할 수 없습니다.
```
전이 규칙 위반이 Model에서 `OrderError`로 차단되고, Controller를 거쳐 View가
사용자에게 표시 가능한 오류 메시지로 변환하는 전체 흐름이 정상 동작함을 확인했다.

> Windows 콘솔에서 한글 출력이 깨지면 `PYTHONIOENCODING=utf-8` 환경변수를 설정하고 실행한다
> (콘솔 코드페이지 문제이며 애플리케이션 로직과 무관).

## 5. 결론

- **역할 분리**: Model은 규칙을 스스로 보장하고, Controller는 조율만 하며, View는 표현만 한다는
  원칙이 코드 구조와 테스트로 모두 확인됐다.
- **기능 무결성**: 정상 흐름 5건 + 예외/경계 케이스 8건, 총 13개 시나리오가 모두 통과하여
  주문 생성부터 배송완료/취소까지 전체 라이프사이클에 누락된 분기가 없음을 검증했다.
- **확장 지점**: 결제 연동, 재고 차감, 영속화(DB) 등은 Controller 아래에 별도 계층(Service/Repository)을
  추가해 확장 가능하며, 현재 Model/View 인터페이스를 변경할 필요가 없다.

이 PoC는 MVC 스켈레톤이 실제 도메인 시나리오에서 "구조만 있고 동작하지 않는" 상태가 아니라
end-to-end로 검증된 상태임을 보여준다.
