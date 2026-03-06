import whisper
import redis
import json
import time

r=redis.Redis(host="redis",port=6379,decode_responses=True)

QUEUE="audio_jobs"
RESULT_PREFIX="result:"

model=whisper.load_model("base")

print("whiper worker started")

while True:
    job=r.brpop(QUEUE)
    payload=json.loads(job[1])

    job_id=payload["job_id"]
    file_path=payload["file_path"]

    print(f"processing {file_path}")

    result=model.transcribe(file_path)
    text=result["text"]

    r.set(RESULT_PREFIX+job_id,text)
