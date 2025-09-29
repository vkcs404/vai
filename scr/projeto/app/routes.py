
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
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
