# gpt_functions.py
import pytz
from datetime import datetime

def get_current_time(timezone='Asia/Seoul'):
    """지정한 지역의 현재 날짜와 시간을 반환합니다."""
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"{now} {timezone}"
    except Exception as e:
        return f"타임존 오류: {e}"

def get_stock_price(company_name):
    """주식 가격을 조회하는 함수 (확장된 예시 데이터 30개)"""
    prices = {
        # 한국 주요 기업 (IT, 자동차, 바이오)
        "삼성전자": "75,000원", "SK하이닉스": "180,000원", "현대차": "250,000원", 
        "기아": "120,000원", "NAVER": "190,000원", "카카오": "48,000원", 
        "삼성바이오로직스": "800,000원", "셀트리온": "180,000원", "LG에너지솔루션": "380,000원", 
        "POSCO홀딩스": "400,000원", "에코프로": "550,000원", "에코프로비엠": "230,000원",
        
        # 해외 주요 기업 (빅테크)
        "애플": "185달러", "마이크로소프트": "420달러", "구글": "150달러", 
        "아마존": "175달러", "엔비디아": "920달러", "테슬라": "170달러", 
        "메타": "490달러", "넷플릭스": "610달러", "어도비": "500달러", 
        "오라클": "125달러", "인텔": "45달러", "AMD": "180달러",
        
        # 기타 유명 브랜드
        "코카콜라": "60달러", "스타벅스": "90달러", "디즈니": "115달러", 
        "나이키": "100달러", "맥도날드": "280달러", "비자": "270달러"
    }
    
    # [시스템] 로그 출력 (확인용)
    print(f"\n[시스템] '{company_name}' 주가 조회 시도 중...")
    
    # 딕셔너리에서 찾기 (없으면 안내 메시지)
    price = prices.get(company_name)
    
    if price:
        return f"{company_name}의 현재 주가는 {price}입니다."
    else:
        return f"현재 목록에는 '{company_name}' 정보가 없습니다. (삼성전자, 애플, 테슬라 등 30개 기업 조회 가능)"

def get_exchange_rate(currency_pair):
    """환율 조회 (예시 데이터)"""
    rates = {"USD/KRW": "1,350원", "JPY/KRW": "900원"}
    return rates.get(currency_pair, "정보를 찾을 수 없습니다.")

# 도구 명세서
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "현재 시간을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {"timezone": {"type": "string"}},
                "required": ["timezone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "주가를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {"company_name": {"type": "string"}},
                "required": ["company_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "환율을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {"currency_pair": {"type": "string"}},
                "required": ["currency_pair"],
            },
        },
    }
]

def get_company_info(company_name):
    """지정한 회사의 주요 사업 내용 및 정보를 알려줍니다."""
    companies = {
        "삼성전자": "대한민국의 대표적인 글로벌 전자 기업으로, 반도체, 스마트폰, 가전제품 등을 생산합니다.",
        "애플": "아이폰, 맥, 아이패드 등을 설계 및 판매하며 소프트웨어와 서비스를 제공하는 미국 기업입니다.",
        "엔비디아": "GPU 설계 및 AI 컴퓨팅 분야의 선두주자로, 데이터 센터와 게임 산업에 핵심 칩을 공급합니다.",
        "테슬라": "전기자동차, 에너지 저장 장치 및 태양광 패널을 생산하며 자율주행 기술을 개발하는 미국 기업입니다."
    }
    
    print(f"\n[시스템] '{company_name}' 기업 정보 조회 중...")
    info = companies.get(company_name, "해당 기업에 대한 상세 정보가 등록되어 있지 않습니다.")
    return info

# --- tools 리스트에도 추가 ---
tools.append({
    "type": "function",
    "function": {
        "name": "get_company_info",
        "description": "지정한 회사의 사업 개요 및 기업 설명을 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "company_name": {"type": "string", "description": "회사 이름"}
            },
            "required": ["company_name"],
        },
    },
})