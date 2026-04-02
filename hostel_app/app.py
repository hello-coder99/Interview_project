from flask import Flask,render_template
def create_app():
    global app
    app=Flask(__name__)
    app.config['SECRET_KEY']='secret123'
    #Import Blueprints
    from auth.routes import auth_bp
    from student.routes import student_bp
    from admin.routes import admin_bp

    #Register Blueprints
    app.register_blueprint(auth_bp,url_prefix='/auth')
    app.register_blueprint(admin_bp,url_prefix='/admin')
    app.register_blueprint(student_bp,url_prefix='/student')

    return app

app=create_app()
@app.route("/")
def home():
    return render_template("index.html")

if __name__=="__main__":
    #app=create_app()
    app.run(debug=True)

