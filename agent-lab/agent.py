import json
from openai import OpenAI
from dotenv import load_dotenv
from tools import FUNCTION_MAP, TOOLS

load_dotenv()          # .env의 OPENAI_API_KEY를 환경변수로 올림

# API ClINET 열기
client = OpenAI()      # 환경변수의 키를 자동으로 사용
MODEL="gpt-5.6"


# 대화 기록
MESSAGES = []

def run_agent(user_input: str) -> str:
    # 사용자 입력 받기 -> LLM 호출 -> 필요한 도구 실행 -> return

    # 사용자 입력을 MESSAGES에 추가
    MESSAGES.append({
        "role":"user",
        "content":user_input
    })

    # 도구 횟수 제한
    max_steps = 10

    for _ in range(max_steps):

        # 1. LLM 호출
        response = client.chat.completions.create(
            model=MODEL,
            messages=MESSAGES,
            tools=TOOLS,
            reasoning_effort="none"
        )
        message = response.choices[0].message # 답변 부분만 꺼내기
        MESSAGES.append(message)

        # 2. tool call이 없으면 return
        if not message.tool_calls:
            return message.content 

        # 3. LLM이 요청한 tools 실행
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name

            try:
                args = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError:
                result = "ERROR: Invalid tool argumemts. "
            else:
                # 4. FUNCTION_MAP에서 실제 python 함수 찾기
                func_to_run = FUNCTION_MAP.get(func_name)

                if func_to_run is None:
                    result = f"ERROR: Unknown tool '{func_name}'"

                else:
                    try:
                        # 5. 실제 도구 실행
                        result = func_to_run(**args)

                    except Exception as e:
                        result = {
                            f"ERROR: {e}"
                        }

            # 6. 도구 실행 결과를 LLM에게 전달
            MESSAGES.append({
                "role":"tool",
                "tool_call_id": tool_call.id,
                "content":str(result)
            })

    return "ERROR: Too many tool calls."