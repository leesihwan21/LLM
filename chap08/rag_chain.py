from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# 1. 가상의 문서 데이터 (나중에는 PDF나 텍스트 파일을 불러올 수 있어요)
text_data = [
    "성용님은 현재 AI-X 스마트 교통 및 인프라 유지관리 교육을 받고 있습니다.",
    "성용님의 프로젝트인 'ITS-Guard'는 YOLOv8을 활용해 도로의 포트홀을 탐지합니다.",
    "이 교육 과정은 2026년 7월 초에 종료될 예정입니다."
]

# .env 파일에 기록된 OPENAI_API_KEY를 환경 변수로 불러옵니다.
load_dotenv()

# 2. 데이터를 벡터로 변환하여 저장소(Retriever) 만들기
vectorstore = FAISS.from_texts(text_data, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# 3. 프롬프트 설정 (맥락을 활용하도록 지시)
template = """아래 제공된 맥락(context)만을 사용하여 질문에 답하세요. 
답변을 모를 경우 모른다고 답하고 정보를 지어내지 마세요.

맥락: {context}

질문: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-4o-mini")

# 4. RAG 체인 구성
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

# 5. 실행
print("--- [RAG 시스템 가동] ---")
print(chain.invoke("성용님이 개발 중인 프로젝트 이름이 뭐야?"))