import databases.redis_con as redis_con
import databases.mysql_con as mysql_con
r=redis_con.pri_db()


def set_sql_data(au,gu):
    con=mysql_con.sec_db()
    cursor=con.cursor()
    try:
        sql = "INSERT INTO Urls (actual_url,generated_url) VALUES (%s, %s)"
        values = (au,gu)
        cursor.execute(sql,values)
        con.commit()
        return True
    except Exception as e:
        print(f"POST data error {e}")
        return False
    finally:
        cursor.close()
        con.close()
def get_sql_data(gu):
    try:
        con=mysql_con.sec_db()
        cursor=con.cursor()
        sql="SELECT actual_url from Urls WHERE generated_url=%s"
        values=(gu,)
        cursor.execute(sql,values)
        result=cursor.fetchone()
        cursor.close()
        con.close()
        return result
    except Exception as e:
        print(f"Error {e}")
        return None
def set_redis_data(au,gu):
    try:
        r.set(gu,au)
        return True
    except Exception as e:
        print(f"Error : {e}")
        return False
def get_redis_data(gu):
    try:
        if r.exists(gu):
            return r.get(gu)
        else:
            return None

    except Exception as e:
        print(f"GET data error {e}")
        return None


