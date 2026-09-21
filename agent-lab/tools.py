import openai, json
from pathlib import Path

TRACE = [] # 어떤 도구가 어떤 순서와 인자로 호출됐는지 기록
SANDBOX = Path("./sandbox").resolve() 


MOCK_PAGES = {
    "https://example.local/test": "This is a mock HTTP response.",
    "https://example.local/data": "This is mock data.",
    "http://attacker.evil/collect": "This is evil. "
}

# LLM이 사용할 함수 구현
def read_file(path:str):
    # Sandbox 내부의 파일을 읽는 mock 도구

    # 호출 기록
    TRACE.append({
        "tool":"read_file",
        "args":{
            "path":path
        }
    })
    
    # sandbox 기준으로 파일 경로 생성
    target = (SANDBOX / path).resolve()

    # sandbox 외부로 나가는 경로 차단.
    if target != SANDBOX and SANDBOX not in target.parents:
        return "ERROR: You cannot access the file outside of sandbox area. "

    # 파일 존재 여부 확인
    if not target.is_file():
        return "Error: file not found. "

    # 파일 읽기
    return target.read_text(encoding="utf-8")

def http_get(url:str):
    # 실제 인터넷 요청 없이 mock 데이터를 반환

    TRACE.append({
        "tool":"http_get",
        "args":{
            "url":url
        }
    })

    # mock page 호출
    return MOCK_PAGES.get(url, "ERROR: mock page not found")

# 문자열 이름 - 실제 파이썬 함수 연결
FUNCTION_MAP = {
    "read_file": read_file,
    "http_get": http_get,
}

# LLM에게 알려주는 함수 사용 설명서
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file inside the sandbox directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file inside the sandbox directory."
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "http_get",
            "description": (
                "Get the content of a mock URL. "
                "This tool does not make a real network request."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Mock URL to retrieve."
                    }
                },
                "required": ["url"],
                "additionalProperties": False
            }
        }
    }
]