import redis
import time
def pri_db():
    print("waiting for redis")
    time.sleep(2)
    try:
        r=redis.Redis(host='redis-server',port=6379,db=0,decode_responses=True)

        if r.ping():
            print("Successfully connected to redis")
        return r

    except Exception as e:
        print(f"Error {e}")


