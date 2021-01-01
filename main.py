"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, render_template, redirect, request, url_for, send_from_directory, jsonify
#from HackDuke import app
import sqlite3 as sql
from sqlite import removeUser
import os
from werkzeug.utils import  secure_filename

validated = False
info = ""
cred = ""

app = Flask(__name__)


@app.route("/registration", methods=["POST", "GET"])
def submit_page():
    global validated
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["pwd"]
        name = request.form["name"]
        file = request.files['profilePic']
        path = secure_filename(file.filename)
        if not path:
            path = 'person.png'
        full_path = app.instance_path.rstrip("instance") + "static\\" + path
        file.save(full_path)
        #path.save(os.path.join(app.instance_path), "upload", secure_filename(path.filename))
        #dob = request.form["dob"]
        #diagnosis = request.form["diagnosis"]
        #purpose = request.form.getlist("purpose")
        #contact = request.form.getlist("contact")
        #upload = request.files['profilePic']
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users (email, pwd, name, path) VALUES (?,?,?, ?)",(email, pwd, name, full_path))
            con.commit()
        print(full_path)
        return redirect("http://127.0.0.1:5000/login")
    return render_template("registration.html")

@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from users")

    rows = cur.fetchall();
    return render_template("list.html",rows = rows)


@app.route("/match", methods=["POST", "GET"])
def match_page():
    if validated:
        return render_template("match.html")
    return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
def login_page():
    global cred
    global validated
    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]
        with sql.connect("database.db") as con:
           cur = con.cursor()
           cur.execute("""SELECT email ,pwd FROM users WHERE email=? AND pwd=?""",
                (email, pwd))
           con.commit()
        result = cur.fetchone()
        if result:
            cred = email
            validated = True
            return profile_page()
        else:
            return render_template("login_fail.html")
    return render_template("login.html")

@app.route("/",methods=['GET', 'POST'])
def home_page():
    if validated:
        return render_template("home_loggedin.html")
    return render_template("home.html")

@app.route("/logout",methods=['GET','POST'])
def logout():
    global validated
    validated = False
    return render_template("home.html")

@app.route("/media",methods=['GET', 'POST'])
def media_page():
    if validated:
        return render_template("media.html")
    return render_template("login.html")

@app.route("/profile",methods=['GET', 'POST'])
def profile_page():
    global info
    with sql.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT path, name FROM users WHERE email=(?) ", [cred])
        con.commit()
    result = cur.fetchone()
    output = []
    output.append('..' + result[0][result[0].find('HackDukeApp')+11:].replace('\\','/'))
    output.append(result[1])
    info = output
    return render_template("profile.html", output=output)

@app.route("/delete/<name>",methods=['GET'])
def delete_user(name):
    removeUser(name)
    return name + ' will be removed from the table'


@app.route("/chat", methods=['GET'])
def chat_page():
    return render_template("chat.html",output=info)

if __name__ == "__main__":
    app.run(debug=True)
