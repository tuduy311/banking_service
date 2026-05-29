FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY frontend/requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /src/requirements.txt

COPY . /src

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "frontend/main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
