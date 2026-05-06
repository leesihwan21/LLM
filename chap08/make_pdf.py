from fpdf import FPDF

def create_yolo_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # 제목
    pdf.cell(200, 10, txt="YOLOv8 Technical Specification Report", ln=True, align='C')
    
    # 내용
    pdf.set_font("Arial", size=12)
    content = [
        "",
        "1. Model Overview",
        "Ultralytics YOLOv8 is a state-of-the-art model designed for real-time object detection.",
        "",
        "2. Key Architectural Innovations",
        "- Anchor-Free Detection: Improves detection for varied shapes like potholes.",
        "- C2f Module: Enhances gradient flow and reduces computational overhead.",
        "",
        "3. Training & Optimization",
        "- Loss Functions: Employs VFL and CIoU + DFL for extreme precision.",
        "- Mosaic Augmentation: Optimized for the final training stages.",
        "",
        "4. ITS-Guard Application",
        "- Real-time Inference: Optimized for Edge-AI devices in road monitoring."
    ]
    
    for line in content:
        pdf.cell(200, 10, txt=line, ln=True, align='L')
    
    pdf.output("YOLOv8_Spec.pdf")
    print("✅ YOLOv8_Spec.pdf 파일이 생성되었습니다!")

if __name__ == "__main__":
    create_yolo_pdf()