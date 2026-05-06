import streamlit as st
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from gpt_functions import get_company_info, get_current_time, get_stock_price, get_exchange_rate, tools

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="AI 통합 비서", page_icon="🤖")
st.title("🤖 통합 정보 에이전트")
st.caption("주식, 환율, 세계 시간, 기업 정보를 한 번에 물어보세요!")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "너는 유능한 종합 정보 비서야."}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message.get("content", ""))

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🔍 정보를 분석하고 도구를 실행하는 중...", expanded=True) as status:
            # 1. GPT 1차 호출 (스트리밍 모드)
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                tools=tools,
                stream=True 
            )

            full_response_text = ""
            tool_calls = []

            # 스트리밍 조각(chunk) 처리
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_response_text += delta.content
                
                if delta.tool_calls:
                    for tc_chunk in delta.tool_calls:
                        if len(tool_calls) <= tc_chunk.index:
                            tool_calls.append(tc_chunk)
                        else:
                            # 쪼개져서 들어오는 인자값(arguments)을 합침
                            if tc_chunk.function.arguments:
                                tool_calls[tc_chunk.index].function.arguments += tc_chunk.function.arguments

            # 2. 도구 호출 처리
            if tool_calls:
                # GPT의 도구 호출 요청을 메시지 내역에 추가
                assistant_tool_call_msg = {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                        } for tc in tool_calls
                    ]
                }
                st.session_state.messages.append(assistant_tool_call_msg)

                for tc in tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    
                    if name == "get_current_time":
                        res = get_current_time(timezone=args.get('timezone'))
                    elif name == "get_stock_price":
                        res = get_stock_price(company_name=args.get('company_name'))
                    elif name == "get_exchange_rate":
                        res = get_exchange_rate(currency_pair=args.get('currency_pair'))
                    elif name == "get_company_info":
                        res = get_company_info(company_name=args.get('company_name'))
                    
                    st.write(f"✅ {name} 실행 완료")
                    
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": name,
                        "content": str(res)
                    })
                
                # 모든 도구 실행 후 최종 답변 생성을 위한 2차 호출 (스트리밍)
                final_stream = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages,
                    stream=True
                )
                
                message_placeholder = st.empty()
                final_answer = ""
                for chunk in final_stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        final_answer += content
                        message_placeholder.markdown(final_answer + "▌")
                message_placeholder.markdown(final_answer)
                
            else:
                # 도구 호출이 없는 일반 대화인 경우
                st.markdown(full_response_text)
                final_answer = full_response_text
            
            status.update(label="✅ 모든 정보 조회 완료!", state="complete", expanded=False)

        st.session_state.messages.append({"role": "assistant", "content": final_answer})