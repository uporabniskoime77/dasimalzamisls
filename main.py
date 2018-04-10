from string import ascii_lowercase
from random import randint

from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask import redirect

import baza

app = Flask(__name__)
app.secret_key = "akshfdgas"
ascii_crke = ascii_lowercase + "čžš"

@app.route("/")
def index():
    
    return render_template("domaca_stran.html")

@app.route("/logout")
def logout():
    session['user'] = None
    return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('user') is not None:
        return redirect('/')
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        session['user'] = baza.dobi_uporabnika(
            username=request.form['username'],
            password=request.form['password'])
        if session['user'] is None:
            return render_template("login.html", error="Napačni podatki")
        else:
            return redirect('/')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if session.get('user') is not None:
        return redirect('/')
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        if len(request.form['username']) < 3:
            return render_template("register.html", error="Prekratko ime")
        if baza.dobi_uporabnika(username=request.form['username']):
            return render_template("register.html", error="Uporabnik že obstaja")
        if len(request.form['password']) < 3:
            return render_template("register.html", error="Prekratko geslo")
        if request.form['password'] != request.form['password2']:
            return render_template("register.html", error="Gesli se ne ujemata")
        user_id = baza.vstavi_novega_uporabnika(
            username=request.form['username'],
            password=request.form['password'])
        session['user'] = baza.dobi_uporabnika(user_id)
        return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
