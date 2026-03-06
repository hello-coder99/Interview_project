FROM python:3.11-slim

WORKDIR /worker

RUN apt update && apt install -y ffmpeg

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY worker.py .

CMD ["python3","worker.py"]
