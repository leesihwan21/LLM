from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from dotenv import load_dotenv

load_dotenv()

# 1. 검색 툴 설정
search = DuckDuckGoSearchRun()

# 2. 모델에 검색 툴 바인딩
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools([search])

# 3. 검색 후 답변하는 함수
def search_and_answer(question: str):
    messages = [HumanMessage(content=question)]
    
    # LLM이 검색 필요 여부 판단
    response = llm_with_tools.invoke(messages)
    messages.append(response)
    
    # 툴 호출이 있으면 검색 실행
    if response.tool_calls:
        for tool_call in response.tool_calls:
            search_result = search.invoke(tool_call["args"]["query"])
            messages.append(
                ToolMessage(
                    content=search_result,
                    tool_call_id=tool_call["id"]
                )
            )
        # 검색 결과 바탕으로 최종 답변
        final_response = llm.invoke(messages)
        return final_response.content
    
    return response.content

# 4. 챗봇 실행
print("=" * 50)
print("🌐 인터넷 검색 AI 챗봇")
print("=" * 50)

while True:
    question = input("\n질문: ")
    if question.lower() == "exit":
        print("챗봇 종료!")
        break
    
    print("\n🔍 인터넷 검색 중...")
    answer = search_and_answer(question)
    print(f"\n💬 답변:\n{answer}")
    print("-" * 50)