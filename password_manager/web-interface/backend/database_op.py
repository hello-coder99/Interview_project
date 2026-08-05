import backend.mysql_op as mysql_op
import backend.redis_op as redis_op

def get_password(name):
    r_data=redis_op.get_data(name)
    if r_data is not None:
        return r_data
    s_data=mysql_op.get_sdata(name)
    if s_data is not None:
        redis_op.set_data(name,s_data)
        return s_data
    return "not_found"

def get_names():
    data=mysql_op.get_all_names()
    if data is not None:
        result=""
        for i in range(len(data)):
            result+=data[i][0]+"\n"
        return result
    return "not_found"

def store_password(name,password):
    res=mysql_op.set_sdata(name,password)
    return res

def delete_password(name):
    res=redis_op.delete_data(name)
    res2=mysql_op.delete_sdata(name)
    if res is not None and res2 is not None:
        return "deleted_from_redis_mysql"
    if res is not None:
        return "deleted_from_redis"
    if res2 is not None:
        return "deleted_from_mysql"
    return "deleted_from_none"
