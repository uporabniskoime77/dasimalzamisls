from flask import Flask
from urllib import parse
import os
import psycopg2

DATABASE_URL = "postgres://lukapersolja:Ursa2017@localhost:5432/test"


def naredi_povezavo():
    """ Naredi in vrne povezavo do baze podatkov """
    parse.uses_netloc.append("postgres")
    url = parse.urlparse(os.environ.get("DATABASE_URL", DATABASE_URL))
    return psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
def ustvari_tabele():
    """ Najprej izbriši in nato naredi tabele """
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    print("ustvarjam tabele")
    # Zbriši
    kazalec.execute("DROP TABLE IF EXISTS Citati")    
    kazalec.execute("DROP TABLE IF EXISTS Users CASCADE")
    kazalec.execute("DROP TABLE IF EXISTS Profs")

    # Naredi tabelo Users
    kazalec.execute("""CREATE TABLE Users (
                           id       SERIAL PRIMARY KEY,
                           username VARCHAR(100) UNIQUE NOT NULL,
                           password VARCHAR(100) NOT NULL,
                           email    VARCHAR(100) UNIQUE,
                           go_id    INT UNIQUE,
                           gi_id    INT UNIQUE,
                           fb_id    INT UNIQUE,
                           tw_id    INT UNIQUE
                        )""")
    kazalec.execute("""CREATE TABLE Profs (
                           id       SERIAL PRIMARY KEY,
                           ime      VARCHAR(100) NOT NULL
                       )""")

    kazalec.execute("""CREATE TABLE Citati (
                           id       SERIAL PRIMARY KEY,
                           citat    VARCHAR(300) NOT NULL,
                            prof_id INT REFERENCES Profs (id),
                            user_id INT REFERENCES Users (id)
                       )""")
    povezava.commit()
    kazalec.close()
    povezava.close()

def profesorji(prof):
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    for profes in prof:
        kazalec.execute("INSERT INTO Profs (ime) VALUES (%s)",(profes,))
    kazalec.execute("SELECT id, ime FROM Profs")
    return kazalec.fetchall()

app = Flask(__name__)
profesores = ('burek','kebab')

@app.route("/", methods = ['GET', 'POST'])
def index():
    ustvari_tabele()
    profs = profesorji(profesores)
    # if session.get('user') is not None:
    #     if request.method == 'POST':
    #         baza.vstavi_citat(citat=request.form['citat'], prof_id=request.form['profesor'], user_id=baza.dobi_id(session['user'][0]))
    print(profs)
    return '{}'.format(profs[0][0])

if __name__ == "__main__":
    app.run(host="0.0.0.0")