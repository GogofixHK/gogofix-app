FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY gogofix_api.py .
COPY templates/ templates/
COPY static/ static/

# Run with uvicorn
CMD ["python3", "-m", "uvicorn", "gogofix_api:app", "--host", "0.0.0.0", "--port", "8000"]
