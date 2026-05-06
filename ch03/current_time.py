from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 1. 현재 시간 Tool 정의
@tool
def get_current_time() -> str:
    """현재 날짜와 시간을 반환합니다."""
    now = datetime.now()
    return now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")

# 2. 모델에 Tool 바인딩
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools([get_current_time])

# 3. 질문 전송
response = llm_with_tools.invoke("현재 시간은?")

# 4. Tool 호출 실행
if response.tool_calls:
    tool_result = get_current_time.invoke(response.tool_calls[0]["args"])
    
    # 5. 결과를 다시 LLM에 전달해서 자연스러운 답변 생성
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    messages = [
        HumanMessage(content="현재 시간은?"),
        response,
        ToolMessage(content=tool_result, tool_call_id=response.tool_calls[0]["id"])
    ]
    final_response = llm.invoke(messages)
    
    print("\n" + "=" * 40)
    print("🕐 AI 응답:")
    print(final_response.content)
    print("=" * 40)
else:
    print(response.content)