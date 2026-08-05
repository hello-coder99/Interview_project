import backend.dbcon.mysql_con as mysql_con

def get_sdata(name):
    connection=None
    cursor=None
    try:
        connection=mysql_con.sec_db()
        cursor=connection.cursor()
        sql="SELECT Password from password_hub where Pname=%s"
        values=(name,)
        cursor.execute(sql,values)
        result=cursor.fetchone()
        if result:
            print("returned from mysql ")
            return result[0]
        return None
    except Exception as e:
        print(f"Error : {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def get_all_names():
    connection=None
    cursor=None
    try:
        connection=mysql_con.sec_db()
        cursor=connection.cursor()
        sql="SELECT Pname from password_hub"
        cursor.execute(sql)
        result=cursor.fetchall()
        if result:
            return result
        return None
    except Exception as e:
        print(f"Error !! {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def set_sdata(name,password):
    connection=None
    cursor=None
    try:
        connection=mysql_con.sec_db()
        cursor=connection.cursor()
        sql="INSERT INTO password_hub (Pname,Password) VALUES (%s,%s)"
        values=(name,password)
        cursor.execute(sql,values)
        connection.commit()
        return "ok"
    except Exception as e:
        print(f"Error !! {e}")
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()

def delete_sdata(name):
    connection = None
    cursor = None
    try:
        connection = mysql_con.sec_db()
        cursor = connection.cursor()
        
        sql = "DELETE FROM password_hub WHERE Pname = %s"
        values = (name,)
        cursor.execute(sql, values)
        
        # Optional: Check if anything was actually deleted
        if cursor.rowcount == 0:
            return None
            
        connection.commit()
        return "ok"
        
    except Exception as e:
        print(f"Error !! {e}")
        return None
        
    finally:
        # Safely close only if they were successfully initialized
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
