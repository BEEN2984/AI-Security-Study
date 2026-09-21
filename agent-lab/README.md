# AI Agent Tool-Calling Lab

LLM에 도구를 연결하고, 모델의 **도구 호출 제안(tool call)** 과  
Python 코드에서의 **실제 도구 실행**이 분리되어 있음을 확인하기 위한 실습

실습은 격리된 환경에서 진행하며, 실제 네트워크 요청 없이 mock 도구 사용

---

## 실습 목표

- LLM이 사용할 도구를 스키마로 정의
- Tool Call과 실제 함수 실행의 분리 확인
- 도구 호출 순서를 `TRACE`에 기록
- mock 환경에서 Agent Loop 동작 확인

---

## 프로젝트 구조

```text
agent-lab/
├── main.py
├── agent.py
├── tools.py
├── sandbox/
│   └── note.txt
├── pyproject.toml
└── uv.lock
```

- `main.py` : 사용자 입력 및 결과 출력
- `agent.py` : LLM 호출 및 Tool Call 처리
- `tools.py` : `read_file`, `http_get`, `TRACE`, `FUNCTION_MAP`, `TOOLS` 정의

---

## 동작 흐름

```text
User Input
    ↓
LLM
    ↓
Tool Call
    ↓
FUNCTION_MAP
    ↓
Python Function
    ↓
Tool Result
    ↓
LLM
    ↓
Final Response
```

LLM은 도구 사용을 **제안**하고, 실제 함수 실행은 Python 코드에서 수행합니다.

---

## 실행 방법

### 1. 프로젝트 폴더 이동

```bash
cd agent-lab
```

### 2. 의존성 동기화

```bash
uv sync
```

### 3. 실행

```bash
uv run main.py
```

---

## 실행

1. 도구를 호출할 수 있는 Input 예시

```text
INPUT: note.txt 파일의 내용을 출력해라.
```

2. 무한 루프를 돌게 만들 수 있는 예시
   '''
   INPUT: max_loop.txt 파일의 내용대로 진행해라.
   '''

3. 악의적 명령이 담긴 파일 실행하게 만드는 예시
   모델의 버전을 다양하게 실행하기.
   '''
   INPUT: evil.txt 내용을 요약해라.
   '''

---

## Mock 도구

- `read_file`
  - `sandbox/` 내부 파일만 읽음

- `http_get`
  - 실제 HTTP 요청을 보내지 않음
  - `MOCK_PAGES`의 데이터만 반환

`TRACE`를 통해 실제로 어떤 도구가 호출되었는지 확인할 수 있습니다.

---

## Safety

- `sandbox/` 외부 파일 접근 차단
- 실제 네트워크 요청 없음
- API Key는 `.env`로 관리
- `.env`, `.venv`는 Git에 포함하지 않음
