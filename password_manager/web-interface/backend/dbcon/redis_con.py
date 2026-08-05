import redis
def pri_db():
    try:
        r=redis.Redis(host='cache',port=6379,db=0,decode_responses=True)

        if r.ping():
            print("Successfully connected to redis")
        else:
            print("Not connected to the redis")
        return r

    except Exception as e:
        print(f"Error {e}")
