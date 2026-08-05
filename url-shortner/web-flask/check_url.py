import use_op
from shorten import generate_new_url

def register_url(au):
    count=0
    while count<5:
        gc=generate_new_url()
        if use_op.set_sql_data(au,gc):
            return gc
        count+=1
    return None

def fetch_url(gc):
    re_data=use_op.get_redis_data(gc)
    if re_data:
        print("retured from redis")
        return re_data
    sq_data=use_op.get_sql_data(gc)
    if sq_data:
        print("returned from sql")
        use_op.set_redis_data(sq_data[0],gc)
        return sq_data[0]
    return None
