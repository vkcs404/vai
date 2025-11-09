from flask import Flask ## Importa a classe Flask, essencial para criar a aplicação web.
from flask_sqlalchemy import SQLAlchemy  #Importa a extensão SQLAlchemy para gerenciar o banco de dados.



db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'PePeU'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meuapp.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        from.import routes
        app.register_blueprint(routes.main_bp) #Arrumei aq galera tava chamando so bp usamos em /routes main_bp! 
        return app
    
#é onde a instância principal do Flask é criada (app = Flask(__name__)), onde extensões (como SQLAlchemy) são inicializadas, e onde os Blueprints (rotas) são importados e registrados.
#Inicia o flask e configura o banco de dados.