from flask import Blueprint,render_template,request,redirect,jsonify
from db import get_user_info
admin_bp=Blueprint('admin',__name__)

@admin_bp.route('/')
def home_admin():
    return "homepage of admin"

@admin_bp.route('/dashboard')
def dashboard():
    name=request.cookies.get('user')
    role=request.cookies.get('role')
    if role=="admin":
        return render_template("admin.html",name=name)
    if role=="student":
        return redirect("/student"),301
    return redirect("/auth/login"),301

@admin_bp.route('/get_info',methods=["GET","POST"])
def get_info():
    name=request.cookies.get('user')
    role=request.cookies.get('role')
    if role=='admin':
        if request.method=="POST":
            username=request.json['username']
            userrole=request.json['userrole']
            result=get_user_info(username,userrole)
            return jsonify({"id":str(result[0]),
                            "user":str(result[1]),
                            "email":str(result[2]),
                            "role":str(result[3])})
            #return render_template("check.html",userid=result[0],username=result[1],email=result[2],role=result[3])
        return render_template("get_user.html")
    return "NOT AUTHORIZED",403
            

