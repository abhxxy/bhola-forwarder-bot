FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py transformer.py ./
COPY entrypoint.sh ./
RUN chmod 755 entrypoint.sh && mkdir -p /data

VOLUME ["/data"]
ENTRYPOINT ["/app/entrypoint.sh"]
