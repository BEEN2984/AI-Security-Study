import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient


async def main():
    while True:
        inp = input("검색을 사용하시겠어요? (y/n): ")
        
        if inp.lower() == "y":
            use_rag = True
            break
        elif inp.lower() == "n":
            use_rag = False
            break
        else:
            print("잘못된 입력입니다.")
    
    inp = input("질문을 주세요: ")

    load_dotenv()
    client = MCPClient.from_config_file("mcp_config.json")
    llm = ChatOpenAI(model="gpt-4o")

    if use_rag:
        rag_agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=30
        )

        rag_result = await rag_agent.run(
            "당신은 DuckDuckGo 검색 전문가입니다.\n"
            "아래 사용자 요청을 읽고 사용자 요청을 처리하는데 필요한 문서를 찾으려면 어떤 쿼리가 필요한지 생각한 뒤,\n"
            "그 쿼리를 바탕으로 검색해 **상위 문서 5개의 내용을 읽고 요약해 반환해주세요.**\n"
            f"질문: {inp}",
            max_steps=30,
        )
        print(f"\n검색 결과: {rag_result}")

        prompt = (
            "다음은 검색을 통해 얻어낸 상위 5개 결과입니다:\n"
            f"{rag_result}\n"
            "--------------------------------\n"
            "위 검색 결과를 사용해 다음 질문에 답하세요.\n"
            f"질문: {inp}"
        )

    else:
        prompt = (
            "다음 질문에 답하세요.\n"
            f"질문: {inp}"
        )

    answer_agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=30,
        disallowed_tools=["search"],
    )

    answer = await answer_agent.run(
        prompt,
        max_steps=30,
    )

    print(f"\n결과: {answer}") 

if __name__ == "__main__":
    asyncio.run(main())