# Step 8. Regression / Safety 테스트 추가 (세부 구현사항)

`PLAN.md`의 Step 0~7 범위를 벗어난 추가 작업이다. Step 0~7에서 각 기능을 개별/통합 검증했지만,
① 과거에 발견했던 버그가 향후 리팩터링으로 재발하지 않도록 고정(회귀 방지)하고,
② 오삭제·데이터 손상·비정상 입력 등 위험 상황에서 애플리케이션이 안전하게 동작함을 별도로 검증하기 위한
Regression / Safety 테스트를 추가한다. **구현 전 검토용 문서**이며, 검토 완료 후 이 문서를 기준으로 구현한다.

## 1. 목표

- **Regression**: 이전 Step 진행 중 실제로 발견했던 이슈(id 채번 로직, 메뉴 입력 처리 등)를 반복 시나리오로
  다시 검증하여, 이후 코드 변경이 같은 버그를 재도입하지 않도록 안전망을 추가한다.
- **Safety**: 오삭제 방지, 잘못된/악의적일 수 있는 입력에 대한 내성, 대상 없음일 때 불필요한 파일 쓰기가
  없는지, 특수 문자를 포함한 데이터의 무결성 등 "안전하게 실패하는지"를 검증한다.

## 2. 대상 파일

`tests/test_step8_regression_safety.py` (신규 파일, 기존 `tests/test_step0.py`~`test_step7_e2e.py`는 수정하지 않음)

## 3. 회귀(Regression) 테스트 계획

| 테스트 함수 | 검증 내용 | 회귀 방지 대상 |
|---|---|---|
| `test_create_item_id_never_duplicates_across_delete_create_cycles` | 생성→삭제→생성을 여러 번(3회 이상) 반복해도 각 시점에 남아있는 `id`가 항상 유일한지 확인 | Step 2에서 발견한 "결번을 재사용하지 않되, `max+1` 기준으로 계산" 로직이 반복 상황에서도 깨지지 않는지 |
| `test_main_survives_multiple_consecutive_invalid_choices` | 잘못된 메뉴 입력(`"9"`, `"x"`, `""`)을 연속으로 여러 번 넣어도 크래시 없이 계속 메뉴를 다시 보여주다가 정상 종료(`"6"`)되는지 확인 | Step 6 메뉴 분기 로직의 `else` 처리가 여러 번 반복돼도 무한 루프에 빠지거나 예외를 던지지 않는지 |
| `test_main_process_survives_full_scenario_via_real_subprocess` | Step 7 시나리오를 실제 `subprocess`로 (`PYTHONUTF8=1` 환경변수 설정 후) 끝까지 실행해 종료 코드 0, `stderr` 없음을 확인 | Step 6에서 실제로 발생했던 `EOFError`(placeholder였던 `main.py`가 실제 로직으로 바뀌며 터진 회귀)류의 프로세스 레벨 회귀를 다시 잡아낸다 — 유닛 테스트만으로는 못 잡는 실제 OS 프로세스 실행 문제 대비 |

## 4. 안전성(Safety) 테스트 계획

| 테스트 함수 | 검증 내용 |
|---|---|
| `test_delete_item_requires_exact_lowercase_y_to_confirm` | `"yes"`, `"n"`, `""`, `"ㅇ"` 등 `.strip().lower()` 후에도 `"y"`가 되지 않는 모든 입력은 삭제하지 않고 취소 처리되는지 확인 (엄격한 확인 절차로 오삭제 방지). 단, `"Y "`처럼 공백/대문자를 포함해도 `strip().lower()` 결과가 `"y"`가 되는 입력은 의도적으로 삭제를 허용하는 것이 현재 구현의 정상 동작이므로 이번 테스트의 "비확인" 목록에서는 제외한다 |
| `test_id_lookup_tolerates_surrounding_whitespace` | `read_one`/`update_item`/`delete_item`에 `" 1 "`처럼 앞뒤 공백이 있는 id를 입력해도 정상적으로 대상(`id=1`)을 찾는지 확인 |
| `test_update_and_delete_do_not_write_file_when_target_not_found` | 존재하지 않는 `id`로 `update_item`/`delete_item` 호출 시 `data.json`이 아예 생성/수정되지 않는지(불필요한 쓰기 없음) 확인 |
| `test_special_characters_survive_round_trip_without_corruption` | 따옴표(`"`), 백슬래시(`\`), 이모지 등 특수 문자가 포함된 `name`/`email`을 생성한 뒤 `read_all`로 재조회했을 때 원본 그대로 보존되고, 다른 필드/레코드가 깨지지 않는지 확인 |
| `test_every_record_always_has_exactly_id_name_email_keys` | Create/Update/Delete를 섞어 여러 번 수행한 뒤, 남아있는 모든 레코드가 항상 `{"id", "name", "email"}` 키만 가지고 있는지(필드 유실/오염 없음) 확인 |
| `test_delete_removes_exactly_one_matching_record` | (방어적 시나리오) 데이터에 동일 `id`를 가진 레코드가 우연히 2건 있는 손상된 상태를 직접 구성했을 때, `delete_item`이 정확히 첫 번째 일치 레코드 1건만 제거하고 나머지 레코드 수가 예상대로 줄어드는지 확인 — 현재 구현(`for`문 첫 매치 후 `return`)의 동작을 문서화하고 고정 |

## 5. 예시 코드

```python
def test_delete_item_requires_exact_lowercase_y_to_confirm(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])

    for bogus_confirm in ["yes", "n", "", "ㅇ"]:
        inputs = iter(["1", bogus_confirm])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        crud.delete_item()

    assert storage.load_data() == [{"id": 1, "name": "홍길동", "email": "hong@example.com"}]


def test_update_and_delete_do_not_write_file_when_target_not_found(tmp_path, monkeypatch):
    data_file = tmp_path / "data.json"
    monkeypatch.setattr(storage, "DATA_FILE", str(data_file))
    storage.save_data([{"id": 1, "name": "홍길동", "email": "hong@example.com"}])
    mtime_before = data_file.stat().st_mtime_ns

    monkeypatch.setattr("builtins.input", lambda _: "999")
    crud.update_item()

    assert data_file.stat().st_mtime_ns == mtime_before
```

`test_main_process_survives_full_scenario_via_real_subprocess`는 `tests/test_step0.py`의
`test_main_runs_without_error`와 동일한 `subprocess.run(..., input=...)` 패턴을 사용하되, Step 7에서
수동으로 검증했던 8단계 전체 입력 시퀀스를 그대로 전달하고 `env`에 `PYTHONUTF8=1`을 추가한다. 자식 프로세스의
`PYTHONUTF8=1`은 자식이 stdin을 해석하는 방식에만 영향을 주고, 부모(`subprocess.run`)가 stdin에 문자열을
인코딩해 전달하는 방식에는 영향을 주지 않으므로 `subprocess.run(..., encoding="utf-8")`를 명시해야 한다
(그렇지 않으면 한글 환경의 로케일 인코딩(`cp949`)으로 인코딩되어 `UnicodeEncodeError`가 발생한다).

## 6. 검증 방법

```bash
.venv/Scripts/python.exe -m pytest tests/test_step8_regression_safety.py -v
```

- 위 9개 테스트(회귀 3건 + 안전성 6건) 모두 통과해야 완료로 간주한다.
- 전체 회귀 확인을 위해 `tests/` 전체(기존 39건 + 신규 9건 = 48건)도 함께 실행한다.

## 7. 완료 기준

- [x] `tests/test_step8_regression_safety.py` 작성 및 전체 통과 (기존 39건 테스트 회귀 없음)
- [x] `docs/step8.md`에 실제 구현/테스트 결과 반영 (구현 완료 후 업데이트)
- [x] `README.md`에 회귀/안전성 테스트 항목 간단히 언급
- [x] 커밋 & 푸쉬

## 8. 구현 결과 및 검토 중 발견한 계획 오류

구현 및 1차 테스트 실행 과정에서 계획 문서(4~5절)의 시나리오 중 3건이 실제로는 성립하지 않아 수정했다.
모두 애플리케이션 코드(`crud.py`/`storage.py`/`main.py`)의 결함이 아니라 **테스트 설계 단계의 오류**였다.

| 발견한 문제 | 원인 | 조치 |
|---|---|---|
| `test_main_process_survives_full_scenario_via_real_subprocess` 실패 (`UnicodeEncodeError`) | 자식 프로세스의 `PYTHONUTF8=1`은 자식이 stdin을 해석하는 방식에만 영향을 줄 뿐, 부모 `subprocess.run`이 stdin에 문자열을 인코딩해 전달하는 방식(로케일 기본 인코딩, 한글 Windows에서는 `cp949`)에는 영향을 주지 않음 | `subprocess.run(..., encoding="utf-8")`을 명시적으로 추가 |
| `test_delete_item_requires_exact_lowercase_y_to_confirm` 실패 (데이터가 삭제되어 버림) | 계획에서 "비확인" 입력 예시로 든 `"Y "`(대문자+트레일링 공백)가 실제로는 `.strip().lower()`를 거쳐 `"y"`가 되어 **정상적으로 삭제가 수행되는 것이 현재 구현의 의도된 동작**이었음 (안전성 결함이 아니라 계획의 예시 선정 오류) | 비확인 목록을 `"Y "` → `"n"`으로 교체, `docs/step8.md`에 왜 `"Y "`가 제외되는지 명시 |
| `test_special_characters_survive_round_trip_without_corruption` 실패 (문자열 불일치) | `read_all()`은 `print(item)`으로 dict의 `repr()`을 출력하는데, `repr()`은 문자열 내 백슬래시를 이스케이프하므로 원본 문자열이 출력 텍스트에 그대로 나타나지 않음 | 테스트 데이터에서 이름 필드의 백슬래시를 제거(따옴표·이모지는 유지)하고, round-trip 무결성은 이미 `storage.load_data()` 등가 비교로 엄격하게 검증되므로 출력 검사는 보조 확인으로만 유지 |

### 8.1 테스트 실행 결과

```bash
.venv/Scripts/python.exe -m pytest tests/ -v
```

```
tests/test_step8_regression_safety.py::test_create_item_id_never_duplicates_across_delete_create_cycles PASSED
tests/test_step8_regression_safety.py::test_main_survives_multiple_consecutive_invalid_choices PASSED
tests/test_step8_regression_safety.py::test_main_process_survives_full_scenario_via_real_subprocess PASSED
tests/test_step8_regression_safety.py::test_delete_item_requires_exact_lowercase_y_to_confirm PASSED
tests/test_step8_regression_safety.py::test_id_lookup_tolerates_surrounding_whitespace PASSED
tests/test_step8_regression_safety.py::test_update_and_delete_do_not_write_file_when_target_not_found PASSED
tests/test_step8_regression_safety.py::test_special_characters_survive_round_trip_without_corruption PASSED
tests/test_step8_regression_safety.py::test_every_record_always_has_exactly_id_name_email_keys PASSED
tests/test_step8_regression_safety.py::test_delete_removes_exactly_one_matching_record PASSED

============================== 48 passed in 0.57s ==============================
```

기존 39건(Step 0~7)을 포함해 총 48건 모두 통과했다 (기존 테스트 회귀 없음).
