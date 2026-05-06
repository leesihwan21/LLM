from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# 1. 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. 페이지 설정
st.title("💬 나만의 챗봇")

# 3. 세션 상태 초기화 (핵심!)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 기존 대화 출력
for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    else:
        with st.chat_message("assistant"):
            st.write(message.content)

# 5. 사용자 입력
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    # 사용자 메시지 세션에 저장
    st.session_state.messages.append(HumanMessage(content=user_input))

    with st.chat_message("user"):
        st.write(user_input)

    # LLM 응답 생성 (전체 대화 히스토리 전달 → 이름 기억!)
    response = llm.invoke(st.session_state.messages)

    # AI 메시지 세션에 저장
    st.session_state.messages.append(AIMessage(content=response.content))

    with st.chat_message("assistant"):
        st.write(response.content)