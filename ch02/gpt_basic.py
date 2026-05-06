import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. .env 파일의 API 키 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

# 2. 터미널에서 사용자 입력 받기
print("--------------------------------------------------")
user_input = input("GPT에게 궁금한 점을 입력하세요: ")
print("--------------------------------------------------")

# 3. GPT에게 질문 전달
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_input}
    ]
)

# 4. 답변 출력
print("\n[GPT의 답변]")
print(response.choices[0].message.content)
print("--------------------------------------------------")