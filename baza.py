import os
from urllib import parse
import psycopg2

DATABASE_URL = "postgres://postgres:asuna@localhost:5432/vislice"


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


def zakodiraj_geslo(password):
    """ Zakodira geslo in ga vrne """
    import hashlib, binascii
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000)
    return binascii.hexlify(dk).decode()


def ustvari_tabele():
    """ Najprej izbriši in nato naredi dve tabeli: Users in Scores. """
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()

    # Zbriši
    kazalec.execute("DROP TABLE IF EXISTS Scores")
    kazalec.execute("DROP TABLE IF EXISTS Users")

    # Naredi tabelo Users
    kazalec.execute("""CREATE TABLE Users (
                           id       SERIAL PRIMARY KEY,
                           username VARCHAR(100) UNIQUE NOT NULL,
                           password VARCHAR(100) NOT NULL
                       )""")
    # Naredi tabelo Scores
    kazalec.execute("""CREATE TABLE Scores (
                           id       SERIAL PRIMARY KEY,
                           user_id  INT,
                           napake   INT,
                           beseda   VARCHAR(100),
                           FOREIGN KEY (user_id) REFERENCES Users (id)
                       )""")
    povezava.commit()
    kazalec.close()
    povezava.close()


def napolni_tabele():
    """ Ustvari nekaj uporabnikov in nekaj iger. """
    from random import randint
    import uuid
    for i in range(10):
        user_id = vstavi_novega_uporabnika("Uporabnik"+str(i))
        for j in range(10):
            vstavi_novo_igro(user_id, randint(30, 100), str(uuid.uuid4()))


def vstavi_novega_uporabnika(username, password="123"):
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute(
        "INSERT INTO Users (username, password) VALUES (%s, %s) RETURNING id",
        (username, zakodiraj_geslo(password)))
    nov_user_id = kazalec.fetchone()[0]
    povezava.commit()
    kazalec.close()
    povezava.close()
    return nov_user_id


def vstavi_novo_igro(user_id, napake, beseda):
    """ Vstavi novo igro v tabelo Scores. """
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute("""INSERT INTO Scores (user_id, napake, beseda)
                       VALUES (%s, %s, %s)""", (user_id, napake, beseda))
    povezava.commit()
    kazalec.close()
    povezava.close()


def dobi_najboljse():
    """ Najdi 10 iger z najmanj napakami. """
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute("""
        SELECT Users.username, Scores.napake, Scores.beseda
        FROM Scores
        JOIN Users ON Scores.user_id=Users.id
        ORDER BY Scores.napake
        """)
    return kazalec.fetchmany(10)


def dobi_uporabnika(user_id=None, username=None, password=None):
    """ V bazi najde in vrne uporabnika (če osbstaja) """
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    if user_id is not None:
        kazalec.execute("SELECT * FROM Users WHERE id=%s", (user_id,))
    elif username is not None and password is not None:
        kazalec.execute("SELECT * FROM Users WHERE username=%s AND password=%s",
                        (username, zakodiraj_geslo(password)))
    elif username is not None:
        kazalec.execute("SELECT * FROM Users WHERE username=%s", (username,))
    else:
        raise Exception("Napaka 'dobi_uporabnika': "
                        "Nimam dovolj podatkov, da bi našel uporabnika.")

    return kazalec.fetchone()


if __name__ == "__main__":
    ustvari_tabele()
