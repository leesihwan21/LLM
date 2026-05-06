import streamlit as st
import os
import json
import pytz
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 환경 설정
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# [함수 정의] 시간 조회
def get_current_time(timezone='Asia/Seoul'):
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"{now} {timezone}"
    except Exception as e:
        return f"Error: {e}"

# [도구 명세]
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "지정한 타임존의 현재 시간을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "예: Asia/Seoul, America/New_York"}
            },
            "required": ["timezone"],
        },
    }
}]

# --- 스트림릿 UI 시작 ---
st.set_page_config(page_title="🌍 세계 시간 AI 비서", page_icon="⏰")
st.title("🌍 세계 시간 AI 비서")
st.caption("궁금한 지역의 시간을 물어보세요! (예: 뉴욕 지금 몇 시야?)")

# 대화 기록 초기화 (세션 상태 이용)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "너는 전 세계 시간을 안내하는 비서야."}]

# 기존 대화 표시
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("메시지를 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 답변 생성
    with st.chat_message("assistant"):
        with st.status("⏳ 시간을 확인하는 중...", expanded=True) as status:
            # 1차 호출
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                tools=tools
            )
            ai_message = response.choices[0].message
            
            if ai_message.tool_calls:
                st.session_state.messages.append(ai_message)
                for tool_call in ai_message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    result = get_current_time(timezone=args.get('timezone'))
                    
                    st.write(f"✅ {args.get('timezone')} 시간 조회 완료")
                    
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": result
                    })
                
                # 2차 호출 (최종 답변)
                final_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages
                )
                final_answer = final_response.choices[0].message.content
            else:
                final_answer = ai_message.content
            
            status.update(label="✅ 조회 완료!", state="complete", expanded=False)

        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})