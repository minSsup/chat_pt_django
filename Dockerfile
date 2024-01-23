# 기본 파이썬 이미지를 사용
FROM python:3.11.5-alpine

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# OpenGL 라이브러리와 curl 설치
RUN apk update && apk add curl mesa-gl libaio && rm -rf /var/cache/apk/*

# Oracle Instant Client 다운로드 및 설치

RUN apk --no-cache add libaio libnsl libc6-compat curl && \
    cd /tmp && \
    curl -o instantclient-basiclite.zip https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip -SL && \
    unzip instantclient-basiclite.zip && \
    mv instantclient*/ /usr/lib/instantclient && \
    rm instantclient-basiclite.zip && \
    ln -s /usr/lib/instantclient/libclntsh.so.21.1 /usr/lib/libclntsh.so && \
    ln -s /usr/lib/instantclient/libocci.so.21.1 /usr/lib/libocci.so && \
    ln -s /usr/lib/instantclient/libociicus.so /usr/lib/libociicus.so && \
    ln -s /usr/lib/instantclient/libnnz21.so /usr/lib/libnnz21.so && \
    ln -s /usr/lib/libnsl.so.2 /usr/lib/libnsl.so.1 && \
    ln -s /lib/libc.so.6 /usr/lib/libresolv.so.2 && \
    ln -s /lib64/ld-linux-x86-64.so.2 /usr/lib/ld-linux-x86-64.so.2

ENV LD_LIBRARY_PATH /usr/lib/instantclient

# Oracle Instant Client 설치 후 동적 라이브러리 링크 갱신
RUN echo /usr/local/instantclient_21_3 > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig /lib /usr/lib

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 모델 파일 다운로드
RUN curl -o /app/modelFoodName1_200.h5 https://chat-pt.s3.ap-northeast-2.amazonaws.com/model/modelFoodName1_200.h5

# Django 애플리케이션 추가
COPY . /app/

ENV HOST 0.0.0.0
EXPOSE 9000

# runserver로 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]