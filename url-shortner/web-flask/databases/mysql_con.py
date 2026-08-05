import mysql.connector
import time
def sec_db():
    print("wait for mysql")
    time.sleep(2)
    while True:
        try:
            con=mysql.connector.connect(
                    host='database',
                    user='root',
                    password='root',
                    database='mydb'
                    )
            print("successfully connected to mysql")
            return con
        except Exception as e:
            print(f"waiting for mysql")
            time.sleep(2)


