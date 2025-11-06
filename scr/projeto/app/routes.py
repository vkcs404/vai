from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Cliente, RelatorioBasico, RelatorioIntermediario, RelatorioAvancado
from . import db
from .ferramentas.scanner_avancado import rodar_scan_avancado
main_bp = Blueprint('main', __name__)

# ... (todas as suas outras rotas como index, cadastro, etc. continuam iguais) ...
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@main_bp.route('/login')
def login():
    return render_template('login.html')

@main_bp.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')

@main_bp.route('/scaner')
def scaner():
    # Proteger esta rota: se o usuário não estiver logado, redireciona para o login.
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    return render_template('scaner.html')

# ... (outras rotas simples) ...

# Rota do cliente novo (nenhuma mudança necessária aqui, o status 'ativo' será definido por padrão)
@main_bp.route('/cliente_novo', methods=['GET' ,'POST'])
def cliente_novo():
    if request.method == 'POST':
        nome = request.form.get('cliente_nome')
        email = request.form.get('cliente_email')
        senha = request.form.get('cliente_senha')
        
        email_existe = Cliente.query.filter_by(cliente_email=email).first()

        if email_existe:
            flash("Email já cadastrado.", "danger")
            return redirect(url_for('main.cadastro'))
        
        senha_criptografada = generate_password_hash(senha, method='pbkdf2:sha256')

        novo_cliente = Cliente(
            cliente_nome=nome,
            cliente_email=email,
            cliente_senha=senha_criptografada
            # O campo 'cliente_status' será 'ativo' por padrão, conforme definido no models.py
        )

        db.session.add(novo_cliente)
        db.session.commit()
        
        flash("Cadastro realizado com sucesso! Faça o login.", "success")
        return redirect(url_for('main.login'))
    
    return render_template ('cadastro.html')


# Rota para cliente logar (MODIFICADA)
@main_bp.route('/cliente_entrar', methods=['GET', 'POST'])
def cliente_entrar():
    if request.method == 'POST':
        email = request.form.get('cliente_email')
        senha = request.form.get('cliente_senha')

        cliente = Cliente.query.filter_by(cliente_email=email).first()

        # --- LÓGICA DE STATUS ADICIONADA AQUI ---
        # 1. Verifica se o cliente existe
        if not cliente:
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('main.login'))

        # 2. VERIFICA SE O CLIENTE ESTÁ ATIVO (Se desativado n pode entrar)
        if cliente.cliente_status != 'ativo':
            flash('Este usuário está desativado e não pode entrar.', 'danger')
            return redirect(url_for('main.login'))

        # 3. Se estiver ativo, verifica a senha
        if check_password_hash(cliente.cliente_senha, senha):
            session['cliente_id'] = cliente.id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main.scaner'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('main.login'))
    
    return render_template('login.html')

@main_bp.route('/admin/alternar_status/<int:cliente_id>', methods=['POST'])
def alternar_status(cliente_id):
 

    cliente = Cliente.query.get_or_404(cliente_id)

    # Lógica para alternar o status
    if cliente.cliente_status == 'ativo':
        cliente.cliente_status = 'inativo'
        flash(f'Cliente {cliente.cliente_nome} foi desativado.', 'success')
    else:
        cliente.cliente_status = 'ativo'
        flash(f'Cliente {cliente.cliente_nome} foi ativado.', 'success')
    
    db.session.commit()
    
    # Redireciona de volta para a página de onde o admin veio (ex: uma lista de clientes)
    return redirect(url_for('main.listar_clientes')) # Supondo que você crie uma rota '/listar_clientes'


# Exemplo de uma rota para listar clientes (para o admin usar)
@main_bp.route('/listar_clientes')
def listar_clientes():
    # Lógica de segurança para garantir que só admins vejam isso
    clientes = Cliente.query.all()
    return render_template('listar_clientes.html', clientes=clientes)
    




@main_bp.route('/scaner')
def scaner():
    # Proteger esta rota: se o usuário não estiver logado, redireciona para o login.
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    # Passa o cliente inteiro para o template
    cliente = Cliente.query.get(session['cliente_id'])
    
    # O template 'scaner.html' agora terá acesso ao 'cliente.nivel_acesso'
    return render_template('scaner.html', cliente=cliente)


# --- ROTA POST para SCAN AVANÇADO (Sua ideia) ---
@main_bp.route('/executar_scanner_avancado', methods=['POST'])
def executar_scanner_avancado():
    
    # --- Passo 1: Checar Login ---
    if 'cliente_id' not in session:
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    # --- Passo 2: Checar Permissão (Segurança) ---
    cliente = Cliente.query.get(session['cliente_id'])
    if cliente.nivel_acesso != 'avancado':
        flash('Permissão negada. Você não tem acesso ao scanner avançado.', 'danger')
        return redirect(url_for('main.scaner'))

    # --- Passo 3: Executar e Salvar ---
    alvo = request.form.get('alvo')
    if not alvo:
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        # Chama a função do seu arquivo .py
        conteudo_do_relatorio = rodar_scan_avancado(alvo)

        # Salva no modelo CORRETO (RelatorioAvancado)
        novo_relatorio = RelatorioAvancado(
            conteudo_tecnico=conteudo_do_relatorio,
            cliente_id=cliente.id
        )
        
        db.session.add(novo_relatorio)
        db.session.commit()
        
        flash('Scan avançado concluído e relatório salvo!', 'success')

    except Exception as e:
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger')

    return redirect(url_for('main.scaner'))


# --- ROTA POST para SCAN INTERMEDIÁRIO