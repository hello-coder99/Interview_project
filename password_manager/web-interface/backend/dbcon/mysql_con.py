import mysql.connector
from time import sleep
def sec_db():
    while True:
        try:
            con=mysql.connector.connect(
                    host='database',
                    user='root',
                    password='1234',
                    database='mydb'
                    )
            print("successfully connected to mysql")
            return con
        except Exception as e:
            print(f"waiting for mysql")
            sleep(2)
