FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY gogofix_api.py .
COPY templates/ templates/
COPY static/ static/

# Use a startup script to debug
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'echo "PORT=$PORT"' >> /start.sh && \
    echo 'exec python3 -m uvicorn gogofix_api:app --host 0.0.0.0 --port ${PORT:-8000}' >> /start.sh && \
    chmod +x /start.sh

CMD ["/start.sh"]
