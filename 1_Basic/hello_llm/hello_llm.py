from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()          # .env의 OPENAI_API_KEY를 환경변수로 올림
client = OpenAI()      # 환경변수의 키를 자동으로 사용

MODEL = "gpt-5.5"

user_input = input("Order: ")

response = client.responses.create(
    model=MODEL,
    input=user_input,   # 문자열을 주면 SDK가 [{"role":"user", ...}]로 감싼다
)

print("LLM:", response)