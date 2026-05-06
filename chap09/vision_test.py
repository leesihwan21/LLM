import base64
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# 1. 환경 변수(.env) 로드
load_dotenv()

# 2. 멀티모달 모델 설정 (비전 기능이 지원되는 gpt-4o-mini 사용)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 3. 이미지를 Base64 문자열로 변환하는 함수 (교재 26p)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 4. 분석할 이미지 경로 설정
# 폴더에 분석할 사진을 넣고 파일명을 accident_sample.jpg로 맞춰주세요.
image_path = "accident_sample.jpg" 

if not os.path.exists(image_path):
    print(f"❌ 에러: [{image_path}] 파일을 찾을 수 없습니다. 사진을 chap09 폴더에 넣어주세요!")
else:
    # 이미지 인코딩 실행
    base64_image = encode_image(image_path)

    # 5. 멀티모달 메시지 구성 (교재 27~28p)
    # 5. 멀티모달 메시지 구성 (가장 확실한 인식 방법)
    message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
            {
                "type": "text", 
                "text": (
                    "이 사진은 도로 관제 CCTV 화면이야. "
                    "지금 사진 속 상황이 사고인지, 아니면 그냥 차가 멈춰 있는 건지 분석해줘. "
                    "분석할 수 없다는 말은 하지 말고, 눈에 보이는 차량의 상태나 위치를 바탕으로 관제 보고서를 써줘."
                )
            },
        ]
    )

    # 6. AI에게 전송 및 결과 출력
    print("🔍 AI 관제사가 실시간 이미지를 분석 중입니다...")
    response = llm.invoke([message])
    
    print("\n" + "="*60)
    print("        [ITS 통합 관제 시스템 - 상황 분석 보고서]        ")
    print("="*60)
    print(response.content)
    print("="*60)