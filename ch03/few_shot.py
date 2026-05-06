from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from dotenv import load_dotenv

load_dotenv()  # .env 에서 API 키 로드

# 1. 모델 설정
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. 퓨샷 예시 정의
examples = [
    {
        "input": "고양이 어떻게 해야 되는 거야?",
        "output": "고양이한테 밥 줘야 해! 쓰다듬어 주면 너무 좋아해~ 야옹~ 🐱"
    },
    {
        "input": "물고기 어떻게 해야 되는 거야?",
        "output": "어항에 넣어줘야 해! 밥도 조금만 줘야 해~ 많이 주면 죽는대! 🐟"
    },
]

# 3. 예시 프롬프트 템플릿
example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

# 4. 퓨샷 프롬프트 구성
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

# 5. System + FewShot + 질문 합치기
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 유치원생이야. 유치원생처럼 답변해줘."),
    few_shot_prompt,
    ("human", "{input}"),
])

# 6. 체인 실행
chain = final_prompt | llm
response = chain.invoke({"input": "강아지 어떻게 해야되는거야?"})

print(response.content)