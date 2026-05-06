from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# 1. 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. PDF 로드 (파일명 정확히 확인!)
loader = PyPDFLoader("농업_현장데이터의_디지털_전환을_위한_영농일지_표준화와_자동화_전략.pdf")
docs = loader.load()

print(f"✅ 총 {len(docs)} 페이지 로드 완료\n")

# 3. 요약 프롬프트
prompt_template = """
당신은 농업 데이터 전문 AI 연구원입니다.
아래 논문 내용을 읽고 핵심 내용을 전문적으로 요약해주세요.

요약 항목:
1. 연구 목적
2. 핵심 내용
3. 주요 결론 및 시사점

논문 내용:
{text}

[AI 연구원의 요약 결과]
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

# 4. 요약 체인 실행
chain = load_summarize_chain(
    llm=llm,
    chain_type="map_reduce",
    map_prompt=prompt,
    combine_prompt=prompt,
    verbose=True
)

result = chain.invoke(docs)
print("\n========== AI 연구원 요약 결과 ==========")
print(result["output_text"])