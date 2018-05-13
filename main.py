from random import randint

from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask import session
from flask import redirect
from flask import url_for
from werkzeug.contrib.fixers import ProxyFix
import sys

import baza

from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.github import make_github_blueprint, github

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.secret_key = "akshfdgas"
google_blueprint = make_google_blueprint(
    client_id="61570463416-39jkgsv8h1bfkl7epvqebli5l1qbfvcj.apps.googleusercontent.com",
    client_secret="Sv4Yzbndtw4XVX7K9q-KRka8",
    scope=["profile", "email"]
)
facebook_blueprint = make_facebook_blueprint(
    client_id='215709269202041',
    client_secret='89d9c7120731e5a5822e743a5237aac0',
    scope=["public_profile", "email"],
)
github_blueprint = make_github_blueprint(
    client_id="d5bf5460b7584396c62c",
    client_secret="08f7317fa0e162c64cda8ae1f6ee22005adf900e",
)
twitter_blueprint = make_twitter_blueprint(
    api_key="xdrGzKtrIIOp9fJNlEHQgFm8K",
    api_secret="L9JAON7utiNOVKABfgr5iM6XQWmnAXMMB3KspyHZwDiFd9NAQK",
)
app.register_blueprint(google_blueprint, url_prefix="/login/google")
app.register_blueprint(twitter_blueprint, url_prefix="/login/twitter")
app.register_blueprint(facebook_blueprint, url_prefix="/login/facebook")
app.register_blueprint(github_blueprint, url_prefix="/login/github")

profesores = ('burek','kebab')

def out_login(email, username):
    if session.get('user') is not None:
        return redirect('/')
    elif email is not None:
        session['user'] = baza.dobi_uporabnika(email=email)
    else:
        raise Exception("Napaka 'dobi_uporabnika': "
                        "Nimam dovolj podatkov, da bi našel uporabnika.")
    if session['user'] is None:
        out_register(email=email, username=username)
    else:
        return redirect('/')

def out_register(email, username):
    if session.get('user') is not None:
        return redirect('/')
    elif email is not None:
        if baza.dobi_uporabnika(email=email):
            return render_template("register.html", error="Uporabnik že obstaja")
        user_id = baza.vstavi_novega_uporabnika(email=email, username=username)
        session['user'] = baza.dobi_uporabnika(user_id)
    return redirect('/')


@app.route("/", methods = ['GET', 'POST'])
def index():
    profs = baza.profesorji()
    if session.get('user') is not None:
        baza.vstavi_citat("citat", 2, 1)
        if request.method == 'POST':
            baza.vstavi_citat(citat=request.form['citat'], prof_id=request.form['profesor'], user_id=session['user'][0])
    return render_template("domaca_stran.html", profs=profs)
    
    
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

@app.route("/citati")
def citati():
    nekej = baza.dobi_citate()
    print(nekej)
    return render_template ("citati.html", nekej=nekej)

@app.route("/citati/<int:prof_id>")
def dobi_citate(prof_id):
    citati = baza.dobi_citate()[:-1]
    prof = baza.dobi_citate()[-1]
    return render_template("citati.html", citati=citati, prof=prof)

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

@app.route("/twitter")
def twitter_login():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/verify_credentials.json?include_email=true")
    assert resp.ok
    info = resp.json()
    return out_login(username=info["screen_name"], email=info["email"])

@app.route("/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    info = resp.json()
    return out_login(username=info["name"], email=info["email"])

@app.route("/github")
def github_login():
    if not github.authorized:
        return redirect(url_for("github.login"))
    resp = github.get("/user")
    assert resp.ok
    info = resp.json()
    return out_login(username=info["login"], email=info["email"])

@app.route("/facebook")
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))
    resp = facebook.get("me")
    assert resp.ok, resp.text
    info = resp.json()
    return out_login(username=info["name"], email=info["email"])

@app.before_first_request
def load():
    baza.ustvari_tabele(profesores)
    session['user'] = None

if __name__ == "__main__":
    app.run(host="0.0.0.0")
