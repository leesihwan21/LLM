from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

load_dotenv()

search = DuckDuckGoSearchRun()

# 1. 날씨 검색 Tool
@tool
def search_weather(city: str) -> str:
    """특정 도시의 현재 날씨를 검색합니다."""
    return search.run(f"{city} 날씨 오늘 현재")

# 2. 상태 정의
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 3. 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools([search_weather])

# 4. 챗봇 노드
def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 5. 툴 노드
def tool_node(state: State):
    last_message = state["messages"][-1]
    tool_messages = []
    for tool_call in last_message.tool_calls:
        city = tool_call["args"].get("city", "수원")
        result = search.run(f"{city} 날씨 오늘 현재")
        tool_messages.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )
    return {"messages": tool_messages}

# 6. 조건 분기
def should_use_tool(state: State):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tool_node"
    return END

# 7. 그래프 구성
builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tool_node", tool_node)
builder.set_entry_point("chatbot")
builder.add_conditional_edges("chatbot", should_use_tool)
builder.add_edge("tool_node", "chatbot")
graph = builder.compile()

# 8. 실행
print("=" * 50)
print("🌤️ LangGraph 날씨 챗봇 (종료: exit)")
print("=" * 50)

chat_history = []

while True:
    user_input = input("\n나: ")
    if user_input.lower() == "exit":
        break
    chat_history.append(HumanMessage(content=user_input))
    result = graph.invoke({"messages": chat_history})
    ai_message = result["messages"][-1]
    chat_history.append(ai_message)
    print(f"\nAI: {ai_message.content}")