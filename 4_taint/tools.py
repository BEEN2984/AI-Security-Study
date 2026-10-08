import openai, json
from pathlib import Path
from taint import register_tainted_data

TRACE = [] # 어떤 도구가 어떤 순서와 인자로 호출됐는지 기록
SANDBOX = Path("./sandbox").resolve() 

#-------------------------------------------------
# mock_datas.json 불러오기
# tools.py가 있는 디렉터리
BASE_DIR = Path(__file__).parent

# mock_datas.json 불러오기
with open(BASE_DIR / "json/mock_data.json", "r", encoding="utf-8") as f:
    MOCK_DATA = json.load(f)

MOCK_PAGES = MOCK_DATA["pages"]
MOCK_ACCOUNTS = MOCK_DATA["accounts"]


# ------------------------------------------------
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
    content = target.read_text(encoding="utf-8")

    # 파일 내용을 untrusted source로 등록
    register_tainted_data(value=content, source="file", detail=path)
    return content

def write_file(path: str, content: str):
    # Sandbox 내부의 파일을 수정하는 mock 도구

    # 호출 기록
    TRACE.append({
        "tool": "write_file",
        "args": {
            "path": path,
            "content": content
        }
    })

    # sandbox 기준으로 파일 경로 생성
    target = (SANDBOX / path).resolve()

    # sandbox 외부로 나가는 경로 차단
    if target != SANDBOX and SANDBOX not in target.parents:
        return "ERROR: You cannot access the file outside of sandbox area."

    # 파일 존재 여부 확인
    if not target.is_file():
        return "ERROR: file not found."

    # 파일 덮어쓰기
    target.write_text(content, encoding="utf-8")

    return "OK: file written."

def delete_file(path:str):
    # Sandbox 내부의 파일을 삭제하는 mock 도구

    # 호출 기록
    TRACE.append({
        "tool": "delete_file",
        "args": {
            "path": path,
        }
    })

    # sandbox 기준으로 파일 경로 생성
    target = (SANDBOX / path).resolve()

    # sandbox 외부로 나가는 경로 차단
    if target != SANDBOX and SANDBOX not in target.parents:
        return "ERROR: You cannot access the file outside of sandbox area."

    # 파일 존재 여부 확인
    if not target.is_file():
        return "ERROR: file not found."

    # 파일 삭제
    target.unlink()

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

def transfer_money(to_account: str):
    # mock 계좌 사이에서 가상의 송금을 수행하는 도구

    TRACE.append({
        "tool": "transfer_money",
        "args": {
            "to_account": to_account
        }
    })

    # 입금 계좌 확인
    if to_account not in MOCK_ACCOUNTS:
        return "ERROR: recipient account not found."



    return f"OK:  transferred to ({to_account})."

# ------------------------------------------------
# 문자열 이름 - 실제 파이썬 함수 연결
FUNCTION_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "delete_file":delete_file,
    "http_get": http_get,
    "transfer_money":transfer_money,
}

# ------------------------------------------------
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

    # write_file
        {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes the specified content to a file in the sandbox, overwriting any existing content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file inside the sandbox directory."
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file. Existing content will be overwritten."
                    }
                },
                "required": ["path", "content"],
                "additionalProperties": False
            }
        }
    },

    #delete_file
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes a file inside the sandbox directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path of the file to delete inside the sandbox directory."
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },

    # http_get
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
    },
    
    # transfer_money
    {
        "type": "function",
        "function": {
            "name": "transfer_money",
            "description": "Transfers the specified amount of money from one account to another in the mock banking system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_account": {
                        "type": "string",
                        "description": "Account number to transfer money to."
                    }
                },
                "required": ["to_account"],
                "additionalProperties": False
            }
        }
    },
]