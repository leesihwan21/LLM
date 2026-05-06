import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 환경 변수 로드 (.env 파일에 저장된 API 키를 읽어옵니다)
load_dotenv()

# 2. LLM 모델 설정
# 온도(temperature)는 0으로 설정하면 답변이 더 일관되게 나옵니다.
model = ChatOpenAI(model="gpt-4o", temperature=0)

# 프롬프트 부분을 이렇게 바꿔보세요!
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 정보를 구조화해서 잘 전달하는 전문 강사야. 답변은 반드시 아래 형식을 지켜줘."),
    ("user", "{topic}에 대해 설명해줘.\n\n### 형식\n1. 한 줄 요약\n2. 세부 특징 3가지")
])

# 4. 출력 파서 설정
# AI의 복잡한 응답 객체에서 텍스트만 쏙 뽑아냅니다.
output_parser = StrOutputParser()

# 5. 체인(Chain) 생성 (LCEL 문법)
# 💡 이 한 줄이 랭체인의 꽃입니다! "프롬프트 -> 모델 -> 파서" 순으로 연결합니다.
chain = prompt | model | output_parser

# 6. 실행 및 결과 출력 (사용자 입력을 받도록 수정)
user_input = input("어떤 주제에 대해 알고 싶으신가요? : ")
result = chain.invoke({"topic": user_input})

print("\n--- [AI 답변] ---")
print(result)