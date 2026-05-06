import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()

# 1. 문서 로드 및 리트리버 설정
loader = TextLoader("./my_project.txt", encoding="utf-8")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(docs)
vectorstore = FAISS.from_documents(split_docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 2. 프롬프트 설정 (역사 기록을 위한 Placeholder 포함)
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 도로 인프라 및 AI 전문가야. 아래 문맥을 바탕으로 전문적으로 답변해줘.\n\n맥락: {context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. RAG 체인 구성 (기존과 동일하되 history를 관리받음)
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

# 4. 세션별로 DB에 대화 기록을 저장하는 함수
def get_session_history(session_id):
    return SQLChatMessageHistory(
        session_id=session_id, 
        connection_string="sqlite:///chat_history.db" # 로컬 DB 파일 생성
    )

# 5. 체인에 히스토리 관리 기능 입히기
# 'history' 변수가 기록을 관리하도록 연결합니다.
chain_with_history = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

# 6. 실행 루프
# 특정 사용자나 세션을 구분하기 위한 ID (실무에서는 사용자 ID를 씁니다)
session_config = {"configurable": {"session_id": "seongyong_user_1"}}

print("--- [DB 연동형 AI 비서 가동] ---")

while True:
    query = input("\n성용님: ")
    if query.lower() in ["exit", "quit", "종료"]:
        break

    # 체인 호출 시 세션 설정을 함께 넘깁니다.
    response = chain_with_history.invoke(
        {"question": query},
        config=session_config
    )

    print(f"AI 전문가: {response}")