import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# 1. 문서 로드 및 리트리버 설정 (기존과 동일)
loader = TextLoader("./my_project.txt", encoding="utf-8")
docs = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=20)
split_docs = text_splitter.split_documents(docs)
vectorstore = FAISS.from_documents(split_docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 2. 대화 기록을 포함한 프롬프트 설정
# MessagesPlaceholder가 대화 기록이 들어갈 자리를 만들어줍니다.
prompt = ChatPromptTemplate.from_messages([
    ("system", "아래 문맥만을 사용하여 질문에 답변하세요:\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
])

model = ChatOpenAI(model="gpt-4o-mini")

# 3. RAG 체인 구성
# 수정 후
chain = (
    {
        # x["question"]만 추출해서 리트리버에게 전달합니다.
        "context": (lambda x: x["question"]) | retriever, 
        "question": lambda x: x["question"],
        "chat_history": lambda x: x["history"]
    }
    | prompt
    | model
    | StrOutputParser()
)

# 4. 연속 대화 실행
chat_history = [] # 대화 기록을 담을 리스트

while True:
    user_input = input("질문 (종료하려면 'exit' 입력): ")
    if user_input.lower() == 'exit':
        break

    # 질문 던지기 (기록과 함께)
    # 실행부 키 이름 통일
    response = chain.invoke({
    "question": user_input,
    "history": chat_history  # 키 이름을 'history'로 통일 (위 lambda x: x["history"]와 매칭)
})

    print(f"\nAI: {response}\n")

    # 대화 기록 업데이트 (사람 질문과 AI 답변을 저장)
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response))