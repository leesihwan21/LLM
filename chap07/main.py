import os
import json
import yfinance as yf
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- [도구 함수 정의] ---
def get_stock_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return str(round(price, 2))
    except Exception:
        return "가격을 가져올 수 없습니다."

def get_exchange_rate(from_currency, to_currency):
    try:
        ticker = f"{from_currency}{to_currency}=X"
        data = yf.Ticker(ticker)
        rate = data.history(period="1d")['Close'].iloc[-1]
        return str(round(rate, 2))
    except Exception:
        return "환율 정보를 가져올 수 없습니다."

# --- [도구 명세서] ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "미국 주식 종목의 현재 가격을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "주식 티커 심볼 (예: AAPL, NVDA)"}
                },
                "required": ["ticker"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "국가 간의 실시간 환율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "기준 통화 (예: USD)"},
                    "to_currency": {"type": "string", "description": "대상 통화 (예: KRW)"}
                },
                "required": ["from_currency", "to_currency"],
            },
        },
    }
]

# --- [메인 로직] ---
messages = [{"role": "user", "content": "엔비디아(NVDA) 주가 알려주고, 오늘 환율(USD to KRW) 적용해서 한국 돈으로 얼마인지 계산해줘."}]

print("📡 GPT에게 질문을 보내는 중...")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

response_message = response.choices[0].message
tool_calls = response_message.tool_calls

if tool_calls:
    print(f"🚀 GPT가 {len(tool_calls)}개의 도구 사용을 결정했습니다!")
    messages.append(response_message)

    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        observation = ""

        if function_name == "get_stock_price":
            observation = get_stock_price(function_args.get("ticker"))
            print(f"✅ 주가 확인 완료")
        elif function_name == "get_exchange_rate":
            observation = get_exchange_rate(function_args.get("from_currency"), function_args.get("to_currency"))
            print(f"✅ 환율 확인 완료")

        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": function_name,
            "content": str(observation),
        })

    final_response = client.chat.completions.create(model="gpt-4o", messages=messages)
    print("\n--- 🤖 GPT의 최종 답변 ---")
    print(final_response.choices[0].message.content)