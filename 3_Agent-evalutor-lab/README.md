## 파일 설명

# AI Agent Security Evaluator Lab

LLM 기반 Agent에 여러 도구를 연결하고, **Direct / Indirect Prompt Injection 공격 케이스를 자동 실행하여 Agent의 도구 호출을 평가**하기 위한 실습 프로젝트

실습은 격리된 환경에서 진행하며, 실제 네트워크 요청이나 실제 금융 거래 없이 **Mock 도구와 Sandbox 환경**만 사용

---

## 실습 목표

- LLM Agent의 Tool Calling 구조 이해
- LLM의 Tool Call 제안과 실제 Python 함수 실행의 분리 확인
- Agent가 호출한 도구와 인자를 `TRACE`에 기록
- Direct / Indirect Prompt Injection 공격 케이스 구성
- YAML을 이용한 공격 케이스 관리
- `success_if`를 이용한 공격 성공 여부 평가
- Allow List를 이용한 정책 위반 여부 평가
- 여러 공격 케이스를 자동 실행
- 평가 결과를 JSON 파일로 저장

---

- `mock_datas.json`
  - 실습에서 사용하는 Mock 데이터를 저장
  - 실제 네트워크 요청이나 실제 금융 시스템 대신 사용할 가상의 웹 페이지와 계좌 정보를 기록
  - 주요 항목:
    - `pages`: `http_get`에서 사용할 Mock 페이지
    - `accounts`: `transfer_money`에서 사용할 Mock 계좌 정보

- `allow_list.json`
  - Agent가 접근하거나 사용할 수 있는 허용 자원 목록을 정의
  - Evaluator는 `TRACE`에 기록된 Tool Call의 인자를 이 파일과 비교하여 정책 위반 여부를 판단
  - 주요 항목:
    - `allowed_urls`: 접근이 허용된 URL 목록
    - `allowed_files`: 접근이 허용된 파일 목록
    - `allowed_accounts`: 송금이 허용된 계좌 목록

- `attacks/`
  - Direct / Indirect Prompt Injection 공격 케이스를 YAML 형식으로 저장
  - 각 공격 케이스는 공격 유형, payload, 사용자 요청, 성공 조건 등을 포함

---

## Agent 동작 흐름

## 출처

공격 케이스와 공격 시나리오를 구성할 때 다음 논문의 위협 모델 및 공격 사례를 참고했습니다.

**Progent: Securing AI Agents with Privilege Control**
