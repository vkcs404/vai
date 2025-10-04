from flask import Flask
from flask_sqlalchemy import SQLAlchemy



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
    
