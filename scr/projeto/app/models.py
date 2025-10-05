from . import db

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Cada usuario tera um id unico
    cliente_nome = db.Column(db.String(80), nullable=False) # Nao pode estar vazio
    cliente_email = db.Column(db.String(320), unique=True, nullable=False)
    cliente_senha = db.Column(db.String(128))

