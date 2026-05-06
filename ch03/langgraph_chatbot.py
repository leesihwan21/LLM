from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict

load_dotenv()

# 1. 상태 정의 (대화 히스토리 저장)
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 3. 챗봇 노드 정의
def chatbot(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 4. 그래프 구성
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# 5. 챗봇 실행
print("=" * 50)
print("🤖 LangGraph 기본 챗봇 (종료: exit)")
print("=" * 50)

chat_history = []

while True:
    user_input = input("\n나: ")
    if user_input.lower() == "exit":
        print("챗봇 종료!")
        break

    # 히스토리에 추가
    chat_history.append(HumanMessage(content=user_input))

    # 그래프 실행
    result = graph.invoke({"messages": chat_history})

    # AI 응답 추출 및 히스토리 저장
    ai_message = result["messages"][-1]
    chat_history.append(ai_message)

    print(f"\nAI: {ai_message.content}")