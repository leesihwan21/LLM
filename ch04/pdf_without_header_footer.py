import fitz
import os

# 1. 파일 설정 (준비하신 PDF 파일명으로 수정하세요)
pdf_file_path = "./gpt-4o-system-card.pdf" # 예시 파일명입니다. 실제 파일명으로 변경해주세요.
doc = fitz.open(pdf_file_path)
full_text = ""

# 2. 전처리 설정 (헤더와 푸터 영역 제외)
# 페이지의 위에서 50pt, 아래에서 50pt를 제외한 영역만 추출 예시
for page in doc:
    # 페이지 크기 확인
    page_rect = page.rect 
    # 본문 영역 지정: 상단(y0) 50~100, 하단(y1) 50~100 정도 여백을 둡니다.
    # [x0, y0, x1, y1] -> 좌, 상, 우, 하 좌표
    content_box = fitz.Rect(0, 70, page_rect.width, page_rect.height - 70)
    
    # 지정한 사각형(Rect) 안의 텍스트만 추출
    text = page.get_text("text", clip=content_box)
    full_text += text

# 3. 결과 저장
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

output_path = os.path.join(output_folder, "clean_text.txt")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"전처리 완료! 결과 저장: {output_path}")