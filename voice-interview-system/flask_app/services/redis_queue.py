import redis
import json
import uuid

r=redis.Redis(host="redis",port=6379,decode_responses=True)

AUDIO_QUEUE="audio_jobs"
RESULT_PREFIX="result:"

def enqueue_audio(file_path):
    job_id=str(uuid.uuid4())
    payload={
            "job_id":job_id,
            "file_path":file_path
            }
    r.lpush(AUDIO_QUEUE,json.dumps(payload))
    return job_id

def get_transcription(job_id):
    return r.get(RESULT_PREFIX+job_id)
