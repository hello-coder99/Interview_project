from flask import Flask

from routes.health import health_bp

app=Flask(__name__)

app.register_blueprint(health_bp)

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
