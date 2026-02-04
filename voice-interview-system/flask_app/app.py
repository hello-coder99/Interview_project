from flask import Flask
from routes.interview import interview_bp
from routes.health import health_bp

app=Flask(__name__)

app.register_blueprint(health_bp)
app.register_blueprint(interview_bp,url_prefix="/interview")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
