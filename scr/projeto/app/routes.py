
from flask import Blueprint, render_template, request, redirect, url_for  #blueprint organiza as rotas em modulos separados/render_template processa os arquivos html/request pega os dados do formulario/redirect: funcão que envia uma resposta ao navegador, redirecionando o usuario/url_for cria urls dinamicas 

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index(): #rotas que usam o método GET não precisam receber nenhum parametro na função - GET eh o metodo padrao que o flask assume quando nao ha especificacao
    return render_template('index.html')

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
@main_bp.route('/cliente_novo', methods=['POST'])
def cliente_novo():
    nome = request.form.get('cliente_nome')
    email = request.form.get('cliente_email')
    telefone = request.form.get('cliente_telefone')
    senha = request.form.get('cliente_senha')

# Rota para editar cliente
@main_bp.route('/cliente_editar', methods=['POST'])
def cliente_editar():
    client_id = request.form.get('client.id')
    nome = request.form.get('cliente_nome')
    email = request.form.get('cliente_email')
    telefone = request.form.get('cliente_telefone')
    senha = request.form.get('cliente_senha')

#Rota para excluir cliente
@main_bp.route('/cliente_excluir', methods=['POST'])
def cliente_excluir():
    cliente_id = request.form.get('cliente_id')

#Rota para listar cliente
@main_bp.route('listar_cliente', methods=['GET'])
def cliente_listar():
    client_id = request.form.get('cliente_id')


#O Blueprint (main_bp) é seu organizador de URLs. O comando @main_bp.route('/') é a regra que conecta um endereço web (a rota, como '/') a uma função Python (ex: def index():). 
#Quando um usuário acessa esse endereço, o Flask executa a função conectada. Essa função usa render_template para criar o HTML da página e o servidor Flask envia esse HTML de volta ao navegador do usuário.