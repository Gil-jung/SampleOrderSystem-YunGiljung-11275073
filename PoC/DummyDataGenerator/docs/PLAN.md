# Dummy Data Generator — 구현 계획서 (PLAN)

본 문서는 `PoC.md`에서 정의한 각 단계를 실제로 구현하기 위한 세부 계획을 정리한다.

---

## Step 1. Dummy 데이터 생성 Tool (기본 기능 구현)

### 1-1. 프로젝트 구조 (안)
```
DummyDataGenerator/
├── dummygen/
│   ├── __init__.py
│   ├── cli.py            # CLI 진입점 (argparse)
│   ├── schema.py          # 스키마 로딩/검증
│   ├── generator.py       # 필드 타입별 값 생성 로직
│   ├── writer.py          # JSON 파일 출력
│   └── types/
│       ├── string_gen.py
│       ├── number_gen.py
│       ├── date_gen.py
│       ├── boolean_gen.py
│       ├── enum_gen.py
│       └── composite_gen.py  # 배열/객체 타입
├── schemas/
│   └── order-schema.json
├── tests/
│   └── ...
└── docs/
    └── PLAN.md
```

### 1-2. 스키마 정의 포맷
- JSON Schema를 기반으로 하되, 값 생성에 필요한 확장 속성(`x-generator`)을 추가한다.

```json
{
  "type": "object",
  "properties": {
    "orderId": { "type": "string", "x-generator": { "pattern": "ORD-{seq:04d}" } },
    "customerName": { "type": "string", "x-generator": { "faker": "name" } },
    "quantity": { "type": "integer", "x-generator": { "min": 1, "max": 10 } },
    "status": { "type": "string", "enum": ["PAID", "CANCELLED", "PENDING"] }
  },
  "required": ["orderId", "customerName", "quantity"]
}
```

### 1-3. CLI 명령 설계
| 명령 | 설명 |
|---|---|
| `dummy-gen generate --schema <file> --count <N> --output <file>` | 스키마 기반으로 N건의 Dummy 데이터 생성 |
| `dummy-gen validate --schema <file> --data <file>` | 생성된 데이터가 스키마에 부합하는지 검증 |
| `dummy-gen --seed <value>` | 재현 가능한 랜덤 시드 지정(옵션) |

### 1-4. 타입별 생성 로직
- **문자열**: 고정 패턴(`pattern`) 또는 Faker 라이브러리 활용(이름/주소 등)
- **숫자**: `min`/`max` 범위 내 랜덤 정수/실수
- **날짜**: `start`/`end` 범위 내 랜덤 일시, ISO 8601 포맷 출력
- **Boolean**: 고정 확률(`true_ratio`) 기반 랜덤
- **Enum**: `enum` 목록 중 랜덤 선택(가중치 옵션 지원)
- **배열/객체**: 하위 스키마를 재귀적으로 호출하여 생성, 배열은 `minItems`/`maxItems` 범위로 개수 결정

### 1-5. 산출물
- `dummy-gen` CLI 실행 파일(Python 스크립트 또는 패키징된 실행 파일)
- `schemas/` 하위 예제 스키마 파일
- 생성된 JSON 데이터 샘플

### 1-6. 완료 기준
- [ ] 기본 타입(문자열/숫자/날짜/Boolean/Enum) 생성 지원
- [ ] `--count` 옵션으로 N건 생성 가능
- [ ] 결과가 valid JSON 파일로 저장됨
- [ ] 최소 1개 이상의 단위 테스트 통과

---

## Step 2. 주문관리 시스템 시나리오 기반 검증

### 2-1. 시나리오 스키마 설계
- `schemas/order-schema.json`에 주문(Order), 고객(Customer), 결제(Payment), 배송(Shipment) 구조를 정의
- 필드 간 종속 관계(파생 필드)를 표현하기 위한 확장 속성 추가

```json
{
  "properties": {
    "items": { "type": "array", "items": { "$ref": "#/definitions/orderItem" } },
    "payment": {
      "type": "object",
      "properties": {
        "amount": { "type": "number", "x-generator": { "derivedFrom": "items", "formula": "sum(quantity*unitPrice)" } }
      }
    }
  }
}
```

### 2-2. 입력 → 연관 데이터 생성 로직
1. 사용자가 주문 입력값(주문번호, 고객명, 상품목록)을 JSON으로 전달
2. `generator.py`가 입력값을 기준(seed value)으로 삼아 연관 필드를 채움
   - `customer` → 고객 ID/연락처/등급 자동 생성
   - `payment.amount` → `items`의 `quantity * unitPrice` 합산으로 계산(파생 필드)
   - `shipment` → 운송장 번호/배송 상태 자동 생성
3. 완성된 주문 전체 객체를 JSON으로 출력

### 2-3. 정합성 검증 로직 (Validator)
- `validator.py` 모듈 추가
  - 파생 필드 재계산 후 실제 값과 비교(`payment.amount == sum(items)`)
  - 참조 무결성 체크(customerId, orderId 등 유일성 검증)
  - 스키마 대비 필드 누락/타입 불일치 검사

### 2-4. 테스트 케이스
| 구분 | 테스트 내용 |
|---|---|
| 기능 | 주문 입력 → 연관 필드(고객/결제/배송) 정상 생성 확인 |
| 정합성 | `결제금액 = Σ(수량 × 단가)` 일치 여부 |
| 재현성 | 동일 시드로 2회 실행 시 동일 결과 생성 확인 |
| 유일성 | N건 생성 시 `orderId`, `customerId` 중복 없음 확인 |
| 예외처리 | 필수 필드 누락/타입 오류 입력 시 명확한 에러 메시지 반환 |
| 성능 | 1,000건 생성 시 처리 시간 측정 및 기준치(예: 5초 이내) 확인 |

### 2-5. 완료 기준
- [ ] 주문 입력 시 고객/결제/배송 데이터 자동 생성
- [ ] 파생 필드 정합성 100% 통과
- [ ] 재현성/유일성/예외처리 테스트 통과
- [ ] 테스트 결과 보고서 작성 (`docs/scenario-test-report.md` 등)

---

## Step 3. 완전 무결한 Dummy 데이터 생성 Tool 완성

### 3-1. 개선 항목 정리
- Step 2에서 발견된 이슈 목록화 및 수정
- 스키마 확장 속성(`x-generator`) 문서화 및 표준화
- 도메인 무관하게 재사용 가능하도록 `generator.py`의 파생 필드/참조 로직 일반화

### 3-2. 정합성/재현성 보강
- 시드(seed) 전역 적용: `--seed` 옵션으로 전체 랜덤 생성기 초기화
- 파생 필드 계산을 별도 후처리 단계로 분리하여 스키마 종류에 상관없이 동일하게 적용
- 생성 직후 자동 검증(Validator) 실행 → 실패 시 생성 중단 및 원인 로그 출력

### 3-3. 확장성 확보
- 신규 도메인 스키마 추가 시 코드 수정 없이 `schemas/*.json` 파일만 추가하면 되도록 구조화
- 커스텀 생성기(플러그인) 등록 인터페이스 제공 (`register_generator(name, func)`)

### 3-4. 문서화
- `docs/schema-guide.md`: 스키마 작성 방법 및 확장 속성 레퍼런스
- `docs/cli-usage.md`: CLI 명령어 및 옵션 가이드
- README 갱신: 설치/실행 방법, 예제 포함

### 3-5. 완료 기준
- [ ] Step 2에서 식별된 이슈 전건 해결
- [ ] 신규 도메인 스키마(예: 재고관리) 추가 테스트로 확장성 검증
- [ ] 전체 테스트 스위트(단위/통합) 통과
- [ ] 사용자 가이드 문서 완성

---

## 부록. 마일스톤 요약

| 단계 | 핵심 구현 내용 | 완료 산출물 |
|---|---|---|
| 1 | CLI 기본 구조, 타입별 생성기, JSON 출력 | `dummy-gen` v0.1 |
| 2 | 주문관리 시나리오 스키마, 연관 데이터 생성, 정합성 검증 | 시나리오 테스트 결과 보고서 |
| 3 | 정합성/재현성/확장성 보강, 검증 자동화 | `dummy-gen` v1.0 |
| 4 | 문서화 및 최종 검수 | 사용자 가이드, README |
