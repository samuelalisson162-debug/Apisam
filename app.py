import os
import secrets
import sqlite3
from functools import wraps

from flask import Flask, g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash


DATABASE = "api_login.db"

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    db.commit()


@app.before_request
def prepare_database():
    init_db()


@app.get("/")
def home():
    return jsonify(
        {
            "mensagem": "API online.",
            "rotas": ["/cadastro", "/login", "/perfil", "/logout"],
        }
    )


def get_logged_user():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "", 1).strip()
    db = get_db()
    user = db.execute(
        """
        SELECT users.id, users.name, users.email
        FROM tokens
        JOIN users ON users.id = tokens.user_id
        WHERE tokens.token = ?
        """,
        (token,),
    ).fetchone()

    return user


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user = get_logged_user()

        if user is None:
            return jsonify({"erro": "Voce precisa fazer login."}), 401

        g.user = user
        return route_function(*args, **kwargs)

    return wrapper


@app.post("/cadastro")
def cadastro():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"erro": "Informe name, email e password."}), 400

    if len(password) < 6:
        return jsonify({"erro": "A senha precisa ter pelo menos 6 caracteres."}), 400

    db = get_db()

    try:
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Este email ja esta cadastrado."}), 409

    return (
        jsonify(
            {
                "mensagem": "Usuario cadastrado com sucesso.",
                "usuario": {"id": cursor.lastrowid, "name": name, "email": email},
            }
        ),
        201,
    )


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"erro": "Informe email e password."}), 400

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"erro": "Email ou senha invalidos."}), 401

    token = secrets.token_hex(32)
    db.execute("INSERT INTO tokens (token, user_id) VALUES (?, ?)", (token, user["id"]))
    db.commit()

    return jsonify(
        {
            "mensagem": "Login feito com sucesso.",
            "token": token,
            "usuario": {"id": user["id"], "name": user["name"], "email": user["email"]},
        }
    )


@app.get("/perfil")
@login_required
def perfil():
    return jsonify(
        {
            "usuario": {
                "id": g.user["id"],
                "name": g.user["name"],
                "email": g.user["email"],
            }
        }
    )


@app.post("/logout")
@login_required
def logout():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "", 1).strip()

    db = get_db()
    db.execute("DELETE FROM tokens WHERE token = ?", (token,))
    db.commit()

    return jsonify({"mensagem": "Logout feito com sucesso."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
