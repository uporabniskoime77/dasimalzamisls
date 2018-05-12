import unittest
import main
import baza


class RegistracijaTestCase(unittest.TestCase):
    def setUp(self):
        main.app.testing = True
        if not baza.DATABASE_URL.endswith("_test"):
            baza.DATABASE_URL += "_test"
        baza.ustvari_tabele()
        self.app = main.app.test_client()

    def tearDown(self):
        main.app.testing = False

    def test_loading(self):
        response = self.app.get('/')
        assert response.status_code == 200

    def test_register(self):
        response = self.app.get('/register')
        assert response.status_code == 200
        assert b"Registriraj se!" in response.data

        response = self.app.post('/register', data={
            "username": "test",
            "password": "test",
            "password2": "netest"
        })
        assert response.status_code == 200
        assert b"Gesli se ne ujemata" in response.data

        response = self.app.post('/register', data={
            "username": "testUsername",
            "password": "test",
            "password2": "test"
        })
        assert response.status_code == 302

        response = self.app.get('/')
        assert response.status_code == 200
        assert b"testUsername" in response.data
        assert b"Odjava" in response.data

        user = baza.dobi_uporabnika(username="testUsername")
        assert user[1] == "testUsername"

        response = self.app.get('/logout')
        assert response.status_code == 302

        response = self.app.get('/')
        assert response.status_code == 200
        assert b"Prijava" in response.data

        response = self.app.post('/login', data={
            "username": "testUsername",
            "password": "test"
        })
        assert response.status_code == 302

        response = self.app.get('/')
        assert response.status_code == 200
        assert b"testUsername" in response.data
        assert b"Odjava" in response.data


unittest.main()