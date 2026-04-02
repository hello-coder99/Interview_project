from dotenv import load_dotenv
import os
import mysql.connector 
load_dotenv()
def conn():
    try:
        connection=mysql.connector.connect(
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                database=os.getenv("DATABASE")
                )
        l=list()
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        exit(1)
def register(username,email,password,isadmin):
    connection=conn()
    cursor=connection.cursor()
    """username=input("Enter the username:")
    email=input("Enter the email :")
    password=input("Enter the password:")
    isadmin=input("Are you admin ?Y/N:")"""
    if isadmin.upper()=='Y':
        sql = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
        values = (username, email, password, "admin")
    else:
        sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        values = (username, email, password)
    cursor.execute(sql,values)
    connection.commit()
    cursor.close()
    connection.close()

def login_by_username(username,password):
    connection=conn()
    cursor=connection.cursor()
    sql="SELECT username,role FROM users WHERE username=%s AND password=%s"
    values=(username,password)
    cursor.execute(sql,values)
    result=cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return result
    return None
def login_by_email(email,password):
    connection=conn()
    cursor=connection.cursor()
    sql="SELECT username,role FROM users WHERE email=%s AND password=%s"
    values=(email,password)
    cursor.execute(sql,values)
    result=cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return result
    return None

def get_user_info(username,role):
    connection=conn()
    cursor=connection.cursor()
    sql="SELECT id,username,email,role FROM users WHERE username=%s AND role=%s"
    values=(username,role)
    cursor.execute(sql,values)
    result=cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return result
    return None
