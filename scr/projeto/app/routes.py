from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Cliente, RelatorioBasico, RelatorioIntermediario, RelatorioAvancado
from . import db
from .ferramentas.scanner_avancado import rodar_scan_avancado
from .ferramentas.scanner_intermediario import rodar_scan_intermediario
from .ferramentas.scanner_basico import rodar_scan_basico
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

@main_bp.route('/escolher_relatorio')
def escolher_relatorio():
    return render_template('escolher_relatorio.html')

@main_bp.route('/selecionar_relatorio', methods=['POST'])
def selecionar_relatorio():
    tipo_relatorio = request.form.get('tipo_relatorio')
    if tipo_relatorio in ['basico', 'intermediario', 'avancado']:
        session['tipo_relatorio'] = tipo_relatorio
        # Definir preços e descrições
        precos = {
            'basico': '10,00',
            'intermediario': '15,00',
            'avancado': '20,00'
        }
        descricoes = {
            'basico': 'Indicado para pessoas com pouco conhecimento técnico em cibersegurança que desejam verificar se o site da empresa está seguro.',
            'intermediario': 'Ideal para desenvolvedores que querem garantir que seus sites estejam protegidos, com um relatório que aponta falhas de segurança que devem ser mitigadas.',
            'avancado': 'Voltado para usuários mais experientes que desejam automatizar a detecção de falhas de segurança e receber um relatório detalhado sobre a segurança do site.'
        }
        session['preco_relatorio'] = precos[tipo_relatorio]
        session['descricao_relatorio'] = descricoes[tipo_relatorio]
        
        # Check if user is logged in
        if 'cliente_id' in session:
            # User is logged in, go to payment
            return redirect(url_for('main.pagamento'))
        else:
            # User not logged in, redirect to login
            flash('Por favor, faça login ou cadastre-se para continuar.', 'info')
            return redirect(url_for('main.login'))
    else:
        flash('Opção de relatório inválida.', 'danger')
        return redirect(url_for('main.escolher_relatorio'))

@main_bp.route('/pagamento')
def pagamento():
    # Check if user is logged in
    if 'cliente_id' not in session:
        flash('Por favor, faça login para continuar com o pagamento.', 'warning')
        return redirect(url_for('main.login'))
    
    # Obter relatório selecionado da sessão
    tipo_relatorio = session.get('tipo_relatorio', None)
    preco_relatorio = session.get('preco_relatorio', None)
    
    if not tipo_relatorio:
        flash('Por favor, selecione um tipo de relatório primeiro.', 'warning')
        return redirect(url_for('main.escolher_relatorio'))
    
    return render_template('pagamento.html', tipo_relatorio=tipo_relatorio, preco_relatorio=preco_relatorio)

@main_bp.route('/confirmar_pagamento', methods=['POST'])
def confirmar_pagamento():
    # Mark payment as confirmed in session
    session['pagamento_confirmado'] = True
    flash('Pagamento confirmado com sucesso!', 'success')
    return redirect(url_for('main.scaner'))


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
            
            # Check if there's a pending report selection
            if 'tipo_relatorio' in session and not session.get('pagamento_confirmado'):
                # Redirect to payment
                return redirect(url_for('main.pagamento'))
            else:
                # Redirect to scanner
                return redirect(url_for('main.scaner'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('main.login'))
    
    return render_template('login.html')

@main_bp.route('/admin/alternar_status/<int:cliente_id>', methods=['POST'])
def alternar_status(cliente_id):
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))

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
    return redirect(url_for('main.listar_clientes'))


@main_bp.route('/scaner')
def scaner():
    # Proteger esta rota: se o usuário não estiver logado, redireciona para o login.
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    # Passa o cliente inteiro para o template
    cliente = Cliente.query.get(session['cliente_id'])
    
    # Get report information from session
    tipo_relatorio = session.get('tipo_relatorio', None)
    preco_relatorio = session.get('preco_relatorio', None)
    descricao_relatorio = session.get('descricao_relatorio', None)
    
    # O template 'scaner.html' agora terá acesso ao 'cliente.nivel_acesso' e report info
    return render_template('scaner.html', 
                         cliente=cliente,
                         tipo_relatorio=tipo_relatorio,
                         preco_relatorio=preco_relatorio,
                         descricao_relatorio=descricao_relatorio)


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

@main_bp.route('/executar_scanner_intermediario', methods=['POST'])
def executar_scanner_intermediario():
    
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

#routa basica#
@main_bp.route('/executar_scanner_basico', methods=['POST'])
def executar_scanner_basico():
    
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


    # Rota para Alterar o Nível de Acesso do Cliente
@main_bp.route('/admin/alterar_nivel/<int:cliente_id>', methods=['POST'])
def alterar_nivel_acesso(cliente_id):
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))

    cliente_alvo = Cliente.query.get_or_404(cliente_id)
    novo_nivel = request.form.get('novo_nivel')
    
    # Lista de níveis válidos para evitar injeção de dados
    niveis_validos = ['basico', 'intermediario', 'avancado']

    if novo_nivel and novo_nivel in niveis_validos:
        # Altera o nível do cliente no banco de dados
        cliente_alvo.nivel_acesso = novo_nivel
        db.session.commit()
        
        flash(f'O nível de acesso de {cliente_alvo.cliente_nome} foi alterado para {novo_nivel.title()}.', 'success')
    else:
        flash('Nível de acesso inválido.', 'danger')
    
    # Redireciona de volta para a lista de clientes ou para onde você precisar
    return redirect(url_for('main.listar_clientes'))


# ######################################################################
# NOVAS ROTAS ADICIONADAS
# ######################################################################

# Rota para visualizar relatórios recentes
@main_bp.route('/relatorios_recentes')
def relatorios_recentes():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id'])
    
    # Buscar todos os relatórios do cliente dos últimos 30 dias
    from datetime import datetime, timedelta
    data_limite = datetime.utcnow() - timedelta(days=30)
    
    # Combinar todos os tipos de relatórios
    relatorios = []
    
    # Relatórios Básicos
    basicos = RelatorioBasico.query.filter(
        RelatorioBasico.cliente_id == cliente.id,
        RelatorioBasico.data_criacao >= data_limite
    ).all()
    for rel in basicos:
        relatorios.append({
            'id': rel.id,
            'tipo': 'basico',
            'data_criacao': rel.data_criacao,
            'alvo': None  # Adicionar se tiver campo alvo
        })
    
    # Relatórios Intermediários
    intermediarios = RelatorioIntermediario.query.filter(
        RelatorioIntermediario.cliente_id == cliente.id,
        RelatorioIntermediario.data_criacao >= data_limite
    ).all()
    for rel in intermediarios:
        relatorios.append({
            'id': rel.id,
            'tipo': 'intermediario',
            'data_criacao': rel.data_criacao,
            'alvo': None
        })
    
    # Relatórios Avançados
    avancados = RelatorioAvancado.query.filter(
        RelatorioAvancado.cliente_id == cliente.id,
        RelatorioAvancado.data_criacao >= data_limite
    ).all()
    for rel in avancados:
        relatorios.append({
            'id': rel.id,
            'tipo': 'avancado',
            'data_criacao': rel.data_criacao,
            'alvo': None
        })
    
    # Ordenar por data (mais recentes primeiro)
    relatorios.sort(key=lambda x: x['data_criacao'], reverse=True)
    
    return render_template('relatorios_recentes.html', relatorios=relatorios)


# Rota para visualizar um relatório específico
@main_bp.route('/visualizar_relatorio/<int:relatorio_id>/<tipo>')
def visualizar_relatorio(relatorio_id, tipo):
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id'])
    
    # Buscar o relatório correto baseado no tipo
    if tipo == 'basico':
        relatorio = RelatorioBasico.query.get_or_404(relatorio_id)
    elif tipo == 'intermediario':
        relatorio = RelatorioIntermediario.query.get_or_404(relatorio_id)
    elif tipo == 'avancado':
        relatorio = RelatorioAvancado.query.get_or_404(relatorio_id)
    else:
        flash('Tipo de relatório inválido.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
    
    # Verificar se o relatório pertence ao cliente
    if relatorio.cliente_id != cliente.id:
        flash('Você não tem permissão para visualizar este relatório.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
    
    return render_template('visualizar_relatorio.html', relatorio=relatorio, tipo=tipo)


# Rota para minha conta
@main_bp.route('/minha_conta')
def minha_conta():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id'])
    
    # Contar relatórios por tipo
    total_basico = RelatorioBasico.query.filter_by(cliente_id=cliente.id).count()
    total_intermediario = RelatorioIntermediario.query.filter_by(cliente_id=cliente.id).count()
    total_avancado = RelatorioAvancado.query.filter_by(cliente_id=cliente.id).count()
    
    return render_template('minha_conta.html', 
                         cliente=cliente,
                         total_basico=total_basico,
                         total_intermediario=total_intermediario,
                         total_avancado=total_avancado)


# Rota de logout
@main_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('main.index'))


# Rota para termos de uso
@main_bp.route('/termos')
def termos():
    return render_template('termos_styled.html')


# ######################################################################
# ROTAS DE ADMINISTRADOR
# ######################################################################

from .models import Administrador

# Rota de login do admin
@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    # POST - processar login
    email = request.form.get('admin_email')
    senha = request.form.get('admin_senha')
    
    admin = Administrador.query.filter_by(admin_email=email).first()
    
    if not admin:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    if check_password_hash(admin.admin_senha, senha):
        session['admin_id'] = admin.id
        session['is_admin'] = True
        flash('Login de administrador realizado com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    else:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))


# Rota para entrar como admin (alternativa)
@main_bp.route('/admin/entrar', methods=['POST'])
def admin_entrar():
    email = request.form.get('admin_email')
    senha = request.form.get('admin_senha')
    
    admin = Administrador.query.filter_by(admin_email=email).first()
    
    if not admin:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    if check_password_hash(admin.admin_senha, senha):
        session['admin_id'] = admin.id
        session['is_admin'] = True
        flash('Login de administrador realizado com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    else:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))


# Dashboard do admin
@main_bp.route('/admin/dashboard')
def admin_dashboard():
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    # Redirecionar para listar_clientes que já mostra tudo
    return redirect(url_for('main.listar_clientes'))


# Atualizar rota listar_clientes para usar template correto
@main_bp.route('/listar_clientes')
def listar_clientes():
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    clientes = Cliente.query.all()
    return render_template('admin_dashboard.html', clientes=clientes)


# Logout do admin
@main_bp.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Você saiu da área administrativa.', 'success')
    return redirect(url_for('main.index'))
    return redirect(url_for('main.listar_clientes'))