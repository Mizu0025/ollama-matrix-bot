FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code
COPY . .

# Create the store directory 
# (We don't chown here because the host mount will override it anyway)
RUN mkdir -p /app/store

ENV DATA_FILE=/app/store/bot_data.json
ENV SESSION_FILE=/app/store/session.txt
ENV PYTHONUNBUFFERED=1

# The bot will run as whatever user:group is specified in docker-compose
CMD ["python", "main.py"]