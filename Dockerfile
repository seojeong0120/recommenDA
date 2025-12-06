FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# requirements.txt 위치가
# senior-exercise-recommender-core/requirements.txt
# 인 경우
COPY senior-exercise-recommender-core/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 실제 코드 전체 복사
COPY senior-exercise-recommender-core /app

# Railway가 주는 PORT 환경변수 사용 (기본값 8000)
ENV PORT=8000
EXPOSE 8000

# FastAPI: api.py 파일 안에 app = FastAPI() 인 경우
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]