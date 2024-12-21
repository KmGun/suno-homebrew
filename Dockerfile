# PyTorch 공식 이미지를 기반으로 사용
FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

# 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive

# Conda를 사용하여 Python 3.10.12 설치 및 환경 설정
RUN conda install -y python=3.10.12 && \
    conda clean -ya

# 빌드 도구 및 의존성 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    git \
    sox libsox-fmt-mp3 \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libpostproc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip==23.1.2

# 필수 패키지 설치
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 작업 디렉토리 설정
COPY . /app
WORKDIR /app


CMD ["python", "/app/main.py"]