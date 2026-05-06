import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. 파일 불러오기 (Document Loader)
loader = TextLoader("./my_project.txt", encoding="utf-8")
docs = loader.load()

# 2. 문서 쪼개기 (Text Splitter) - 너무 길면 AI가 읽기 힘들거든요
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=20)
split_docs = text_splitter.split_documents(docs)

# 3. 벡터 저장소 구축
vectorstore = FAISS.from_documents(split_docs, OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 4. 프롬프트 설정
template = """아래의 문맥만을 사용하여 질문에 답하세요:
{context}

질문: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-4o-mini")

# 5. RAG 체인 구성
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 6. 실행 및 검색 과정 확인
question = "ITS-Guard의 주요 기술이 뭐야?"

# 검색된 원본 문서 확인 (2번 과제: 검색 과정 확인)
relevant_docs = retriever.invoke(question)
print("--- [검색된 관련 문장들] ---")
for i, doc in enumerate(relevant_docs):
    print(f"[{i+1}]: {doc.page_content}")

# 최종 답변 출력
print("\n--- [AI 최종 답변] ---")
print(chain.invoke(question))