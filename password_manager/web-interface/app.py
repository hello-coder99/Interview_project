from flask import Flask,render_template,request,jsonify
from flask_cors import CORS
from time import sleep
import backend.database_op as database_op

app=Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/listed",methods=['GET','POST'])
def listed():
    if request.method=="POST":
        return jsonify({"status":database_op.get_names()})
    return jsonify({"status":"use json post request only"})

@app.route("/get_pass",methods=['GET','POST'])
def get_pass():
    if request.method=="POST":
        data=request.get_json()
        if data:
            name=data.get("name")
            return jsonify({"status":str(database_op.get_password(name))})
        return jsonify({"status":"no/invalid data requested"})
    return jsonify({"status":"use json post request on name parameter"})

@app.route("/store_pass",methods=['GET','POST'])
def store_pass():
    if request.method=="POST":
        data=request.get_json()
        if data:
            name=data.get("name")
            password=data.get("password")
            res=database_op.store_password(name,password)
            return jsonify({"status":res}),200
        return jsonify({"status":"invalid data found"})
    return jsonify({"status":"use json post request in json name,password object"})

@app.route("/delete_pass",methods=['GET','POST'])
def delete_pass():
    if request.method=="POST":
        data=request.get_json()
        if data:
            name=data.get("name")
            res=database_op.delete_password(name)
            return jsonify({"status":res}),200
        return jsonify({"status":"invalid data found"})
    return jsonify({"status":"use json post request on name parameter"})

if __name__=="__main__":
    print("waiting for connection.....")
    sleep(5)
    app.run(host='0.0.0.0',debug=True)
