import os
import json
import pytz
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 1. 환경 설정 및 클라이언트 초기화
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. 기능 함수들 정의 (책의 내용 반영)
def get_current_time(timezone='Asia/Seoul'):
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[시스템] {timezone} 시간 조회 중...")
        return f"{now} {timezone}"
    except Exception as e:
        return f"타임존 오류: {e}"

def get_stock_price(company_name):
    # 실제 주가 조회 로직 대신 책의 예시 데이터 사용
    prices = {"삼성전자": "75,000원", "애플": "180달러", "엔비디아": "900달러"}
    price = prices.get(company_name, "정보를 찾을 수 없습니다.")
    print(f"\n[시스템] {company_name} 주가 조회 중...")
    return price

def get_exchange_rate(currency_pair):
    # 실제 환율 조회 로직 대신 책의 예시 데이터 사용
    rates = {"USD/KRW": "1,350원", "JPY/KRW": "900원"}
    rate = rates.get(currency_pair, "정보를 찾을 수 없습니다.")
    print(f"\n[시스템] {currency_pair} 환율 조회 중...")
    return rate

# 3. GPT에게 알려줄 [도구 명세서] 확장
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "지정한 지역의 현재 날짜와 시간을 알려줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "타임존 명칭"}
                },
                "required": ["timezone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "지정한 회사의 주식 가격을 알려줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "회사 이름"}
                },
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "지정한 통화 쌍의 환율을 알려줍니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency_pair": {"type": "string", "description": "통화 쌍 (예: USD/KRW)"}
                },
                "required": ["currency_pair"],
            },
        },
    }
]

# 4. 메인 대화 루프
messages = [{"role": "system", "content": "너는 시간, 주가, 환율을 안내하는 유능한 비서야."}]

print("=== 🤖 통합 에이전트 실행 중 ('exit' 입력 시 종료) ===")

while True:
    user_input = input("\n사용자: ")
    if user_input.lower() in ["exit", "종료", "quit"]:
        break
    
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    ai_message = response.choices[0].message
    
    if ai_message.tool_calls:
        messages.append(ai_message)
        
        # 여러 개의 함수 호출을 처리할 수 있는 루프
        for tool_call in ai_message.tool_calls:
            function_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # 함수 이름에 따라 실행 분기 처리
            if function_name == "get_current_time":
                observation = get_current_time(timezone=args.get("timezone"))
            elif function_name == "get_stock_price":
                observation = get_stock_price(company_name=args.get("company_name"))
            elif function_name == "get_exchange_rate":
                observation = get_exchange_rate(currency_pair=args.get("currency_pair"))
            
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": str(observation),
            })
        
        final_response = client.chat.completions.create(model="gpt-4o", messages=messages)
        ai_message = final_response.choices[0].message

    print(f"AI: {ai_message.content}")
    messages.append(ai_message)