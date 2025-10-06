
from flask import Blueprint, render_template, request, redirect, url_for, session, flash #blueprint organiza as rotas em modulos separados/render_template processa os arquivos html/request pega os dados do formulario/redirect: funcão que envia uma resposta ao navegador, redirecionando o usuario/url_for cria urls dinamicas 
from werkzeug.security import generate_password_hash, check_password_hash # pra criptografa a senha

from .models import Cliente # chamando o "cliente" do banco de dados
from . import db # trouxemos o banco de dados
main_bp = Blueprint('main', __name__) # Cria o Blueprint chamado 'main' para organizar as rotas

@main_bp.route('/') # O @main_bp indica ao Flask que esta rota pertence ao módulo 'main'
def index(): #rotas que usam o método GET não precisam receber nenhum parametro na função - GET eh o metodo padrao que o flask assume quando nao ha especificacao
    return render_template('index.html') # render_template: Envia a respectiva página para o usuário.

# Rota para cadastrar
@main_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

# Rota para logar
@main_bp.route('/login')
def login():
    return render_template('login.html')

# Rota para pagamente
@main_bp.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')

# Rota para scanear
@main_bp.route('/scaner')
def scaner():
    return render_template('scaner.html')

# Rota para ver os relatorios 
@main_bp.route('/relatorio')
def relatorio():
    return render_template('relatorio.html')


# CRUDE

# Rota do cliente novo
@main_bp.route('/cliente_novo', methods=['GET' ,'POST'])
def cliente_novo():
    if request.method == 'POST':
        nome = request.form.get('cliente_nome')
        email = request.form.get('cliente_email')
        senha = request.form.get('cliente_senha')
        
        #verifica se o email existe (Já esta cadastrado)
        email_existe = Cliente.query.filter_by(cliente_email=email).first() #se nao estiver cadastrado faz a query no BD

        if email_existe:
            return "Email já cadastrado"
        
        # criptografar a senha
        # biblioteca padrao do py para criptografar
        senha_criptografada = generate_password_hash(senha, method='pbkdf2:sha256')

        # instanciar o novo cliente # GUARDAMOS A SENHA COMO HASHED POIS TEMOS QUE GUARDALA CRIPTOGRAFADA, e nao a senha dele de fato
        #colocar no bd 
        novo_cliente = Cliente(
            cliente_nome=nome,
            cliente_email=email,
            cliente_senha=senha_criptografada
        )

        # salvamos no banco de dados com os seguintes comandos
        db.session.add(novo_cliente)
        db.session.commit()
        
        # se tude der certo manda pra pagina do scaner
        return redirect(url_for('main.scaner'))
    
    # se a pessoa tentar o metodo GET mantem na pagina de cadastro
    return render_template ('cadastro.html')



# Rota para cliente logar
@main_bp.route('/cliente_entrar', methods=['GET', 'POST'])
def cliente_entrar():
    if request.method == 'POST':
        email = request.form.get('cliente_email')
        senha = request.form.get('cliente_senha')

        #Procura o email do cliente no banco de dados
        cliente = Cliente.query.filter_by(cliente_email=email).first()

        #Ve se o usuario existe e se a senha é igual a do BD

        if cliente and check_password_hash(cliente.cliente_senha, senha):
            # Login bem-sucedido
            session['cliente_id'] = cliente.id # Guarda o ID do cliente na sessão
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.scaner'))
        else:
            # login falhou
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('main.cliente_entrar'))
    
    return render_template('login.html')


#cliente_editar
#cliente_excluir
#cliente_listar 
 
