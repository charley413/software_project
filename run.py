from flask import Flask, redirect , url_for , session
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
import time
import math

app=Flask(__name__)
app.config["MONGO_URI"]="mongodb://localhost:27017/SOFRWARE_PROJECT"
app.config["SECRET_KEY"]="abcd"
mongo=PyMongo(app)


@app.template_filter("format")
def format(value):
    if value is None:
        return""

    nowtime=time.time()
    offset=datetime.fromtimestamp(nowtime)-datetime.utcfromtimestamp(nowtime)
    value=datetime.fromtimestamp((int(value)/1000))+offset
    return value.strftime('%Y-%m-%d %H:%M')
@app.route("/")
def base():
    return render_template("base.html")


@app.route("/list")
def list():
    
    

    board = mongo.db.board
    datas=board.find({}).sort("pubdate",-1)
    return render_template("list.html",datas=datas )

@app.route("/view/<idx>")
def board_view(idx):
    if session.get("login_id") is None : 
        return redirect(url_for("login"))
    if idx is not None:
        board = mongo.db.board
        data=board.find_one({"_id":ObjectId(idx)})

        if data is not None:
            result={
                "id":data.get("_id"),
                "title":data.get("title"),
                "contents":data.get("contents"),
                "pubdate":data.get("pubdate")
                
            }
            return render_template("view.html",result=result)
    return abort(404)


@app.route("/write",methods=["GET","POST"])
def board_write():
    if session.get("login_id") is None : 
        return redirect(url_for("login"))
    if request.method=="POST":
        title=request.form.get("title")
        contents=request.form.get("contents")
        current_utc_time = round(datetime.utcnow().timestamp()*1000)

        board=mongo.db.board
        post={
            "title":title,
            "contents":contents,
            "pubdate":current_utc_time
        }
        x=board.insert_one(post)
        print(x.inserted_id)

        return redirect(url_for("board_view", idx=x.inserted_id))
    else:
        return render_template("write.html")

@app.route("/join",methods=["GET","POST"])
def member_join():
    if request.method=="POST":
        name = request.form.get("name",type=str)
        login_id=request.form.get("login_id",type=str)
        password=request.form.get("password",type=str)
        members=mongo.db.members
        post = {
        "name":name,
        "login_id":login_id,
        "password":password
        } 
        members.insert_one(post)
    
        return redirect(url_for("login"))
    else :
        return render_template("join.html")

   
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        login_id=request.form.get("login_id")
        password=request.form.get("password")

        members=mongo.db.members
        data=members.find_one({"login_id":login_id})

        if data is None:
            return redirect(url_for("login"))
        else:
            if data.get("password")==password:
                session["login_id"]=login_id
                session["name"]=data.get("name")
                session["id"]=str(data.get("_id"))
                return redirect(url_for("list"))
            else:
                return redirect(url_for("login"))

        return""
    else:
        return render_template("login.html")

@app.route("/edit/<idx>",methods=["GET","POST"])
def board_edit(idx):
    if session.get("login_id") is None : 
        return redirect(url_for("login"))
    if request.method=="GET":
        board=mongo.db.board
        data=board.find_one({"_id": ObjectId(idx)})
       
        return render_template("edit.html", data=data)
    else:
        title=request.form.get("title")
        contents=request.form.get("contents")
        board=mongo.db.board
        data=board.find_one({"_id": ObjectId(idx)})
        board.update_one({"_id":ObjectId(idx)},{
            "$set":{
                    "title":title,
                    "contents":contents,
                }})
        return redirect(url_for("board_view",idx=idx))

@app.route("/delete/<idx>",methods=["GET","POST"])
def board_delete(idx):
    board=mongo.db.board
    data=board.find_one({"_id": ObjectId(idx)})
    board.delete_one({"_id":ObjectId(idx)})
    return redirect(url_for("list"))


if __name__=='__main__':
    app.run(debug=True)