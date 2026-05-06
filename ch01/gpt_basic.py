import openai
from openai import OpenAI

client = OpenAI(api_key="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")

# 터미널에서 입력을 직접 받도록 수정
user_input = input("GPT에게 물어볼 말을 입력하세요: ")

response = client.chat.completions.create(
    model="gpt-4o-mini", # 비용이 저렴한 최신 모델
    messages=[
        {"role": "user", "content": user_input}
    ]
)

print("\n[GPT의 답변]")
print(response.choices[0].message.content)