# 스키마 작성 가이드

`dummy-gen`은 JSON Schema를 기반으로 하되, 값 생성 방식을 지정하기 위한 확장 속성 `x-generator`를 추가로 지원합니다.

## 기본 타입

### string
```json
{ "type": "string" }
```
- `x-generator.pattern`: `{seq:04d}` 형식의 시퀀스 치환 패턴 (예: `"ORD-{seq:04d}"` → `ORD-0000`, `ORD-0001`, ...)
- `x-generator.choices`: 후보 문자열 목록 중 랜덤 선택 (예: `["홍길동", "김철수"]`)
- 옵션 미지정 시 8자리 랜덤 영숫자 문자열 생성

### integer / number
```json
{ "type": "integer", "x-generator": { "min": 1, "max": 10 } }
```
- `x-generator.min`, `x-generator.max`: 값 범위 (기본값 0~1000)
- `type: "integer"`는 정수, `type: "number"`는 실수로 생성됩니다.

### boolean
```json
{ "type": "boolean", "x-generator": { "true_ratio": 0.3 } }
```
- `x-generator.true_ratio`: `true`가 나올 확률 (기본값 0.5)

### enum
```json
{ "type": "string", "enum": ["PAID", "CANCELLED", "PENDING"] }
```
- `x-generator.weights`: `enum` 목록과 같은 길이의 가중치 리스트 (예: `[3, 1, 1]`)

### string + format: date-time
```json
{
  "type": "string",
  "format": "date-time",
  "x-generator": { "start": "2026-01-01T00:00:00", "end": "2026-12-31T23:59:59" }
}
```
- ISO 8601 형식의 날짜/시간 문자열 생성
- `start`/`end` 미지정 시 기본 범위(2020-01-01 ~ 2029-12-31) 사용

### object / array
```json
{
  "type": "object",
  "properties": { "name": { "type": "string" } }
}
```
```json
{
  "type": "array",
  "items": { "type": "integer" },
  "x-generator": { "minItems": 1, "maxItems": 3 }
}
```
- `object`는 `properties`를 재귀적으로 생성
- `array`는 `items` 스키마를 반복 생성하며, 개수는 `minItems`~`maxItems` 범위에서 랜덤 결정 (기본값 1~3)

## 파생 필드 (Derived Field)

다른 필드(주로 형제/상위 배열)로부터 값을 계산해야 하는 경우 `derivedFrom`과 `formula`를 사용합니다.

```json
{
  "payment": {
    "type": "object",
    "properties": {
      "amount": {
        "type": "integer",
        "x-generator": { "derivedFrom": "items", "formula": "sum(quantity*unitPrice)" }
      }
    }
  }
}
```

- `derivedFrom`: 레코드 최상위(root)에 있는 배열 필드명
- `formula`: 현재 `sum(필드A*필드B)` 형식만 지원 — 배열의 각 원소에서 `필드A * 필드B`를 계산한 뒤 합산
- 계산은 값 생성이 모두 끝난 뒤 후처리로 적용되어, 다른 필드 값에 영향받지 않고 항상 정확한 합계를 가집니다.

## 필수 필드 / 검증

```json
{
  "type": "object",
  "required": ["orderId", "customer"],
  "properties": { ... }
}
```
- `required` 목록은 `dummy-gen validate` 명령 또는 `generate --validate` 옵션에서 누락 여부를 검사하는 데 사용됩니다.

## 커스텀 생성기 (플러그인)

내장 타입으로 표현하기 어려운 값은 Python 코드에서 커스텀 생성 함수를 등록해 사용할 수 있습니다.

```python
from dummygen.generator import register_generator

def generate_business_number(field_schema, rng, seq):
    return f"{rng.randint(100,999)}-{rng.randint(10,99)}-{rng.randint(10000,99999)}"

register_generator("business_number", generate_business_number)
```

```json
{ "type": "string", "x-generator": { "custom": "business_number" } }
```

등록되지 않은 `custom` 이름을 참조하면 `ValueError`가 발생합니다.

## 예제

전체 예제는 [`schemas/order-schema.json`](../schemas/order-schema.json)에서 확인할 수 있습니다 (주문관리 시스템 시나리오).
