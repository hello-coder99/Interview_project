from flask import Blueprint,request,render_template,session,make_response
from db import register,login_by_username,login_by_email

auth_bp=Blueprint('auth',__name__)

@auth_bp.route('/register',methods=["GET","POST"])
def register_user():
    if request.method=="POST":
        data=request.form
        username=data["user"]
        email=data["email"]
        password=data["pass"]
        isadmin=data["isadmin"]
        register(username,email,password,isadmin)
        return "successfully summited"
    return render_template("register.html")

@auth_bp.route('/login',methods=["GET","POST"])
def login_user():
    if request.method=="POST":
        resp=make_response("http://localhost:5000/admin http://localhost:5000/student")
        cred=''
        data=request.form
        username=data["user"]
        email=data["email"]
        password=data["pass"]
        if username:
            cred=login_by_username(username,password)
            resp.set_cookie('user',
                            str(cred[0]),
                            max_age=60*60*24,
                            httponly=True,  
                            secure=False)
            resp.set_cookie('role',
                            str(cred[1]),
                            max_age=60*60*24,
                            httponly=True,
                            secure=False)
            return resp
        if email:
            cred=login_by_email(email,password)
            resp.set_cookie('user',
                            str(cred[0]),
                            max_age=60*60*24,
                            httponly=True,
                            secure=False)
            resp.set_cookie('role',
                            str(cred[1]),
                            max_age=60*60*24,
                            httponly=True,
                            secure=False)
            return resp
    return render_template("login.html")
@auth_bp.route('/logout',methods=["GET","POST"])
def logout():
    if request.method=="POST":
        value=request.form['logout']
        if value=="logout":
            resp=make_response("you are logout now")
            resp.delete_cookie('user')
            resp.delete_cookie('role')
            return resp
    return render_template("logout.html")


