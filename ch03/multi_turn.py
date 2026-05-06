from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

# 1. 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. 대화 히스토리 (랭체인 메모리 역할)
chat_history = []

print("=" * 40)
print("💬 랭체인 챗봇 (종료: exit)")
print("=" * 40)

while True:
    user_input = input("\n나: ")
    
    if user_input.lower() == "exit":
        print("챗봇 종료!")
        break
    
    # 3. 히스토리에 사용자 메시지 추가
    chat_history.append(HumanMessage(content=user_input))
    
    # 4. 전체 히스토리를 LLM에 전달 (이름 기억 핵심!)
    response = llm.invoke(chat_history)
    
    # 5. 히스토리에 AI 응답 추가
    chat_history.append(AIMessage(content=response.content))
    
    print(f"\nAI: {response.content}")