FROM python:3.13-slim

WORKDIR /app

ENV PYTHONPATH=/app:$PYTHONPATH

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start_api.sh

CMD ["python", "launcher.py"]
