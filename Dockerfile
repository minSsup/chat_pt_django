# 기본 파이썬 이미지를 사용
FROM python:3.11.5 as builder

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Gunicorn 설치
# RUN pip install gunicorn

# 모델 파일 추가
COPY modelFoodName1_200.h5 /app

# Django 애플리케이션 추가
COPY . /app/

# 빌드 완료
#FROM python:3.11.5-slim
#
#WORKDIR /app
#
#COPY --from=builder /app /app

# Gunicorn 실행
# CMD ["gunicorn", "django.wsgi:application", "-b", "0.0.0.0:9000"]

ENV HOST 0.0.0.0
EXPOSE 9000

# Django 애플리케이션 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]