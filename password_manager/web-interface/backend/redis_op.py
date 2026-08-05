import backend.dbcon.redis_con as redis_con

def get_data(name):
    try:
        r=redis_con.pri_db()
        if r.exists(name):
            return r.get(name)
        return None
    except Exception as e:
        print(f"Error !! {e}")
        return None
    finally:
        r.close()


def set_data(name,password):
    try:
        r=redis_con.pri_db()
        if r.exists(name):
            return None
        r.set(name,password)
        return "ok"
    except Exception as e:
        print(f"Error !! {e}")
        return None
    finally:
        r.close()


def delete_data(name):
    try:
        r=redis_con.pri_db()
        if r.exists(name):
            r.delete(name)
            return "ok"
        else:
            return None
    except Exception as e:
        print(f"Error !! {e}")
        return None
    finally:
        r.close()

