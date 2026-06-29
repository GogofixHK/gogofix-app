FROM python:3.11-slim

WORKDIR /app

# Create writable data directory
RUN mkdir -p /data
ENV DATA_DIR=/data

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY gogofix_api.py .
COPY templates/ templates/
COPY static/ static/

EXPOSE 8000

# Python startup script
RUN echo 'import os, sys' > /start.py && \
    echo 'port = int(os.environ.get("PORT", "8000"))' >> /start.py && \
    echo 'print(f"Starting GoGofix on port {port}, DATA_DIR={os.environ.get(\"DATA_DIR\", \"N/A\")}")' >> /start.py && \
    echo 'import uvicorn' >> /start.py && \
    echo 'uvicorn.run("gogofix_api:app", host="0.0.0.0", port=port, log_level="info")' >> /start.py

CMD ["python", "/start.py"]
