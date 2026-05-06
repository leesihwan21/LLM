# 🛡️ ITS-Guard (Road Obstacle Detection System)

AI 기반 실시간 도로 위험 요소(포트홀, 싱크홀) 감지 및 지능형 민원 관리 대시보드 프로젝트입니다.

## 🚀 프로젝트 개요
- **목표**: 딥러닝 객체 탐지 기술을 활용하여 도로의 위험 요소를 조기에 발견하고, 이를 관리자에게 실시간으로 통보하여 사고를 예방합니다.
- **주요 타겟**: 스마트 시티 인프라 관리자 및 도로 유지보수 담당자.

## 🛠️ Tech Stack
- **Language**: Python 3.x
- **Framework**: Flask (Backend), PyTorch (AI)
- **AI Model**: YOLOv8
- **Database**: MySQL
- **Infrastructure**: Docker, Linux

## 🏗️ System Architecture
본 프로젝트는 확장성을 위해 중앙 Flask 서버를 중심으로 각 기능이 분리된 마이크로서비스 형태를 지향합니다.
1. **Frontend**: 사용자 대시보드 및 실시간 관제 화면.
2. **Flask Server**: 인증(JWT), 권한 관리 및 DB 연동 총괄.
3. **AI Vision Server**: 영상 데이터 분석 및 객체 탐지 전담.

## 📂 주요 디렉토리 구조
- `/models`: 학습된 YOLOv8 가중치 파일 (.pt)
- `/server`: Flask API 서버 소스 코드
- `/data`: 모델 학습 및 테스트용 데이터셋 정보

## 🤝 Contact
- **Author**: leesihwan21
- **Email**: (여기에 이메일 주소를 적어주세요)
