import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.messages import ToolMessage
import yfinance as yf

# 1. 환경 설정 및 모델 선언
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. 파이단틱(Pydantic)으로 입력 데이터 형식 정의
class StockPriceInput(BaseModel):
    ticker: str = Field(description="주식 종목 코드 (예: AAPL, TSLA, NVDA)")

# 3. @tool 데코레이터로 AI가 쓸 도구 만들기
@tool("get_stock_price", args_schema=StockPriceInput)
def get_stock_price(ticker: str) -> str:
    """지정한 주식 종목의 최신 가격 정보를 가져오는 함수입니다."""
    stock = yf.Ticker(ticker)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return f"{ticker}의 현재 주가는 {price:.2f}달러입니다."

# 4. 모델에 도구 바인딩 (AI에게 도구의 존재를 알림)
tools = [get_stock_price]
llm_with_tools = llm.bind_tools(tools)

# 5. 실행 테스트
print("--- [테스트 1: 일반 질문] ---")
res1 = llm_with_tools.invoke("안녕? 넌 누구니?")
print(f"답변: {res1.content}") # 일반 답변 출력
print(f"도구 호출 여부: {res1.tool_calls}") # 비어있음

print("\n--- [테스트 2: 도구가 필요한 질문] ---")
res2 = llm_with_tools.invoke("테슬라(TSLA) 주가 좀 알려줄래?")
print(f"답변: {res2.content}") # AI는 직접 답하지 않고 도구 호출 정보를 보냄
print(f"도구 호출 정보: {res2.tool_calls}") 

# 6. AI가 판단한 도구를 실제로 실행하기
if res2.tool_calls:
    for tool_call in res2.tool_calls:
        # AI가 고른 도구 실행 (여기서는 get_stock_price)
        result = get_stock_price.invoke(tool_call["args"])
        print(f"\n[도구 실행 결과]: {result}")

# 7. 도구 실행 결과를 메시지 이력에 추가하고 최종 답변 받기
if res2.tool_calls:
    # 도구 실행 결과를 ToolMessage 형태로 만듦
    tool_msg = ToolMessage(
        content=result, 
        tool_call_id=res2.tool_calls[0]["id"]
    )
    
    # 질문 + AI의 도구 호출 결정 + 도구 실행 결과 -> 이 3개를 다시 AI에게 보냄
    final_res = llm_with_tools.invoke([
        ("human", "테슬라(TSLA) 주가 좀 알려줄래?"),
        res2, 
        tool_msg
    ])
    
    print(f"\n--- [최종 AI 답변] ---")
    print(final_res.content)