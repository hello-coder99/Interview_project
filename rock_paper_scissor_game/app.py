from flask import Flask,request,render_template,jsonify
from random import choice
app=Flask(__name__)
data=["rock","paper","scissor"]
default="default"
def decision(me,comp):
    if me=="rock":
        if comp=="rock":
            return "Draw"
        if comp=="paper":
            return "Computer wins"
        if comp=="scissor":
            return "You win"
    elif me=="paper":
        if comp=="rock":
            return "You win"
        if comp=="paper":
            return "Draw"
        if comp=="scissor":
            return "Computer wins"
    elif me=="scissor":
        if comp=="rock":
            return "Computer wins"
        if comp=="paper":
            return "You win"
        if comp=="scissor":
            return "Draw"
    return "no result"

@app.route("/",methods=["GET","POST"])
def home():
    result="no result"
    if request.method=="POST":
        comp_choice=choice(data)
        my_choice=request.json.get('choice')
        result=decision(my_choice,comp_choice)
        img1=f"./static/images/{my_choice}.jpg"
        img2=f"./static/images/{comp_choice}.jpg"
        return jsonify({"img1":img1,"img2":img2,"result":result}) 
    return render_template("index.html")

app.run()

