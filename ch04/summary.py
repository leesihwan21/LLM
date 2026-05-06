import openai
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 1. 농공학회 PDF 읽어오기
loader = PyPDFLoader("농업 현장데이터의 디지털 전환을 위한 영농일지 표준화와 자동화 전략.pdf")
docs = loader.load()

# 페이지 전체 텍스트 합치기
text_to_summarize = "\n".join([doc.page_content for doc in docs])

print(f"✅ 총 {len(docs)} 페이지 로드 완료\n")

# 2. GPT에게 요약 요청 (AI 연구원 페르소나로 변경!)
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "너는 농업 데이터 전문 AI 연구원이야. 논문을 읽고 전문적으로 요약해줘."
        },
        {
            "role": "user",
            "content": f"""다음 논문을 아래 항목으로 요약해줘:
1. 연구 목적
2. 핵심 내용
3. 주요 결론 및 시사점

논문 내용:
{text_to_summarize}"""
        }
    ]
)

# 3. 결과 출력
print("-" * 30)
print("📚 AI 연구원 요약 결과:")
print(response.choices[0].message.content)
print("-" * 30)