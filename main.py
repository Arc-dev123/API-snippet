from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS

import string
import random

import sqlite3

app = Flask(__name__)
CORS(app)
API = Api(app)

conn = sqlite3.connect("main")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS account (
            user_id INT PRIMARY KEY,
            fname TEXT,
            lname TEXT,
            email TEXT,
            pwd TEXT
)""")

cur.execute("""CREATE TABLE IF NOT EXISTS token (
            user_id TEXT,
            token TEXT
)""")

conn.commit()
cur.close()
conn.close()

class Register(Resource):
    def post(self):
        token_words = string.printable

        data = request.get_json()
        fname = data.get("fname")
        lname = data.get("lname")
        email = data.get("email")
        pwd = data.get('pwd')
        cpwd = data.get('cpwd')

        conn = sqlite3.connect("main")
        cur = conn.cursor()

        if not (fname and lname and email and pwd and cpwd):
            return {"data": "Lack of data"}, 404

        if not pwd == cpwd:
            return {"data": "Confirm password and password do not match"}, 404

        cur.execute("SELECT * FROM account WHERE email = ?", (email,))
        if cur.fetchone():
            return {"data": "This email already exists"}, 404

        cur.execute("INSERT INTO account (fname, lname, email, pwd) VALUES (?, ?, ?, ?)", (fname, lname, email, pwd,))

        cur.execute("SELECT user_id FROM account WHERE email = ?", (email,))

        user_id = cur.fetchone()[0]

        token = ""

        for i in range(0, 29):
            token = token + random.choice(token_words)

        cur.execute("INSERT INTO token (user_id, token) VALUES (?, ?)", (user_id, token,))

        conn.commit()

        cur.close()
        conn.close()

        return {"data": "Success"}, 200

class Login(Resource):
    def get(self):
        token_words = string.printable

        data = request.get_json()
        email = data.get("email")
        pwd = data.get("pwd")

        conn = sqlite3.connect("main")
        cur = conn.cursor()

        if not (email and pwd):
            return {"data": "Lack of data"}, 404

        cur.execute("SELECT * FROM account WHERE email = ?", (email,))
        existence = cur.fetchone()

        if not existence:
            return {"data": "This email does not exists"}, 404

        cur.execute("SELECT pwd FROM account WHERE email = ?", (email,))
        dbpwd = cur.fetchone()[0]

        if not (dbpwd == pwd):
            return {"data": "Password does not match"}, 404

        token = ""

        for i in range(0, 29):
            token = token + random.choice(token_words)

        cur.execute("SELECT user_id FROM account WHERE email = ?", (email,))

        user_id = cur.fetchone()[0]

        cur.execute("UPDATE token SET token = ? WHERE user_id = ?", (token, user_id,))

        conn.commit()

        cur.close()
        conn.close()

        return {"token": token}, 200

API.add_resource(Register, "/register")

API.add_resource(Login, "/login")

if __name__ == "__main__":
    app.run(debug=True)
