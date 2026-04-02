from flask import Blueprint,render_template,session,request

student_bp=Blueprint('student',__name__)

@student_bp.route('/')
def student_home():
    return "homepage of student"

@student_bp.route('/dashboard')
def dashboard():
    name=request.cookies.get('user')
    role=request.cookies.get('role')
    if role=="student":
        return render_template("student.html",name=name)
    if role=="admin":
        return redirect("/admin"),301
    return redirect("/auth/login"),301
