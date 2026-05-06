from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

print("📄 PDF 로딩 중...")

# 1. PDF 로드
loader = PyPDFLoader("수원_도시기본계획.pdf")
docs = loader.load()
print(f"✅ 총 {len(docs)} 페이지 로드 완료")

# 2. 텍스트 분할 (청크)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(docs)
print(f"✅ 총 {len(chunks)} 청크 분할 완료")

# 3. 벡터 DB 생성 (임베딩)
print("🔄 벡터 DB 생성 중... (시간이 걸릴 수 있어요)")
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
print("✅ 벡터 DB 생성 완료!")

# 4. 프롬프트 설정
prompt = ChatPromptTemplate.from_messages([
    ("system", """너는 수원시 도시기본계획 전문 AI 어시스턴트야.
아래 문서 내용을 바탕으로 질문에 답변해줘.
문서에 없는 내용은 '문서에서 찾을 수 없습니다'라고 말해줘.

[관련 문서]
{context}"""),
    ("human", "{question}")
])

# 5. RAG 체인 구성
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. 챗봇 실행
print("\n" + "="*50)
print("🏙️ 수원시 도시기본계획 RAG 챗봇")
print("="*50)

while True:
    question = input("\n질문: ")
    if question.lower() == "exit":
        break
    
    print("\n🔍 답변:")
    response = rag_chain.invoke(question)
    print(response)
    print("-"*50)