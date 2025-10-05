from . import db

class Cliente(db.Model): #Criacao da classe cliente no banco
    id = db.Column(db.Integer, primary_key=True) # Cada usuario tera um id unico
    cliente_nome = db.Column(db.String(80), nullable=False) # Nao pode estar vazio
    cliente_email = db.Column(db.String(320), unique=True, nullable=False)  #unique = nao pode haver emails repetidos/+ de uma conta com mesmo email
    cliente_senha = db.Column(db.String(128)) 
    #80, 320 e 128 sao os padroes de caracteres por string nos respectivos campos