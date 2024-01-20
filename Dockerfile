# 기본 파이썬 이미지를 사용
FROM python:3.11.5 as builder

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# OpenGL 라이브러리 설치 명령어
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Gunicorn 설치
RUN pip install --no-cache-dir gunicorn

# 모델 파일 추가
COPY modelFoodName1_200.h5 /app

# Django 애플리케이션 추가
COPY . /app/

ENV HOST 0.0.0.0
EXPOSE 9000

# Gunicorn 실행
CMD ["gunicorn", "ChatPtDjango.wsgi:application", "-b", "0.0.0.0:9000"]