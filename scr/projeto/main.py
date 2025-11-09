#É o arquivo que você executa para iniciar o servidor.
from app import create_app, db
from app.models import Cliente 

app = create_app()

# Cria o banco de dados se nao estiver criado!
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

