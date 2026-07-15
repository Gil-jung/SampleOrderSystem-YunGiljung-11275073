# SampleOrderSystem — 반도체 시료 생산주문관리 시스템

가상의 반도체 회사 S-Semi의 시료(Sample) 생산·주문·재고·출고를 관리하는 콘솔 기반
애플리케이션이다. TDD(`tdd` 스킬)를 사용해 Model → Repository → Service →
Controller/View 계층을 단계적으로 구현했다.

- 언어: Python 3.13
- 저장 방식: 인메모리(dict/list) — 별도 DB 없음
- 실행 방식: 콘솔(터미널) 기반 대화형 메뉴

## 배경

배경, 역할별 흐름, 주문 상태 흐름 등 도메인 설명은 [`CLAUDE.md`](CLAUDE.md)를 참고한다.

## 프로젝트 구조

```
SampleOrderSystem/
├── src/
│   ├── main.py                 # 진입점, 메인 메뉴 루프
│   ├── model/
│   │   ├── sample.py            # Sample (값 객체, 수율 검증)
│   │   └── order.py             # Order, OrderStatus, OrderError(상태 전이 검증)
│   ├── repository/
│   │   ├── sample_repository.py # Sample 인메모리 저장소
│   │   └── order_repository.py  # Order 인메모리 저장소
│   ├── service/
│   │   ├── sample_service.py     # 시료 등록/조회/검색
│   │   ├── order_service.py      # 예약/승인(재고 분기)/거절/생산 완료
│   │   ├── production_service.py # 생산 큐(FIFO), 부족분/실생산량/총생산시간 계산
│   │   ├── monitoring_service.py # 상태별 주문 수, 재고 상태(여유/부족/고갈) 판정
│   │   └── release_service.py    # 출고 처리
│   ├── controller/
│   │   └── menu_controller.py    # 메뉴 명령을 Service로 위임, View용 dict 변환
│   └── view/
│       └── console_view.py       # 메뉴/목록 렌더링
├── tests/                        # pytest 테스트 (총 88건)
│   ├── model/, repository/(Service 테스트에 포함), service/, controller/, view/
│   ├── test_main.py               # main.py 서브메뉴 UI 테스트 (subprocess 기반)
│   └── test_e2e_scenarios.py       # 종합 시나리오(E2E) 테스트
├── pytest.ini
├── PRD.md                         # 기능 요구사항 정의
├── PLAN.md                        # Phase/사이클 단위 구현 로드맵
├── docs/                          # 사이클별 RED/GREEN/REVIEW 기록 (0-1.md ~ 10-6.md 등)
├── CLAUDE.md                      # 프로젝트 배경 및 TDD 진행 방식
└── PoC/                           # 본 구현 이전의 개별 기술 검증 PoC 모음
```

## 실행 방법

```bash
# 가상환경 활성화 후
cd src
python main.py
```

메인 메뉴에서 번호를 입력해 기능을 선택한다.

```
=== 반도체 시료 생산주문관리 시스템 ===
등록 시료 수: 0개 | 총 재고: 0개
1. 시료 관리
2. 주문 (접수 / 승인 / 거절)
3. 모니터링
4. 출고 처리
5. 생산 라인
0. 종료
선택:
```

| 번호 | 메뉴 | 하위 기능 |
|---|---|---|
| 1 | 시료 관리 | 등록 / 조회 / 검색 |
| 2 | 주문 | 예약 / 접수된 목록 조회 / 승인 / 거절 |
| 3 | 모니터링 | 주문량 조회 / 재고량 조회 |
| 4 | 출고 처리 | CONFIRMED 목록 조회 / 출고 실행 |
| 5 | 생산 라인 | 생산 현황 조회 / 대기 큐 조회 / 생산 완료 처리 |
| 0 | 종료 | 프로그램 종료 |

> 생산 완료 처리(5번 메뉴)는 원래 시스템 이벤트로 설계했으나, 콘솔 UI만으로는
> 재고를 늘릴 다른 방법이 없어(등록 직후 재고는 항상 0) 메뉴 명령으로 노출했다
> (`docs/10-5c.md` 참고).

## 주문 상태 흐름

```
RESERVED --승인(재고충분)--> CONFIRMED --출고--> RELEASE
RESERVED --승인(재고부족)--> PRODUCING --생산완료--> CONFIRMED --출고--> RELEASE
RESERVED --거절-------------> REJECTED (종결, 모니터링 제외)
```

## 테스트

```bash
python -m pytest -v
```

Model/Repository/Service/Controller/View 각 계층의 단위 테스트, `main.py`의 서브메뉴
UI 테스트(`subprocess`로 입력을 흘려보내고 출력을 검증), 그리고 재고 충분/재고 부족/
거절/FIFO 다중 생산 시나리오를 잇는 E2E 테스트까지 총 88건의 pytest 테스트로 검증한다.

## 문서

- [`PRD.md`](PRD.md) — 메인 메뉴, 데이터 모델, 기능별 상세 요구사항, 계산식
- [`PLAN.md`](PLAN.md) — Phase 0(스캐폴딩)부터 Phase 11(설계 정리)까지 전체 구현 로드맵
- [`docs/`](docs) — 각 TDD 사이클의 RED(실패 테스트 확인) / GREEN(최소 구현) / REVIEW
  (사람 파트너 승인) 기록. 파일명은 `PLAN.md`의 사이클 번호(예: `4-2.md`, `10-5c.md`)와 대응한다.
- [`CLAUDE.md`](CLAUDE.md) — 프로젝트 배경, 역할, 도메인 설명, TDD 진행 방식

## 설계상 알려진 제약

전체 설계 재점검(2026-07-15, `PLAN.md` Phase 11)에서 발견한 항목 중 일부는 아직
정리 전이거나 의도적으로 남겨둔 단순화다.

- 재고 상태 판정("여유"/"부족"/"고갈")은 시료별 `CONFIRMED` 주문 수량 합을 미출고
  수요로 본다 (PRD.md 4.4절).
- 생산 완료 시 재고에 반영되는 양은 실 생산량이 아니라 "부족분"만큼으로 단순화했다
  (수율에 따른 불량 처리는 모델링하지 않음, `docs/5-7.md` 참고).
- 하나의 생산 라인만 운영하며, 하나의 주문은 하나의 시료 종류만 요구하고, 출고는
  주문 단위 전량 처리로 가정한다 (`PRD.md` 7절).
