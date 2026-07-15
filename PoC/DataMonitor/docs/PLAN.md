# 구현 계획 (PLAN)

> 본 문서는 [PoC.md](../PoC.md)에서 정의한 데이터 모니터링 Tool을 실제로 구현하기 위한
> Step 별 세부 작업 계획을 정리한다.

## Step 0. 프로젝트 구조 준비

```
DataMonitor/
├── docs/
│   └── PLAN.md
├── src/
│   ├── store.py            # 인메모리 저장소 + Monitorable 인터페이스
│   ├── order_simulator.py  # 주문관리 시나리오 이벤트 생성기
│   └── monitor.py          # 데이터 모니터링 Tool (콘솔)
├── tests/
│   ├── test_store.py
│   ├── test_monitor.py
│   └── test_scenarios.py
├── PoC.md
└── .gitignore
```

- [ ] `src/`, `tests/` 디렉터리 생성
- [ ] `pytest.ini` 또는 `pyproject.toml`에 테스트 경로 설정

---

## Step 1. In-Memory Store 구현 (`src/store.py`)

**목표**: 주문 데이터를 보관하고 `Monitorable` 인터페이스(`snapshot()`)를 제공하는 저장소 구현.

세부 작업:
- [ ] `Order` 데이터 구조 정의 (dataclass): `order_id`, `customer`, `items`, `amount`, `status`, `created_at`, `updated_at`
- [ ] `OrderStore` 클래스 구현
  - `create(order: Order) -> None`
  - `update_status(order_id: str, status: str) -> None`
  - `cancel(order_id: str, reason: str) -> None`
  - `snapshot() -> list[dict]`: 내부 dict를 얕은 복사하여 반환 (원본 변경과 무관하게 안전)
- [ ] 동시 접근 대비: `threading.Lock`으로 최소 임계구역만 보호 (조회 성능 저하 방지 위해 스냅샷 생성 시점만 락)
- [ ] 단위 테스트(`tests/test_store.py`): 생성/상태변경/취소/스냅샷 무결성 검증

**완료 기준**: 저장소 CRUD가 예외 없이 동작하고 `snapshot()`이 항상 최신 상태의 복사본을 반환.

---

## Step 2. 주문관리 시나리오 시뮬레이터 (`src/order_simulator.py`)

**목표**: PoC.md의 S1~S8 시나리오를 재현하는 이벤트 생성 스크립트 작성.

세부 작업:
- [ ] 주문 랜덤 생성 함수 (`customer`, `items`, `amount` 랜덤값)
- [ ] 상태 전이 로직: `CREATED → PAID → SHIPPING → DELIVERED`, 일부는 `CANCELLED`로 분기
- [ ] CLI 옵션: `--rate`(초당 생성 건수), `--duration`(총 실행 시간), `--burst`(S4 대량 동시 생성 테스트용)
- [ ] `OrderStore` 인스턴스를 공유하여 `monitor.py`와 동일 프로세스 또는 별도 스레드에서 실행 가능하도록 구성

**완료 기준**: 시뮬레이터 실행 시 시나리오 S1~S4 이벤트를 재현 가능.

---

## Step 3. 데이터 모니터링 Tool (`src/monitor.py`)

**목표**: `Monitorable` 저장소를 polling 방식으로 조회하여 콘솔에 실시간 렌더링.

세부 작업:
- [ ] `render(snapshot: list[dict], prev_snapshot: list[dict]) -> str` — 표 형태 문자열 생성
  - 상단 요약(전체 건수, 상태별 건수)
  - 변경된 레코드(신규/상태변경) 하이라이트 표시
- [ ] 메인 루프: `interval` 초마다 콘솔 clear 후 `render()` 결과 출력
- [ ] CLI 옵션 파싱 (`argparse`): `--interval`, `--filter status=PAID`, `--sort created_at`
- [ ] 예외 처리: 저장소 접근 중 예외 발생 시 크래시 대신 에러 메시지 출력 후 다음 주기 재시도
- [ ] 빈 데이터 상태 처리: "데이터 없음" 메시지 출력 (S7)

**완료 기준**: `monitor.py` 단독 실행 시 `order_simulator.py`가 생성하는 데이터 변경이 지연 없이 반영.

---

## Step 4. 시나리오 기반 검증 (S1~S8)

**목표**: PoC.md 3.2절의 시나리오를 실제로 실행하고 결과를 기록.

세부 작업:
- [ ] `tests/test_scenarios.py`: S1(신규 생성), S2(상태 전이), S3(취소), S6(필터/정렬), S7(빈 상태)을 자동화 테스트로 작성
- [ ] S4(대량 동시 생성), S5(race condition), S8(장시간 실행)은 수동/부하 테스트로 별도 실행
  - S4: `order_simulator.py --burst 1000` 실행 후 `monitor.py` 집계 건수 확인
  - S5: 스냅샷 렌더링 중 저장소에 동시 write 발생시켜 예외 미발생 확인
  - S8: 수 시간 백그라운드 실행 후 메모리/CPU 사용량 모니터링 (`tracemalloc`, 작업관리자 등 활용)
- [ ] 시나리오별 결과를 `docs/VALIDATION_RESULT.md`(추후 작성)에 기록

**완료 기준**: S1~S8 전 항목 통과, 실패 시 원인 분석 후 Step 1~3 수정.

---

## Step 5. 최종 구현 반영 및 마무리

**목표**: 검증 과정에서 발견된 이슈를 반영하여 정식 버전 완성.

세부 작업:
- [ ] 발견된 버그/성능 이슈 수정
- [ ] `README.md` 작성 (설치/실행 방법)
- [ ] `pytest` 전체 테스트 통과 확인
- [ ] PoC.md의 "완료 기준(DoD)" 체크리스트 전체 충족 확인
- [ ] 커밋 및 푸시

**완료 기준**: PoC.md 4.1절 DoD 항목 전부 체크 완료.

---

## 일정 요약

| Step | 내용 | 예상 산출물 |
|---|---|---|
| 0 | 프로젝트 구조 준비 | 디렉터리 스캐폴딩 |
| 1 | In-Memory Store 구현 | `src/store.py`, `tests/test_store.py` |
| 2 | 주문 시나리오 시뮬레이터 | `src/order_simulator.py` |
| 3 | 데이터 모니터링 Tool | `src/monitor.py` |
| 4 | 시나리오 검증 (S1~S8) | `tests/test_scenarios.py`, 검증 결과 문서 |
| 5 | 최종 구현 반영 | 정식 버전 + README |
