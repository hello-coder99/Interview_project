from pathlib import Path
import sys

parent_dir=str(Path(__file__).resolve().parent.parent)

if parent_dir not in sys.path:
    sys.path.insert(0,parent_dir)

import use_op
from shorten import generate_new_url

def register_url(au):
    sq=False
    count=0
    while sq==False and count<5:
        gu=generate_new_url()
        sq=use_op.set_sql_data(au,gu)
    return sq

def fetch_url(gu):
    re_data=use_op.get_redis_data(gu)
    if re_data is not None:
        print("retured from redis")
        return re_data
    sq_data=use_op.get_sql_data(gu)
    if sq_data[0] is not None:
        print("returned from sql")
        use_op.set_redis_data(sq_data[0],gu)
        return sq_data[0]
    return None
