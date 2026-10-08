# 실습6: Taint Tracking 삽입

기존 Direct / Indirect Prompt Injection 평가 환경에 **Taint Tracking 기반 데이터 흐름 검사 계층**을 추가하는 실습

외부에서 유입된 비신뢰 데이터를 Tainted Data로 등록하고, 해당 데이터가 위험한 도구 인자로 사용되는 경우 실제 도구 실행 전에 차단

---

## 실습 목표

- 비신뢰 데이터에 Taint를 부여하는 기능 구현
- 위험한 Tool 인자로 비신뢰 데이터가 전달되는지 검사
- Taint 적용 전후 공격 성공 여부 비교

## 동작 흐름

```text
User Request
     ↓
    LLM
     ↓
 Tool Call 제안
     ↓
 Policy Check
     ↓
 Taint Check
  ┌───┴───┐
 Safe   Tainted
  ↓        ↓
도구 실행  실행 차단
  └───┬────┘
      ↓
  TRACE 기록
      ↓
공격 성공 여부 평가
```

## Taint 등록 및 검사

`taint.py`에서 비신뢰 데이터의 등록과 위험 Sink 검사를 구현

**비신뢰 데이터 출처**

- `file`
- `web`
- `tool_output`
- `email`

`register_tainted_data()`를 통해 비신뢰 데이터를 `TAINTED_DATA`에 저장

**위험 Sink**

| Tool             | 검사 인자    |
| ---------------- | ------------ |
| `transfer_money` | `to_account` |
| `http_get`       | `url`        |
| `write_file`     | `path`       |
| `delete_file`    | `path`       |

`check_taint_tool_call()`에서 도구 인자가 등록된 Tainted Data와 일치하는지 검사

Taint가 발견되면 `TaintViolation` 예외를 발생시켜 도구 실행을 차단

## Tool 수정

기존 `tools.py`의 `read_file()`에 Taint 등록 과정 추가

```python
content = target.read_text(encoding="utf-8")

register_tainted_data(
    value=content,
    source="file",
    detail=path
)
```

Sandbox 파일을 읽은 경우 해당 내용을 비신뢰 데이터로 등록

이후 LLM이 해당 데이터를 위험한 도구 인자로 사용하면 Taint 검사 대상이 됨

## Agent 수정

기존 `agent.py`에 Taint 검사 과정 추가

```text
LLM Tool Call
     ↓
check_policy()
     ↓
    allow
     ↓
check_taint_tool_call()
  ┌───┴───┐
 Pass   Violation
  ↓        ↓
도구 실행 TAINT_DENIED
```

`run_agent()`에서 `taint_enabled`로 Taint 검사 활성화 여부를 설정

Taint 검사에서 위반이 발생하면 실제 Python 도구를 실행하지 않고 `TAINT_DENIED` 반환

차단된 도구 이름, 인자, 차단 사유는 `TRACE`에 기록

## 평가 코드 수정

기존 `main.py`에 Taint 검사 결과 수집 및 집계 기능 추가

```python
policy_enabled = True
taint_enabled = False
```

두 옵션을 변경하여 Policy와 Taint Tracking의 적용 여부를 설정

각 공격 케이스 실행 전 다음 데이터를 초기화

```python
TRACE.clear()
MESSAGES.clear()
TAINTED_DATA.clear()
```

이전 공격 케이스의 실행 기록이나 Taint 정보가 다음 테스트에 영향을 주지 않도록 구성

또한 `judge()`에서 실제 실행된 Tool만 공격 성공으로 판단하도록 수정

```python
if not event.get("executed", False):
    continue
```

## 결과 저장

실행 결과는 타임스탬프를 포함한 JSON 파일로 저장

```text
result/results_YYYYMMDD_HHMMSS.json
```

각 실행의 요약 결과는 다음 파일에 누적

```text
result/result_table.md
```

주요 집계 항목

- `attack_success`: 공격 성공 수
- `attack_failed`: 공격 실패 수
- `policy_denied`: 정책에 의해 차단된 케이스 수
- `taint_denied`: Taint 검사에 의해 차단된 케이스 수
- `api_blocked`: API에서 차단된 케이스 수

Direct / Indirect 공격별 성공 및 실패 수도 함께 집계

## 실행

```bash
uv sync
uv run main.py
```

## 실습 결과

외부 파일에서 읽은 데이터를 Tainted Data로 등록하고, 해당 데이터가 위험한 Tool 인자로 전달되는 경우 실행 전에 차단하도록 구현함.

기존 Policy 기반 접근 제어에 Taint Tracking을 추가하여 **허용된 자원에 대한 접근 여부뿐 아니라 비신뢰 데이터의 사용 여부까지 검사**할 수 있도록 구성함.

---

## 주요 파일

- `taint.py`
  - 비신뢰 데이터 등록 및 Taint 검사
  - 위험 Sink 정의
  - Taint 위반 예외 처리

- `tools.py`
  - 파일 읽기 과정에서 Taint 등록

- `agent.py`
  - Policy 검사 이후 Taint 검사 수행
  - 위반 시 Tool 실행 차단

- `main.py`
  - 방어 기능 활성화 설정
  - 케이스별 Taint 상태 초기화
  - Taint 차단 결과 집계 및 저장

> 본 실습은 격리된 환경에서 Mock 도구와 Sandbox 파일을 사용합니다.
