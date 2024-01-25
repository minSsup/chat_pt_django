# 기본 파이썬 이미지를 사용
FROM python:3.11.5

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 설정
WORKDIR /app

# OpenGL 라이브러리와 curl 설치
RUN apt-get update && apt-get install -y libgl1-mesa-glx libaio1 curl && rm -rf /var/lib/apt/lists/*

# Oracle Instant Client 다운로드 및 설치
RUN curl -o instantclient-basic-linux.x64-21.3.0.0.0.zip https://download.oracle.com/otn_software/linux/instantclient/213000/instantclient-basic-linux.x64-21.3.0.0.0.zip && \
    unzip instantclient-basic-linux.x64-21.3.0.0.0.zip -d /usr/local/ && \
    rm -f instantclient-basic-linux.x64-21.3.0.0.0.zip && \
    echo /usr/local/instantclient_21_3 > /etc/ld.so.conf.d/oracle-instantclient.conf && \
    ldconfig

# Oracle Instant Client 설치 후 동적 라이브러리 링크 갱신
RUN echo /usr/local/instantclient_21_3 > /etc/ld.so.conf.d/oracle-instantclient.conf && ldconfig

# 필요한 패키지 설치
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 모델 파일 다운로드
RUN curl -o /app/modelFoodName1_1000_std.h5 https://chat-pt.s3.ap-northeast-2.amazonaws.com/model/modelFoodName1_200.h5

# Django 애플리케이션 추가
COPY . /app/

ENV HOST 0.0.0.0
EXPOSE 9000

# runserver로 실행
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
