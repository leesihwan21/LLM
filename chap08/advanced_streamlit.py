import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableParallel

load_dotenv()

st.set_page_config(page_title="ITS-Guard Pro", page_icon="🛡️")
st.title("🛡️ ITS-Guard Pro: 근거 기반 상담")

# 1. RAG 엔진 (출처 정보를 함께 반환하도록 구성)
@st.cache_resource
def init_rag_engine():
    # 폴더 내의 모든 txt, pdf를 읽도록 확장 가능
    loader = TextLoader("./my_project.txt", encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    split_docs = text_splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(split_docs, OpenAIEmbeddings())
    return vectorstore.as_retriever(search_kwargs={"k": 3}) # 관련도가 높은 3개 문서 추출

retriever = init_rag_engine()

# 2. 대화 기록
msgs = StreamlitChatMessageHistory(key="chat_messages_pro")

# 3. 프롬프트 (근거를 명시하도록 지시)
prompt = ChatPromptTemplate.from_messages([
    ("system", "너는 도로 인프라 AI 전문가야. 반드시 주어진 '맥락'만을 바탕으로 답변해. "
               "답변 끝에는 참고한 문서의 핵심 문구를 '근거' 섹션에 요약해서 적어줘.\n\n맥락: {context}"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 4. 출처를 포함한 RAG 체인 (RunnableParallel 사용)
# 4. 출처를 포함한 RAG 체인 수정
# retriever에게 전체 dict가 아닌 'question' 문자열만 전달하도록 itemgetter 등을 사용하거나 람다를 씁니다.

rag_chain_from_docs = (
    RunnablePassthrough.assign(context=(lambda x: x["context"]))
    | prompt
    | model
    | StrOutputParser()
)

# 이 부분이 핵심 수정 사항입니다!
rag_chain_with_source = RunnableParallel(
    {
        # retriever에게 x["question"] 문자열만 전달하도록 변경
        "context": (lambda x: x["question"]) | retriever, 
        "question": lambda x: x["question"], 
        "history": lambda x: x["history"]
    }
).assign(answer=rag_chain_from_docs)

chain_with_history = RunnableWithMessageHistory(
    rag_chain_with_source,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
    output_messages_key="answer", # 답변 필드를 지정
)

# 5. UI 출력
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt_input := st.chat_input("프로젝트에 대해 궁금한 점을 물어보세요..."):
    st.chat_message("human").write(prompt_input)

    with st.spinner("문서 확인 중..."):
        config = {"configurable": {"session_id": "pro_user"}}
        full_response = chain_with_history.invoke({"question": prompt_input}, config)
        
        answer = full_response["answer"]
        sources = full_response["context"] # 검색된 문서 원본들

    with st.chat_message("ai"):
        st.write(answer)
        # 사이드바나 접기 메뉴로 출처 표시
        with st.expander("📚 참고한 문서 내용 보기"):
            for i, doc in enumerate(sources):
                st.markdown(f"**기록 {i+1}**: {doc.page_content[:200]}...")