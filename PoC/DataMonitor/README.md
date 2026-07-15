# DataMonitor

인메모리에 저장된 데이터 상태를 콘솔에서 실시간으로 조회하는 데이터 모니터링 Tool.
설계 배경과 검증 시나리오는 [PoC.md](PoC.md), 구현 단계는 [docs/PLAN.md](docs/PLAN.md),
시나리오 검증 결과는 [docs/VALIDATION_RESULT.md](docs/VALIDATION_RESULT.md)를 참고한다.

## 설치

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install pytest
```

## 실행

주문관리 시나리오 데이터를 생성한 뒤 모니터링 콘솔을 실시간으로 갱신한다.

```bash
./.venv/Scripts/python.exe src/monitor.py --interval 1.5 --filter status=PAID --sort created_at
```

| 옵션 | 설명 | 기본값 |
|---|---|---|
| `--interval` | polling 주기(초) | `1.5` |
| `--filter` | `필드=값` 형식 필터 (예: `status=PAID`) | 없음 |
| `--sort` | 정렬 기준 필드명 (예: `created_at`) | 없음 |

## 테스트

```bash
./.venv/Scripts/python.exe -m pytest tests/ -v
```

## 프로젝트 구조

```
DataMonitor/
├── docs/
│   ├── PLAN.md               # 구현 단계별 계획
│   └── VALIDATION_RESULT.md  # S1~S8 시나리오 검증 결과
├── src/
│   ├── store.py              # 인메모리 주문 저장소 (Monitorable)
│   ├── order_simulator.py    # 주문관리 시나리오 이벤트 생성기
│   └── monitor.py            # 데이터 모니터링 Tool (콘솔)
├── tests/
│   ├── test_store.py
│   ├── test_order_simulator.py
│   ├── test_monitor.py
│   └── test_scenarios.py     # S1~S8 통합 시나리오 검증
└── PoC.md
```
