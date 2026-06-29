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

# Write startup script as a file
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
