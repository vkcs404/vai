from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#configura a instância (objeto que encapsula todas as funcionalidades da sua aplicação Flask) principal do Flask e inicializa o o banco de dados.

#chama o banco de dados

db = SQLAlchemy()

def create_app(): #monta a aplicação

    app = Flask(__name__) #inicia a aplicacao
    
    app.config['SECRET_KEY'] = 'PePeU' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meuapp.db' # Define o caminho para o banco de dados SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desabilita o rastreamento de modificações para economizar memória
    db.init_app(app) # Conecta o objeto db com as configurações da instância 'app'

    with app.app_context():  # Inicia um contexto de aplicação para garantir que as extensões funcionem
        from.import routes #importa as rotas
        app.register_blueprint(routes.main_bp) #Arrumei aq galera tava chamando so bp usamos em /routes main_bp! / Registra o Blueprint que contém todas as rotas da aplicação
        return app
    
