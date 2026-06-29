FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY gogofix_api.py .
COPY templates/ templates/
COPY static/ static/

# Railway injects PORT env var at runtime
CMD sh -c "python3 -m uvicorn gogofix_api:app --host 0.0.0.0 --port ${PORT:-8000}"
