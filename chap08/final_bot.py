import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# 1. 문서 로드 (PDF 혹은 TXT 선택 가능)
file_path = "./my_project.txt"  # PDF가 있다면 "./project.pdf"로 변경 가능
if file_path.endswith(".pdf"):
    loader = PyPDFLoader(file_path)
else:
    loader = TextLoader(file_path, encoding="utf-8")

docs = loader.load()

# 2. 문서 쪼개기 (실무에서 주로 쓰는 Recursive 방식)
# 단락, 문장, 단어 순으로 문맥을 파괴하지 않고 쪼개줍니다.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(docs)

# 3. 벡터 저장소 구축
vectorstore = FAISS.from_documents(split_docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 4. 프롬프트 설정 (페르소나 강화)
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 도로 인프라 및 AI 전문가야. 아래 문맥을 바탕으로 전문적이고 친절하게 답변해줘.\n\n맥락: {context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 5. RAG 체인 구성
chain = (
    {
        "context": (lambda x: x["question"]) | retriever,
        "question": lambda x: x["question"],
        "history": lambda x: x["history"]
    }
    | prompt
    | model
    | StrOutputParser()
)

# 6. 대화 실행 루프
chat_history = []
print("--- [실무형 AI 비서 가동] ---")

while True:
    query = input("\n성용님: ")
    if query.lower() in ["exit", "quit", "종료"]:
        break

    response = chain.invoke({
        "question": query,
        "history": chat_history
    })

    print(f"AI 전문가: {response}")

    # 기록 유지
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response))