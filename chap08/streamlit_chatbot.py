import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

# --- 페이지 설정 ---
st.set_page_config(page_title="ITS-Guard AI Assistant", page_icon="🛣️")
st.title("🛣️ ITS-Guard 전문 상담 챗봇")
st.markdown("성용님의 도로 인프라 AI 프로젝트 가이드입니다.")

# --- 1. RAG 엔진 설정 (최초 1회만 실행되도록 캐싱) ---
@st.cache_resource
def init_rag_engine():
    loader = TextLoader("./my_project.txt", encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    split_docs = text_splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(split_docs, OpenAIEmbeddings())
    return vectorstore.as_retriever()

retriever = init_rag_engine()

# --- 2. 대화 기록 저장소 설정 (Streamlit 전용) ---
# 브라우저 세션이 유지되는 동안 기록을 유지합니다.
msgs = StreamlitChatMessageHistory(key="chat_messages")

# --- 3. 랭체인 체인 구성 ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 도로 인프라 및 AI 전문가야. 맥락을 바탕으로 친절하게 답변해줘.\n\n맥락: {context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

rag_chain = (
    {
        "context": (lambda x: x["question"]) | retriever,
        "question": lambda x: x["question"],
        "history": lambda x: x["history"]
    }
    | prompt
    | model
    | StrOutputParser()
)

chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# --- 4. 화면에 대화 내용 표시 ---
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# --- 5. 사용자 입력 및 답변 처리 ---
if prompt_input := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 화면 출력 및 저장
    st.chat_message("human").write(prompt_input)

    # AI 답변 생성
    with st.spinner("생각 중..."):
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"question": prompt_input}, config)
        
    # AI 메시지 화면 출력 및 저장
    st.chat_message("ai").write(response)