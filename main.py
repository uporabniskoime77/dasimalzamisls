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

@app.route("/druga_stran", methods=['GET', 'POST'])
def druga():
    if request.method == 'POST':
        session['user'] = baza.dobi_uporabnika(
            username=request.form['username'],
            password=request.form['password'])

    return render_template("druga_stran.html")

@app.route("/vislice/<znak>")
def ugibaj(znak):
    if len(znak) == 1 and znak.isalpha():
        session['ugibal'] += znak
        if znak not in session['beseda']:
            session['slika'] += 1
    for crka in session['beseda']:
        if crka not in session['ugibal']:
            break
    else:
        if session.get('user') is not None:
            baza.vstavi_novo_igro(session['user'][0], session['slika'], session['beseda'])
        return render_template('zmaga.html')

    return render_template("vislice.html", vse_crke=ascii_crke)

@app.route("/vislice")
def vislice():
    session['beseda'] = "endlessness"
    with open('besede.txt') as besede:
        for i in range(randint(1, 350747)):
            session['beseda'] = besede.readline().strip()
    session['slika'] = 0
    session['ugibal'] = ''
    return render_template("vislice.html", vse_crke=ascii_crke)

@app.route("/blog/<int:st_blog>")
def blog(st_blog):
    zadnji = request.cookies.get("blog_stevilka")
    result = render_template(
        "blog.html", stevilka=st_blog, prejsni=zadnji)
    result = make_response(result)
    result.set_cookie("blog_stevilka", str(st_blog))
    return result

@app.route("/lestvica")
def lestvica():
    najboljsi = baza.dobi_najboljse()
    return render_template("lestvica.html", najboljsi=najboljsi)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
