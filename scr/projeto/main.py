from app import create_app, db
from app.models import Cliente 

app = create_app() #chava a a funcao que monta a aplicacao q ta em init.py

# Entra no contexto da aplicação para acessar configurações e extensões e c ria o banco de dados se nao estiver criado!
with app.app_context():   
    db.create_all() # Cria as tabelas no banco de dados ('meuapp.db') para todos os modelos que foram importados (ex: Cliente)

if __name__ == "__main__": #garante que o código só será executado se o arquivo for o principal
    app.run(debug=True)

