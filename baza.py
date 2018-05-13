import os
from urllib import parse
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


def zakodiraj_geslo(password):
    """ Zakodira geslo in ga vrne """
    import hashlib, binascii
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000)
    return binascii.hexlify(dk).decode()


def ustvari_tabele(profes):
    """ Najprej izbriši in nato naredi tabele """
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    # Zbriši
    kazalec.execute("DROP TABLE IF EXISTS Citati")    
    kazalec.execute("DROP TABLE IF EXISTS Users CASCADE")
    kazalec.execute("DROP TABLE IF EXISTS Profs")

    # Naredi tabelo Users
    kazalec.execute("""CREATE TABLE Users (
                           id       BIGSERIAL PRIMARY KEY,
                           username VARCHAR(100) UNIQUE NOT NULL,
                           password VARCHAR(100) NOT NULL,
                           email    VARCHAR(100) UNIQUE
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
    for prof in profes:
        kazalec.execute("INSERT INTO Profs (ime) VALUES (%s)",(prof,))
    print("ustvarjam tabele")
    povezava.commit()
    kazalec.close()
    povezava.close()


def napolni_tabele():
    """ Ustvari nekaj uporabnikov in nekaj iger. """
    from random import randint
    print("tabele so filajo")
    for i in range(10):
        user_id = vstavi_novega_uporabnika("Uporabnik"+str(i))
        for j in range(10):
            vstavi_citat("sej ne veš", 2, user_id)


def vstavi_novega_uporabnika(username, password="123", email=None):
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute(
        "INSERT INTO Users (username, password, email) VALUES (%s, %s, %s) RETURNING id",
        (username, zakodiraj_geslo(password), email))
    nov_user_id = kazalec.fetchone()[0]
    povezava.commit()
    kazalec.close()
    povezava.close()
    return nov_user_id


def vstavi_citat(citat, prof_id, user_id):
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute("""INSERT INTO Citati (citat, prof_id, user_id)
                       VALUES (%s, %s, %s)""", (citat, prof_id, user_id))
    povezava.commit()
    kazalec.close()
    povezava.close()



def dobi_uporabnika(user_id=None, username=None, password=None, email=None):
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
    elif email is not None:
        kazalec.execute("SELECT * FROM Users WHERE email=%s", (email,))
    else:
        raise Exception("Napaka 'dobi_uporabnika': "
                        "Nimam dovolj podatkov, da bi našel uporabnika.")

    return kazalec.fetchone()


def dobi_citate(prof_id = None):
    print("pridem po citate")
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    if prof_id != None:
        citati = kazalec.execute("SELECT * FROM Citati WHERE id=%s", (prof_id,))
        profesor = kazalec.execute("SELECT * FROM Profs WHERE id=%s", (prof_id,))
        return citati, profesor
    else:
        citati = kazalec.execute("SELECT * FROM Citati")
        return kazalec.fetchmany(10)
        
def dobi_id(username):
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute("SELECT id FROM Users WHERE username=%s", (username,))

def profesorji():
    povezava = naredi_povezavo()
    kazalec = povezava.cursor()
    kazalec.execute("SELECT id, ime FROM Profs")
    return kazalec.fetchall()

