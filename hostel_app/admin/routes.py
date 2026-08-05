from flask import Blueprint,render_template,request,redirect,jsonify
from db import get_user_info,update_profile,delete_user
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
            return jsonify({"id":result[0],
                            "user":result[1],
                            "email":result[2],
                            "role":result[3]})
        return render_template("get_user.html")
    return "NOT AUTHORIZED",403

@admin_bp.route('/update-profile',methods=["POST"])
def updateProfile():
    userid=request.cookies.get('user')
    role=request.cookies.get('role')
    if role=='admin':
        update_id=request.json['userid']
        email=request.json['email']
        res=update_profile(update_id,email)
        return jsonify({"statu":res})
    return jsonify({"statu":"not_authorized"})

@admin_bp.route('/delete-profile',methods=["POST"])
def deleteProfile():
    userid=request.cookies.get('user')
    role=request.cookies.get('role')
    if role=='admin':
        delete_id=request.json['delete_id']
        res=delete_user(delete_id)
        return jsonify({"statu":res})
    return jsonify({"statu":"not_authorized"})

