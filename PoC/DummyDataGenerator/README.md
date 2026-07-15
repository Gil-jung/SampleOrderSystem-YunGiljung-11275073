# Dummy Data Generator

테스트를 위한 Dummy(가짜) 데이터를 JSON 파일로 생성하는 콘솔 도구입니다.

- 프로젝트 배경 및 단계별 계획: [PoC.md](PoC.md), [docs/PLAN.md](docs/PLAN.md)
- 스키마 작성 방법: [docs/schema-guide.md](docs/schema-guide.md)
- CLI 사용법: [docs/cli-usage.md](docs/cli-usage.md)

## 빠른 시작

```bash
# 테스트 실행
pytest

# 주문관리 시나리오 예제로 10건 생성 (재현 가능한 시드 지정)
python -m dummygen.cli generate \
  --schema schemas/order-schema.json \
  --count 10 \
  --output orders.json \
  --seed 42 \
  --validate
```

생성된 `orders.json`은 주문(Order) 정보와 함께 고객(Customer), 결제(Payment), 배송(Shipment) 등
연관 데이터를 함께 포함합니다. `payment.amount`는 `items`의 수량×단가 합계로 자동 계산되어
항상 정합성이 보장됩니다.

## 구성

```
dummygen/
├── cli.py         # CLI 진입점 (generate, validate 명령)
├── schema.py      # 스키마 로딩
├── generator.py   # 타입별 값 생성 + 파생 필드 계산 + 커스텀 생성기 플러그인
├── validator.py   # 정합성 / 유일성 / 필수 필드·타입 검증
└── writer.py      # JSON 파일 출력

schemas/
└── order-schema.json   # 주문관리 시스템 예제 스키마

tests/                   # pytest 기반 단위/시나리오 테스트
```

## 개발

전체 기능은 TDD(Red-Green) 방식으로 구현되었으며, 각 기능 단위마다 테스트가 존재합니다.

```bash
pytest -q
```
