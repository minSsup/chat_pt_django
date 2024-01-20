# 기본 파이썬 이미지를 사용
FROM python:3.11.5-slim

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y curl unzip libaio1 libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Oracle Instant Client 버전 설정
ENV ORACLE_INSTANTCLIENT_VERSION 19.8.0.0.0dbru

# Oracle Instant Client 다운로드
RUN mkdir /opt/oracle && \
    cd /opt/oracle && \
    curl -O https://download.oracle.com/otn_software/linux/instantclient/${ORACLE_INSTANTCLIENT_VERSION}/instantclient-basiclite-linux.x64-${ORACLE_INSTANTCLIENT_VERSION}.zip

# Oracle Instant Client 설치
RUN cd /opt/oracle && \
    unzip instantclient-basiclite-linux.x64-${ORACLE_INSTANTCLIENT_VERSION}.zip && \
    rm -f instantclient-basiclite-linux.x64-${ORACLE_INSTANTCLIENT_VERSION}.zip && \
    cd instantclient* && \
    rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci && \
    echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Gunicorn 설치
RUN pip install gunicorn

# 모델 파일 추가
COPY modelFoodName1_200.h5 /app

# Django 애플리케이션 추가
COPY . /app/

ENV HOST 0.0.0.0
EXPOSE 9000

# Gunicorn 실행
CMD ["gunicorn", "ChatPtDjango.wsgi:application", "-b", "0.0.0.0:9000"]
