# CLI 사용 가이드

## 설치 / 실행

```bash
# 가상환경 활성화 후
pip install -e .

# 또는 설치 없이 모듈로 직접 실행
python -m dummygen.cli <command> ...
```

## `generate` — 스키마 기반 Dummy 데이터 생성

```bash
dummy-gen generate --schema <스키마파일> --count <생성건수> --output <출력파일> [--seed <시드값>] [--validate]
```

| 옵션 | 필수 | 설명 |
|---|---|---|
| `--schema` | O | 스키마 JSON 파일 경로 |
| `--count` | X (기본 1) | 생성할 레코드 개수 |
| `--output` | O | 생성 결과를 저장할 JSON 파일 경로 |
| `--seed` | X | 랜덤 시드. 지정 시 동일 입력에 대해 항상 동일한 결과 재현 |
| `--validate` | X | 생성 직후 스키마/정합성 검증을 수행하고, 오류 발견 시 파일을 쓰지 않고 종료(exit code 1) |

### 예제

```bash
python -m dummygen.cli generate \
  --schema schemas/order-schema.json \
  --count 100 \
  --output orders.json \
  --seed 42 \
  --validate
```

## `validate` — 생성된 JSON 데이터 검증

이미 생성된 데이터 파일을 스키마와 대조하여 검증합니다.

```bash
dummy-gen validate --schema <스키마파일> --data <검증할데이터파일>
```

| 옵션 | 필수 | 설명 |
|---|---|---|
| `--schema` | O | 스키마 JSON 파일 경로 |
| `--data` | O | 검증할 JSON 데이터 파일 경로 (레코드 배열) |

검증 항목:
- **필수 필드 누락 / 타입 불일치** (`validate_schema`)
- **파생 필드 정합성** — 예: `payment.amount`가 `items`의 합계와 일치하는지 (`validate_consistency`)

오류가 있으면 각 항목을 `stderr`에 출력하고 exit code 1을 반환합니다. 문제가 없으면 exit code 0을 반환합니다.

## 종료 코드

| 코드 | 의미 |
|---|---|
| 0 | 정상 완료 |
| 1 | 스키마 로드 실패, 검증 실패 등 실행 중 오류 |
| 2 | 잘못된 CLI 인자 |
