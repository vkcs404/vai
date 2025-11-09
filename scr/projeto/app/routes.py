from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Cliente, RelatorioBasico, RelatorioIntermediario, RelatorioAvancado
from . import db
from .ferramentas.scanner_avancado import rodar_scan_avancado
from .ferramentas.scanner_intermediario import rodar_scan_intermediario
from .ferramentas.scanner_basico import rodar_scan_basico
#from fpdf import FPDF
from flask import Response

# Mapeia uma URL a uma função Python que processa a requisição, chama o scanner ou o banco de dados e retorna o HTML

main_bp = Blueprint('main', __name__) # Cria uma instância de Blueprint chamada 'main', que agrupa todas as rotas da aplicação.

# ... (todas as suas outras rotas como index, cadastro, etc. continuam iguais) ...

@main_bp.route('/') # Define a rota para a página inicial (/).
def index(): # Função que será executada ao acessar a rota '/'.
    return render_template('index.html') # Renderiza o template HTML da página inicial.

@main_bp.route('/cadastro') # Define a rota para a página de cadastro.
def cadastro(): # Função que renderiza o formulário de cadastro.
    return render_template('cadastro.html') # Renderiza o template de cadastro.

@main_bp.route('/login') # Define a rota para a página de login.
def login(): # Função que renderiza o formulário de login.
    # Adiciona uma chave 'redirecionar_para_conta' na sessão para indicar que o login veio do header/navegação
    if 'cliente_id' not in session:
        session['redirecionar_para_conta'] = True
    return render_template('login.html') # Renderiza o template de login.

@main_bp.route('/escolher_relatorio') # Rota para a página de escolha do tipo de relatório.
def escolher_relatorio(): # Função que renderiza a página de escolha.
    return render_template('escolher_relatorio.html') # Renderiza o template de escolha.

@main_bp.route('/selecionar_relatorio', methods=['POST']) # Rota que processa a escolha do relatório (POST).
def selecionar_relatorio(): # Função que lida com a seleção do tipo de relatório pelo usuário.
    tipo_relatorio = request.form.get('tipo_relatorio') # Obtém o valor do campo 'tipo_relatorio' do formulário (basico, intermediario ou avancado).
    if tipo_relatorio in ['basico', 'intermediario', 'avancado']: # Verifica se o tipo de relatório escolhido é válido.
        session['tipo_relatorio'] = tipo_relatorio # Armazena o tipo de relatório selecionado na sessão do usuário.
        # Definir preços e descrições
        precos = { # Dicionário de preços para os diferentes níveis de relatório.
            'basico': '10,00',
            'intermediario': '15,00',
            'avancado': '20,00'
        }
        descricoes = { # Dicionário de descrições para os diferentes níveis.
            'basico': 'Indicado para pessoas com pouco conhecimento técnico em cibersegurança que desejam verificar se o site da empresa está seguro.', # Descrição do relatório básico.
            'intermediario': 'Ideal para desenvolvedores que querem garantir que seus sites estejam protegidos, com um relatório que aponta falhas de segurança que devem ser mitigadas.', # Descrição do relatório intermediário.
            'avancado': 'Voltado para usuários mais experientes que desejam automatizar a detecção de falhas de segurança e receber um relatório detalhado sobre a segurança do site.' # Descrição do relatório avançado.
        }
        session['preco_relatorio'] = precos[tipo_relatorio] # Armazena o preço na sessão.
        session['descricao_relatorio'] = descricoes[tipo_relatorio] # Armazena a descrição na sessão.
        
        # --- AJUSTE 1: SEMPRE REDIRECIONA PARA O LOGIN APÓS SELEÇÃO DE RELATÓRIO ---
        # Isso garante que o usuário valide a identidade antes de pagar (Melhora o fluxo UX/Segurança).
        flash('Por favor, faça login ou cadastre-se para continuar o processo de compra.', 'info') # Mensagem informando o próximo passo.
        
        # Define uma flag na sessão para saber que o login deve levar ao pagamento.
        session['login_apos_selecao'] = True 
        
        return redirect(url_for('main.login')) # Redireciona para o login.
        # ---------------------------------------------------------------------------------------
    else:
        flash('Opção de relatório inválida.', 'danger') # Exibe mensagem de erro se o tipo for inválido.
        return redirect(url_for('main.escolher_relatorio')) # Redireciona de volta para a escolha.

@main_bp.route('/pagamento') # Rota para a página de pagamento.
def pagamento(): # Função que lida com a exibição da página de pagamento.
    # Check if user is logged in
    if 'cliente_id' not in session: # Verifica se o usuário está logado.
        flash('Por favor, faça login para continuar com o pagamento.', 'warning') # Mensagem se não estiver logado.
        return redirect(url_for('main.login')) # Redireciona para o login.
    
    # Obter relatório selecionado da sessão
    tipo_relatorio = session.get('tipo_relatorio', None) # Pega o tipo de relatório da sessão.
    preco_relatorio = session.get('preco_relatorio', None) # Pega o preço da sessão.
    
    if not tipo_relatorio: # Se o tipo de relatório não estiver na sessão.
        flash('Por favor, selecione um tipo de relatório primeiro.', 'warning') # Mensagem para selecionar primeiro.
        return redirect(url_for('main.escolher_relatorio')) # Redireciona para a escolha de relatório.
    
    return render_template('pagamento.html', tipo_relatorio=tipo_relatorio, preco_relatorio=preco_relatorio) # Renderiza a página de pagamento com os dados do relatório.

@main_bp.route('/confirmar_pagamento', methods=['POST']) # Rota para confirmar o pagamento (simulação, via POST).
def confirmar_pagamento(): # Função que simula a confirmação do pagamento.
    # Mark payment as confirmed in session
    session['pagamento_confirmado'] = True # Define a flag na sessão indicando que o pagamento foi confirmado.
    
    # Remove a flag de login após seleção, pois o pagamento será finalizado.
    if 'login_apos_selecao' in session:
        session.pop('login_apos_selecao')

    flash('Pagamento confirmado com sucesso!', 'success') # Mensagem de sucesso.
    return redirect(url_for('main.scaner')) # Redireciona para a página do scanner, onde o cliente pode usar o serviço.


# ... (outras rotas simples) ...

# Rota do cliente novo (nenhuma mudança necessária aqui, o status 'ativo' será definido por padrão)
@main_bp.route('/cliente_novo', methods=['GET' ,'POST']) # Rota para cadastrar um novo cliente. Permite GET (mostrar formulário) e POST (enviar dados).
def cliente_novo(): # Função que lida com o cadastro.
    if request.method == 'POST': # Verifica se o formulário foi submetido.
        nome = request.form.get('cliente_nome') # Obtém o nome do formulário.
        email = request.form.get('cliente_email') # Obtém o e-mail do formulário.
        senha = request.form.get('cliente_senha') # Obtém a senha em texto plano.
        email_existe = Cliente.query.filter_by(cliente_email=email).first() # Consulta o banco para ver se o e-mail já existe.

        if email_existe: # Se o e-mail já estiver cadastrado.
            flash("Email já cadastrado.", "danger") # Mensagem de erro.
            return redirect(url_for('main.cadastro')) # Redireciona para o cadastro novamente.
        
        senha_criptografada = generate_password_hash(senha, method='pbkdf2:sha256') # Criptografa a senha usando um algoritmo forte (pbkdf2:sha256).

        novo_cliente = Cliente( # Cria um novo objeto Cliente.
            cliente_nome=nome, # Atribui o nome.
            cliente_email=email, # Atribui o email.
            cliente_senha=senha_criptografada # Atribui a senha criptografada.
            # O campo 'cliente_status' será 'ativo' por padrão, conforme definido no models.py
        )

        db.session.add(novo_cliente) # Adiciona o novo cliente à sessão do banco de dados.
        db.session.commit() # Confirma as mudanças (salva o cliente no banco).
        
        flash("Cadastro realizado com sucesso! Faça o login.", "success") # Mensagem de sucesso.
        return redirect(url_for('main.index')) # Redireciona para o login.
    
    return render_template ('cadastro.html') # Se o método for GET, renderiza o formulário.


# Rota para cliente logar (MODIFICADA)
@main_bp.route('/cliente_entrar', methods=['GET', 'POST']) # Rota para processar o login do cliente.
def cliente_entrar(): # Função que lida com a autenticação.
    if request.method == 'POST': # Se o formulário de login foi submetido.
        email = request.form.get('cliente_email') # Pega o e-mail.
        senha = request.form.get('cliente_senha') # Pega a senha.

        cliente = Cliente.query.filter_by(cliente_email=email).first() # Busca o cliente pelo e-mail.

        # --- LÓGICA DE STATUS ADICIONADA AQUI ---
        # 1. Verifica se o cliente existe
        if not cliente: # Se nenhum cliente foi encontrado.
            flash('E-mail ou senha inválidos.', 'danger') # Mensagem de erro.
            return redirect(url_for('main.login')) # Redireciona para o login.

        # 2. VERIFICA SE O CLIENTE ESTÁ ATIVO (Se desativado n pode entrar)
        if cliente.cliente_status != 'ativo': # Verifica se o status do cliente não é 'ativo'.
            flash('Este usuário está desativado e não pode entrar.', 'danger') # Impede o login.
            return redirect(url_for('main.login')) # Redireciona.

        # 3. Se estiver ativo, verifica a senha
        if check_password_hash(cliente.cliente_senha, senha): # Verifica se a senha fornecida corresponde ao hash armazenado.
            session['cliente_id'] = cliente.id # Armazena o ID do cliente na sessão (mantendo-o logado).
            flash('Login realizado com sucesso!', 'success') # Mensagem de sucesso.
            
            # --- AJUSTE 2: LÓGICA DE REDIRECIONAMENTO APÓS LOGIN ---
            
            # Caso A: O login veio de uma seleção de relatório (prioridade)
            if session.get('login_apos_selecao') and 'tipo_relatorio' in session: 
                # Remove a flag de login após seleção, pois o usuário está prestes a ser redirecionado para o pagamento.
                session.pop('login_apos_selecao', None) 
                return redirect(url_for('main.pagamento')) # Redireciona para o pagamento pendente.
            
            # Caso B: O login veio da navegação/header (redireciona para a conta)
            elif session.get('redirecionar_para_conta'): 
                session.pop('redirecionar_para_conta', None) # Remove a flag após o uso.
                return redirect(url_for('main.minha_conta')) # Redireciona para Minha Conta (como solicitado).
            
            # Caso C: Nenhum caso especial, login padrão
            else:
                return redirect(url_for('main.scaner')) # Redirecionamento padrão para a tela de scanner.
            # ------------------------------------------------------------------
            
        else:
            flash('E-mail ou senha inválidos.', 'danger') # Se a senha estiver incorreta.
            return redirect(url_for('main.login')) # Redireciona para o login.
    
    return render_template('login.html') # Se GET, renderiza o login.

@main_bp.route('/admin/alternar_status/<int:cliente_id>', methods=['POST']) # Rota para um administrador alternar o status de um cliente (POST para alteração).
def alternar_status(cliente_id): # Recebe o ID do cliente como parâmetro.
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'): # Verifica se o usuário logado é um administrador.
        flash('Acesso restrito a administradores.', 'danger') # Bloqueia o acesso.
        return redirect(url_for('main.admin_login')) # Redireciona para o login do admin.

    cliente = Cliente.query.get_or_404(cliente_id) # Busca o cliente pelo ID ou retorna 404 (Não Encontrado).

    # Lógica para alternar o status
    if cliente.cliente_status == 'ativo': # Se o status atual for 'ativo'.
        cliente.cliente_status = 'inativo' # Altera para 'inativo'.
        flash(f'Cliente {cliente.cliente_nome} foi desativado.', 'success') # Mensagem de desativação.
    else: # Se for 'inativo'.
        cliente.cliente_status = 'ativo' # Altera para 'ativo'.
        flash(f'Cliente {cliente.cliente_nome} foi ativado.', 'success') # Mensagem de ativação.
    
    db.session.commit() # Salva a mudança de status no banco de dados.
    
    # Redireciona de volta para a página de onde o admin veio (ex: uma lista de clientes)
    return redirect(url_for('main.listar_clientes')) # Redireciona para a lista de clientes.


# Em app/routes.py

@main_bp.route('/scaner') # Rota principal para a interface do scanner.
def scaner(): # Função que exibe a interface do scanner.
    # Proteger esta rota
    if 'cliente_id' not in session: # Verifica se o cliente está logado.
        flash('Você precisa estar logado para acessar esta página.', 'warning') # Mensagem de aviso.
        return redirect(url_for('main.login')) # Redireciona para o login.
    
    # Busca o cliente (para o template saber o nível de acesso)
    cliente = Cliente.query.get(session['cliente_id']) # Recupera o objeto Cliente completo usando o ID da sessão.
    
    # Renderiza o template, passando APENAS o cliente
    return render_template('scaner.html', cliente=cliente) # Renderiza a página do scanner, passando os dados do cliente para controlar o que ele pode ver/usar.


# Em app/routes.py

# --- ROTA POST para SCAN BÁSICO (CORRIGIDA) ---
@main_bp.route('/executar_scanner_basico', methods=['POST']) # Rota para executar o scanner básico (recebe POST do formulário).
def executar_scanner_basico(): # Função que inicia e armazena o scan básico.
    
    if 'cliente_id' not in session: # Verifica se o cliente está logado.
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente.
    
    # --- CORREÇÃO DE PERMISSÃO ---
    if cliente.nivel_acesso != 'basico': # Verifica se o nível de acesso do cliente corresponde ao scanner básico.
        flash('Permissão negada. Você não tem acesso ao scanner básico.', 'danger') # Mensagem de negação.
        return redirect(url_for('main.scaner')) # Redireciona.

    alvo = request.form.get('alvo') # Obtém o alvo (URL/domínio) do formulário.
    if not alvo: # Verifica se o alvo foi fornecido.
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        # --- CORREÇÃO DE FUNÇÃO ---
        conteudo_do_relatorio = rodar_scan_basico(alvo) # Chama a função de scanner para executar a varredura e obter o resultado.

        # --- CORREÇÃO DE MODELO ---
        novo_relatorio = RelatorioBasico( # Cria uma nova instância do modelo RelatorioBasico.
            conteudo=conteudo_do_relatorio, # Armazena o resultado do scan.
            cliente_id=cliente.id # Associa o relatório ao ID do cliente.
        )
        
        db.session.add(novo_relatorio) # Adiciona o novo relatório à sessão do banco.
        db.session.commit() # Salva o relatório no banco.
        
        flash('Scan básico concluído!', 'success')
        
        # --- CORREÇÃO DE REDIRECT ---
        return redirect(url_for('main.visualizar_relatorio', # Redireciona para a rota de visualização.
                                relatorio_id=novo_relatorio.id, # Passa o ID do novo relatório.
                                tipo='basico')) # Passa o tipo do relatório.

    except Exception as e: # Captura qualquer erro que possa ocorrer durante o scan.
        # !!!!! MUDANÇA IMPORTANTE !!!!!
        # Isso vai nos mostrar o erro no terminal!
        print(f"ERRO NO SCAN BÁSICO: {e}") # Imprime o erro no console (útil para debug).
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger') # Exibe o erro para o usuário.
        return redirect(url_for('main.scaner')) # Redireciona.


# --- ROTA POST para SCAN INTERMEDIÁRIO (CORRIGIDA) ---
@main_bp.route('/executar_scanner_intermediario', methods=['POST']) # Rota para executar o scanner intermediário.
def executar_scanner_intermediario(): # Função que inicia e armazena o scan intermediário.
    
    if 'cliente_id' not in session: # Verifica login.
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente.
    
    # --- CORREÇÃO DE PERMISSÃO ---
    if cliente.nivel_acesso != 'intermediario': # Verifica permissão.
        flash('Permissão negada. Você não tem acesso ao scanner intermediário.', 'danger')
        return redirect(url_for('main.scaner'))

    alvo = request.form.get('alvo') # Obtém o alvo.
    if not alvo: # Verifica alvo.
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        # --- CORREÇÃO DE FUNÇÃO ---
        conteudo_do_relatorio = rodar_scan_intermediario(alvo) # Executa o scan intermediário.

        # --- CORREÇÃO DE MODELO ---
        novo_relatorio = RelatorioIntermediario( # Cria nova instância de RelatorioIntermediario.
            conteudo=conteudo_do_relatorio,
            cliente_id=cliente.id
        )
        
        db.session.add(novo_relatorio)
        db.session.commit()
        
        flash('Scan intermediário concluído!', 'success')
        
        # --- CORREÇÃO DE REDIRECT ---
        return redirect(url_for('main.visualizar_relatorio', 
                                relatorio_id=novo_relatorio.id, 
                                tipo='intermediario')) # Redireciona para a visualização.

    except Exception as e:
        # !!!!! MUDANÇA IMPORTANTE !!!!!
        print(f"ERRO NO SCAN INTERMEDIÁRIO: {e}")
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger')
        return redirect(url_for('main.scaner'))


# --- ROTA POST para SCAN AVANÇADO (CORRIGIDA) ---
@main_bp.route('/executar_scanner_avancado', methods=['POST']) # Rota para executar o scanner avançado.
def executar_scanner_avancado(): # Função que inicia e armazena o scan avançado.
    
    if 'cliente_id' not in session: # Verifica login.
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente.
    
    # --- PERMISSÃO CORRETA ---
    if cliente.nivel_acesso != 'avancado': # Verifica permissão.
        flash('Permissão negada. Você não tem acesso ao scanner avançado.', 'danger')
        return redirect(url_for('main.scaner'))

    alvo = request.form.get('alvo') # Obtém o alvo.
    if not alvo:
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        conteudo_do_relatorio = rodar_scan_avancado(alvo) # Executa o scan avançado.

        novo_relatorio = RelatorioAvancado( # Cria nova instância de RelatorioAvancado.
            conteudo=conteudo_do_relatorio, # Usando 'conteudo' para armazenar o resultado.
            cliente_id=cliente.id
        )
        
        db.session.add(novo_relatorio)
        db.session.commit()
        
        flash('Scan avançado concluído!', 'success')
        
        return redirect(url_for('main.visualizar_relatorio', 
                                relatorio_id=novo_relatorio.id, 
                                tipo='avancado')) # Redireciona para a visualização.

    except Exception as e:
        # !!!!! MUDANÇA IMPORTANTE !!!!!
        print(f"ERRO NO SCAN AVANÇADO: {e}")
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger')
        return redirect(url_for('main.scaner'))


    # Rota para Alterar o Nível de Acesso do Cliente
@main_bp.route('/admin/alterar_nivel/<int:cliente_id>', methods=['POST']) # Rota do admin para mudar o nível de acesso do cliente.
def alterar_nivel_acesso(cliente_id): # Recebe o ID do cliente.
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'): # Verifica se o admin está logado.
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))

    cliente_alvo = Cliente.query.get_or_404(cliente_id) # Busca o cliente a ser alterado.
    novo_nivel = request.form.get('novo_nivel') # Obtém o novo nível do formulário.
    
    # Lista de níveis válidos para evitar injeção de dados
    niveis_validos = ['basico', 'intermediario', 'avancado'] # Define os níveis permitidos (segurança).

    if novo_nivel and novo_nivel in niveis_validos: # Valida se o nível é válido.
        # Altera o nível do cliente no banco de dados
        cliente_alvo.nivel_acesso = novo_nivel # Atualiza o campo 'nivel_acesso'.
        db.session.commit() # Salva a mudança.
        
        flash(f'O nível de acesso de {cliente_alvo.cliente_nome} foi alterado para {novo_nivel.title()}.', 'success')
    else:
        flash('Nível de acesso inválido.', 'danger')
    
    # Redireciona de volta para a lista de clientes ou para onde você precisar
    return redirect(url_for('main.listar_clientes')) # Redireciona.


# ######################################################################
# NOVAS ROTAS ADICIONADAS
# ######################################################################

# Rota para visualizar relatórios recentes
@main_bp.route('/relatorios_recentes') # Rota que lista os relatórios do usuário.
def relatorios_recentes(): # Função que busca e exibe os relatórios.
    if 'cliente_id' not in session: # Verifica login.
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.
    
    # Buscar todos os relatórios do cliente dos últimos 30 dias
    from datetime import datetime, timedelta # Importa timedelta para calcular o intervalo de tempo.
    data_limite = datetime.utcnow() - timedelta(days=30) # Calcula a data de 30 dias atrás (regra dos 30 dias).
    
    # Combinar todos os tipos de relatórios
    relatorios = [] # Lista para armazenar todos os relatórios combinados.
    
    # Relatórios Básicos
    basicos = RelatorioBasico.query.filter( # Faz a consulta:
        RelatorioBasico.cliente_id == cliente.id, # 1. O relatório pertence ao cliente logado.
        RelatorioBasico.data_criacao >= data_limite # 2. O relatório foi criado nos últimos 30 dias.
    ).all() # Busca todos os resultados.
    for rel in basicos: # Itera sobre os resultados básicos.
        relatorios.append({ # Adiciona um dicionário formatado à lista 'relatorios'.
            'id': rel.id,
            'tipo': 'basico',
            'data_criacao': rel.data_criacao,
            'alvo': None  # Adicionar se tiver campo alvo
        })
    
    # Relatórios Intermediários
    intermediarios = RelatorioIntermediario.query.filter( # Consulta relatórios intermediários (mesma lógica).
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
    avancados = RelatorioAvancado.query.filter( # Consulta relatórios avançados (mesma lógica).
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
    relatorios.sort(key=lambda x: x['data_criacao'], reverse=True) # Ordena a lista de dicionários pela data de criação (descendente).
    
    return render_template('relatorios_recentes.html', relatorios=relatorios) # Renderiza o template, enviando a lista ordenada.


# Rota para visualizar um relatório específico
@main_bp.route('/visualizar_relatorio/<int:relatorio_id>/<tipo>') # Rota que recebe o ID e o tipo do relatório via URL (parâmetros dinâmicos).
def visualizar_relatorio(relatorio_id, tipo): # Função que exibe o conteúdo de um relatório.
    if 'cliente_id' not in session: # Verifica login.
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.
    
    # Buscar o relatório correto baseado no tipo
    relatorio = None # Inicializa a variável do relatório.
    if tipo == 'basico': # Se o tipo for 'basico'.
        relatorio = RelatorioBasico.query.get_or_404(relatorio_id) # Busca no modelo RelatorioBasico.
    elif tipo == 'intermediario': # Se o tipo for 'intermediario'.
        relatorio = RelatorioIntermediario.query.get_or_404(relatorio_id) # Busca no modelo RelatorioIntermediario.
    elif tipo == 'avancado': # Se o tipo for 'avancado'.
        relatorio = RelatorioAvancado.query.get_or_404(relatorio_id) # Busca no modelo RelatorioAvancado.
    else: # Se o tipo na URL for inválido.
        flash('Tipo de relatório inválido.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
    
    # Verificar se o relatório pertence ao cliente
    if relatorio.cliente_id != cliente.id: # Verifica se o ID do dono do relatório é o mesmo do cliente logado (segurança).
        flash('Você não tem permissão para visualizar este relatório.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
    
    return render_template('visualizar_relatorio.html', relatorio=relatorio, tipo=tipo) # Renderiza o template com o conteúdo do relatório.


# Rota para minha conta
@main_bp.route('/minha_conta') # Rota para a página de perfil do cliente.
def minha_conta(): # Função que exibe o perfil e estatísticas.
    if 'cliente_id' not in session: # Verifica login.
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.
    
    # Contar relatórios por tipo (estatísticas para o perfil)
    total_basico = RelatorioBasico.query.filter_by(cliente_id=cliente.id).count() # Conta quantos relatórios básicos o cliente possui.
    total_intermediario = RelatorioIntermediario.query.filter_by(cliente_id=cliente.id).count() # Conta quantos intermediários.
    total_avancado = RelatorioAvancado.query.filter_by(cliente_id=cliente.id).count() # Conta quantos avançados.
    
    return render_template('minha_conta.html', # Renderiza a página da conta.
                         cliente=cliente, # Passa os dados do cliente.
                         total_basico=total_basico, # Passa o total de básicos.
                         total_intermediario=total_intermediario, # Passa o total de intermediários.
                         total_avancado=total_avancado) # Passa o total de avançados.


# Rota de logout
@main_bp.route('/logout', methods=['POST']) # Rota para realizar o logout (melhor via POST para segurança).
def logout(): # Função que encerra a sessão.
    session.clear() # Limpa todos os dados da sessão (incluindo 'cliente_id' e 'admin_id').
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('main.index')) # Redireciona para a página inicial.


# Rota para termos de uso
@main_bp.route('/termos') # Rota simples para a página de termos.
def termos():
    return render_template('termos_styled.html') # Renderiza o template de termos.


# ######################################################################
# ROTAS DE ADMINISTRADOR
# ######################################################################

from .models import Administrador # Garante que o modelo Administrador está importado para as rotas de admin.

# Rota de login do admin
@main_bp.route('/admin/login', methods=['GET', 'POST']) # Rota de login do admin.
def admin_login():
    if request.method == 'GET': # Se GET, mostra o formulário.
        return render_template('admin_login.html')
    
    # POST - processar login
    email = request.form.get('admin_email') # Pega o e-mail.
    senha = request.form.get('admin_senha') # Pega a senha.
    
    admin = Administrador.query.filter_by(admin_email=email).first() # Busca o admin pelo e-mail.
    
    if not admin: # Se não encontrou.
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    if check_password_hash(admin.admin_senha, senha): # Verifica a senha.
        session['admin_id'] = admin.id # Salva o ID do admin na sessão.
        session['is_admin'] = True # Define uma flag de admin na sessão.
        flash('Login de administrador realizado com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard')) # Redireciona para o dashboard.
    else:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))


# Rota para entrar como admin (alternativa)
@main_bp.route('/admin/entrar', methods=['POST']) # Rota POST auxiliar (pode ser redundante com admin_login POST).
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
@main_bp.route('/admin/dashboard') # Rota do dashboard.
def admin_dashboard():
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    # Redirecionar para listar_clientes que já mostra tudo
    return redirect(url_for('main.listar_clientes')) # Redireciona o dashboard para a rota de listagem de clientes.


# Atualizar rota listar_clientes para usar template correto
@main_bp.route('/listar_clientes') # Rota que lista todos os clientes (principal view do admin).
def listar_clientes():
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'): # Protege a rota.
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    clientes = Cliente.query.all() # Busca TODOS os clientes no banco de dados.
    return render_template('admin_dashboard.html', clientes=clientes) # Renderiza o dashboard do admin, passando a lista de clientes.


# Logout do admin
@main_bp.route('/admin/logout') # Rota de logout do admin.
def admin_logout():
    session.clear() # Limpa a sessão.
    flash('Você saiu da área administrativa.', 'success')
    return redirect(url_for('main.index')) # Redireciona para o índice.
    return redirect(url_for('main.listar_clientes')) # Esta linha está redundante e nunca será alcançada.


# Em app/routes.py

@main_bp.route('/download_relatorio/<int:relatorio_id>/<tipo>') # Rota para gerar e baixar o relatório em PDF.
def download_relatorio(relatorio_id, tipo): # Recebe ID e tipo do relatório.
    if 'cliente_id' not in session: # Verifica login.
        flash('Você precisa estar logado para baixar relatórios.', 'warning')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.

    # --- LÓGICA DE BUSCA SIMPLIFICADA ---
    conteudo = "" # Variável para armazenar o conteúdo do relatório.
    relatorio = None
    if tipo == 'basico':
        relatorio = RelatorioBasico.query.get_or_404(relatorio_id)
        conteudo = relatorio.conteudo
    elif tipo == 'intermediario':
        relatorio = RelatorioIntermediario.query.get_or_404(relatorio_id)
        conteudo = relatorio.conteudo
    elif tipo == 'avancado':
        relatorio = RelatorioAvancado.query.get_or_404(relatorio_id)
        conteudo = relatorio.conteudo # <-- CORRIGIDO
    else:
        flash('Tipo de relatório inválido.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))

    # --- O RESTO DO SEU CÓDIGO ESTÁ PERFEITO ---
    if relatorio.cliente_id != cliente.id: # Verifica se o cliente é o dono.
        flash('Você não tem permissão para baixar este relatório.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
'''
    # GERA O PDF
    pdf = FPDF() # Cria uma nova instância da classe FPDF.
    pdf.add_page() # Adiciona uma nova página ao PDF.
    pdf.set_font('Arial', '', 12) # Define a fonte e o tamanho.
    pdf.cell(0, 10, f'Relatorio Tecnico - {tipo.title()}', ln=True, align='C') # Adiciona o título do relatório.
    pdf.cell(0, 10, f"Gerado em: {relatorio.data_criacao.strftime('%d/%m/%Y')}", ln=True, align='C') # Adiciona a data de criação.
    pdf.ln(10) # Adiciona uma quebra de linha com altura 10.
    pdf.multi_cell(0, 5, conteudo) # Adiciona o conteúdo do relatório, permitindo múltiplas linhas.
    pdf_output = pdf.output() # Gera o conteúdo binário do PDF.
    
    return Response( # Retorna uma resposta HTTP com o arquivo PDF.
        pdf_output, # O conteúdo binário do PDF.
        mimetype='application/pdf', # Define o tipo MIME como PDF.
        headers={ # Define os cabeçalhos HTTP.
            'Content-Disposition': f'attachment; filename="relatorio_{tipo}_{relatorio_id}.pdf"' # Força o download do arquivo com um nome específico.
        }
    )
'''


'''
#Mapeia uma URL a uma função Python que processa a requisição, chama o scanner ou o banco de dados e retorna o HTML

main_bp = Blueprint('main', __name__) # Cria uma instância de Blueprint chamada 'main', que agrupa todas as rotas da aplicação.

@main_bp.route('/') # Define a rota para a página inicial (/).
def index():  # Função que será executada ao acessar a rota '/'.
    return render_template('index.html') # Renderiza o template HTML da página inicial.

@main_bp.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

#@main_bp.route('/login')
#def login():
#    return render_template('login.html')
@main_bp.route('/login') # Define a rota para a página de login.
def login(): # Função que renderiza o formulário de login.
    # Adiciona uma chave 'redirecionar_para_conta' na sessão para indicar que o login veio do header/navegação
    if 'cliente_id' not in session:
        session['redirecionar_para_conta'] = True
    return render_template('login.html') # Renderiza o template de login.

@main_bp.route('/escolher_relatorio')
def escolher_relatorio():
    return render_template('escolher_relatorio.html')

@main_bp.route('/selecionar_relatorio', methods=['POST']) # Rota que processa a escolha do relatório (POST).
def selecionar_relatorio(): # Função que lida com a seleção do tipo de relatório pelo usuário.
    tipo_relatorio = request.form.get('tipo_relatorio') # Obtém o valor do campo 'tipo_relatorio' do formulário (basico, intermediario ou avancado).
    if tipo_relatorio in ['basico', 'intermediario', 'avancado']:
        session['tipo_relatorio'] = tipo_relatorio # Armazena o tipo de relatório selecionado na sessão do usuário.
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
        session['preco_relatorio'] = precos[tipo_relatorio] # Armazena o preço na sessão.
        session['descricao_relatorio'] = descricoes[tipo_relatorio] # Armazena a descrição na sessão.
        
        # Check if user is logged in
        if 'cliente_id' in session: # Verifica se o ID do cliente está na sessão (usuário logado).
            # User is logged in, go to payment
            return redirect(url_for('main.pagamento')) # Se estiver logado, redireciona para a página de pagamento.
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
    
    return render_template('pagamento.html', tipo_relatorio=tipo_relatorio, preco_relatorio=preco_relatorio)  # Renderiza a página de pagamento com os dados do relatório.

@main_bp.route('/confirmar_pagamento', methods=['POST'])  # Rota para confirmar o pagamento (simulação, via POST).
def confirmar_pagamento():  # Função que simula a confirmação do pagamento.
    session['pagamento_confirmado'] = True
    flash('Pagamento confirmado com sucesso!', 'success')
    return redirect(url_for('main.scaner')) # Redireciona para a página do scanner, onde o cliente pode usar o serviço.

@main_bp.route('/cliente_novo', methods=['GET' ,'POST']) # Rota do cliente novo (status 'ativo' definido por padrão)
def cliente_novo():
    if request.method == 'POST':  # Verifica se o formulário foi submetido.
        nome = request.form.get('cliente_nome') # Obtém o nome do formulário.
        email = request.form.get('cliente_email') # Obtém o e-mail do formulário.
        senha = request.form.get('cliente_senha') # Obtém a senha em texto plano.
        email_existe = Cliente.query.filter_by(cliente_email=email).first()  # Consulta o banco para ver se o e-mail já existe.

        if email_existe:
            flash("Email já cadastrado.", "danger")
            return redirect(url_for('main.cadastro'))
        
        senha_criptografada = generate_password_hash(senha, method='pbkdf2:sha256') # Criptografa a senha usando um algoritmo forte (pbkdf2:sha256).

        novo_cliente = Cliente( # Cria um novo objeto Cliente.
            cliente_nome=nome, # Atribui o nome.
            cliente_email=email, # Atribui o nome.
            cliente_senha=senha_criptografada  # Atribui o email.
            # O campo 'cliente_status' será 'ativo' por padrão, conforme definido no models.py
        )

        db.session.add(novo_cliente) # Adiciona o novo cliente à sessão do banco de dados.
        db.session.commit() # Confirma as mudanças (salva o cliente no banco).
        
        flash("Cadastro realizado com sucesso! Faça o login.", "success")
        return redirect(url_for('main.login'))  # Redireciona para o login.
    
    return render_template ('cadastro.html')

@main_bp.route('/cliente_entrar', methods=['GET', 'POST'])  # Rota para processar o login do cliente.
def cliente_entrar():
    if request.method == 'POST':
        email = request.form.get('cliente_email')
        senha = request.form.get('cliente_senha')

        cliente = Cliente.query.filter_by(cliente_email=email).first() # Busca o cliente pelo e-mail.

        # LÓGICA DE STATUS ADICIONADA AQUI
        # 1. Verifica se o cliente existe
        if not cliente:
            flash('E-mail ou senha inválidos.', 'danger')
            return redirect(url_for('main.login'))

        # 2. VERIFICA SE O CLIENTE ESTÁ ATIVO (Se desativado n pode entrar)
        if cliente.cliente_status != 'ativo':
            flash('Este usuário está desativado e não pode entrar.', 'danger') #impede login
            return redirect(url_for('main.login')) #redireciona

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

@main_bp.route('/admin/alternar_status/<int:cliente_id>', methods=['POST'])  # Rota para um administrador alternar o status de um cliente (POST para alteração).
def alternar_status(cliente_id):
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))

    cliente = Cliente.query.get_or_404(cliente_id)  # Busca o cliente pelo ID ou retorna 404 (Não Encontrado).

    # Lógica para alternar o status
    if cliente.cliente_status == 'ativo': # Se o status atual for 'ativo'.
        cliente.cliente_status = 'inativo' # Altera para 'inativo'.
        flash(f'Cliente {cliente.cliente_nome} foi desativado.', 'success')
    else: # Se for 'inativo'.
        cliente.cliente_status = 'ativo'
        flash(f'Cliente {cliente.cliente_nome} foi ativado.', 'success')
    
    db.session.commit() # Salva a mudança de status no banco de dados.
    
    return redirect(url_for('main.listar_clientes')) # Redireciona para a lista de clientes.

@main_bp.route('/scaner')  # Rota principal para a interface do scanner.
def scaner():
    # Proteger esta rota
    if 'cliente_id' not in session: # Verifica se o cliente está logado.
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login')) # Redireciona para o login.
    
    # Busca o cliente (para o template saber o nível de acesso)
    cliente = Cliente.query.get(session['cliente_id'])
    
    return render_template('scaner.html', cliente=cliente) # Renderiza a página do scanner, passando os dados do cliente para controlar o que ele pode ver/usar.

@main_bp.route('/executar_scanner_basico', methods=['POST']) # Rota para executar o scanner básico (recebe POST do formulário).
def executar_scanner_basico(): # Função que inicia e armazena o scan básico.
    
    if 'cliente_id' not in session: # Verifica se o cliente está logado.
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente.
    
    if cliente.nivel_acesso != 'basico': # Verifica se o nível de acesso do cliente corresponde ao scanner básico.
        flash('Permissão negada. Você não tem acesso ao scanner básico.', 'danger')
        return redirect(url_for('main.scaner'))

    alvo = request.form.get('alvo') # Obtém o alvo (URL/domínio) do formulário.
    if not alvo:
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        conteudo_do_relatorio = rodar_scan_basico(alvo) # Chama a função de scanner para executar a varredura e obter o resultado.

        novo_relatorio = RelatorioBasico( # Cria uma nova instância do modelo RelatorioBasico.
            conteudo=conteudo_do_relatorio, # Armazena o resultado do scan.
            cliente_id=cliente.id # Associa o relatório ao ID do cliente.
        )
        
        db.session.add(novo_relatorio)  # Adiciona o novo relatório à sessão do banco.
        db.session.commit() # Salva o relatório no banco.
        
        flash('Scan básico concluído!', 'success')
      
        return redirect(url_for('main.visualizar_relatorio', # Redireciona para a rota de visualização.
                                relatorio_id=novo_relatorio.id,  # Passa o ID do novo relatório.
                                tipo='basico')) # Passa o tipo do relatório.

    except Exception as e:
        print(f"ERRO NO SCAN BÁSICO: {e}") 
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger')
        return redirect(url_for('main.scaner'))

@main_bp.route('/executar_scanner_intermediario', methods=['POST']) # Rota para executar o scanner intermediário.
def executar_scanner_intermediario():
    
    if 'cliente_id' not in session:
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id'])
    
    # --- CORREÇÃO DE PERMISSÃO ---
    if cliente.nivel_acesso != 'intermediario':
        flash('Permissão negada. Você não tem acesso ao scanner intermediário.', 'danger')
        return redirect(url_for('main.scaner'))

    alvo = request.form.get('alvo')
    if not alvo:
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        # --- CORREÇÃO DE FUNÇÃO ---
        conteudo_do_relatorio = rodar_scan_intermediario(alvo)

        # --- CORREÇÃO DE MODELO ---
        novo_relatorio = RelatorioIntermediario(
            conteudo=conteudo_do_relatorio,
            cliente_id=cliente.id
        )
        
        db.session.add(novo_relatorio)
        db.session.commit()
        
        flash('Scan intermediário concluído!', 'success')
        
        return redirect(url_for('main.visualizar_relatorio', 
                                relatorio_id=novo_relatorio.id, 
                                tipo='intermediario'))

    except Exception as e:
        print(f"ERRO NO SCAN INTERMEDIÁRIO: {e}")
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger')
        return redirect(url_for('main.scaner'))

@main_bp.route('/executar_scanner_avancado', methods=['POST']) # Rota para executar o scanner avançado.
def executar_scanner_avancado():
    
    if 'cliente_id' not in session:
        flash('Sessão expirada. Faça login novamente.', 'danger')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id'])
    
    # --- PERMISSÃO CORRETA ---
    if cliente.nivel_acesso != 'avancado':
        flash('Permissão negada. Você não tem acesso ao scanner avançado.', 'danger')
        return redirect(url_for('main.scaner'))

    alvo = request.form.get('alvo')
    if not alvo:
        flash('Alvo (domínio) não fornecido.', 'warning')
        return redirect(url_for('main.scaner'))

    try:
        conteudo_do_relatorio = rodar_scan_avancado(alvo)

        novo_relatorio = RelatorioAvancado(
            conteudo=conteudo_do_relatorio,
            cliente_id=cliente.id
        )
        
        db.session.add(novo_relatorio)
        db.session.commit()
        
        flash('Scan avançado concluído!', 'success')
        
        return redirect(url_for('main.visualizar_relatorio', 
                                relatorio_id=novo_relatorio.id, 
                                tipo='avancado'))

    except Exception as e:
        print(f"ERRO NO SCAN AVANÇADO: {e}")
        flash(f'Ocorreu um erro durante o scan: {e}', 'danger')
        return redirect(url_for('main.scaner'))


    
@main_bp.route('/admin/alterar_nivel/<int:cliente_id>', methods=['POST']) # Rota do admin para mudar o nível de acesso do cliente.
def alterar_nivel_acesso(cliente_id): # Recebe o ID do cliente.
    if 'admin_id' not in session or not session.get('is_admin'): # Verificar se é admin
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))

    cliente_alvo = Cliente.query.get_or_404(cliente_id) # Busca o cliente a ser alterado.
    novo_nivel = request.form.get('novo_nivel')  # Obtém o novo nível do formulário.
    
    niveis_validos = ['basico', 'intermediario', 'avancado']

    if novo_nivel and novo_nivel in niveis_validos:
        # Altera o nível do cliente no banco de dados
        cliente_alvo.nivel_acesso = novo_nivel # Atualiza o campo 'nivel_acesso'.
        db.session.commit() # Salva a mudança.
        
        flash(f'O nível de acesso de {cliente_alvo.cliente_nome} foi alterado para {novo_nivel.title()}.', 'success')
    else:
        flash('Nível de acesso inválido.', 'danger')
    
    return redirect(url_for('main.listar_clientes')) # Redireciona de volta para a lista de clientes

@main_bp.route('/relatorios_recentes') # Rota para visualizar relatórios recentes
def relatorios_recentes():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.
    
    # Buscar todos os relatórios do cliente dos últimos 30 dias
    from datetime import datetime, timedelta
    data_limite = datetime.utcnow() - timedelta(days=30) # Calcula a data de 30 dias atrás (regra dos 30 dias).
    
    # Combinar todos os tipos de relatórios
    relatorios = []
    
    # Relatórios Básicos
    basicos = RelatorioBasico.query.filter( # Faz a consulta:
        RelatorioBasico.cliente_id == cliente.id, # 1. O relatório pertence ao cliente logado.
        RelatorioBasico.data_criacao >= data_limite # 2. O relatório foi criado nos últimos 30 dias.
    ).all() # Busca todos os resultados.
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
    
    return render_template('relatorios_recentes.html', relatorios=relatorios) # Renderiza o template, enviando a lista ordenada.

@main_bp.route('/visualizar_relatorio/<int:relatorio_id>/<tipo>') # Rota para visualizar um relatório específico -  recebe o ID e o tipo do relatório via URL 
def visualizar_relatorio(relatorio_id, tipo):  # Função que exibe o conteúdo de um relatório.
    if 'cliente_id' not in session: # Verifica login.
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.
    
    # Buscar o relatório correto baseado no tipo
    relatorio = None  # Inicializa a variável do relatório.
    if tipo == 'basico':
        relatorio = RelatorioBasico.query.get_or_404(relatorio_id) # Busca no modelo RelatorioBasico.
    elif tipo == 'intermediario':
        relatorio = RelatorioIntermediario.query.get_or_404(relatorio_id)
    elif tipo == 'avancado':
        relatorio = RelatorioAvancado.query.get_or_404(relatorio_id)
    else:  # Se o tipo na URL for inválido.
        flash('Tipo de relatório inválido.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
    
    # Verificar se o relatório pertence ao cliente
    if relatorio.cliente_id != cliente.id: # Verifica se o ID do dono do relatório é o mesmo do cliente logado (segurança).
        flash('Você não tem permissão para visualizar este relatório.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))
    
    return render_template('visualizar_relatorio.html', relatorio=relatorio, tipo=tipo)  # Renderiza o template com o conteúdo do relatório.

@main_bp.route('/minha_conta') # Rota para a página de perfil do cliente.
def minha_conta():
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('main.login'))
    
    cliente = Cliente.query.get(session['cliente_id']) # Busca o cliente logado.
    
    # Contar relatórios por tipo
    total_basico = RelatorioBasico.query.filter_by(cliente_id=cliente.id).count() # Conta quantos relatórios básicos o cliente possui.
    total_intermediario = RelatorioIntermediario.query.filter_by(cliente_id=cliente.id).count()
    total_avancado = RelatorioAvancado.query.filter_by(cliente_id=cliente.id).count()
    
    return render_template('minha_conta.html', # Renderiza a página da conta.
                         cliente=cliente, # Passa os dados do cliente.
                         total_basico=total_basico,  # Passa o total de básicos.
                         total_intermediario=total_intermediario, # Passa o total de intermediários.
                         total_avancado=total_avancado) # Passa o total de avançados.

@main_bp.route('/logout', methods=['POST']) # Rota para realizar o logout
def logout():
    session.clear() # Limpa todos os dados da sessão (incluindo 'cliente_id' e 'admin_id').
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('main.index')) # Redireciona para a página inicial.

@main_bp.route('/termos') # Rota para termos de uso
def termos():
    return render_template('termos_styled.html')


# ######################################################################
# ROTAS DE ADMINISTRADOR
# ######################################################################

from .models import Administrador

@main_bp.route('/admin/login', methods=['GET', 'POST']) # Rota de login do admin
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    # POST - processar login
    email = request.form.get('admin_email')
    senha = request.form.get('admin_senha')
    
    admin = Administrador.query.filter_by(admin_email=email).first() # Busca o admin pelo e-mail.
    
    if not admin:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    if check_password_hash(admin.admin_senha, senha):  # Verifica a senha.
        session['admin_id'] = admin.id # Salva o ID do admin na sessão.
        session['is_admin'] = True # Define uma flag de admin na sessão.
        flash('Login de administrador realizado com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard')) # Redireciona para o dashboard.
    else:
        flash('E-mail ou senha inválidos.', 'danger')
        return redirect(url_for('main.admin_login'))


# Rota para entrar como admin (alternativa)
#@main_bp.route('/admin/entrar', methods=['POST'])
#def admin_entrar():
#    email = request.form.get('admin_email')
#    senha = request.form.get('admin_senha')
    
#    admin = Administrador.query.filter_by(admin_email=email).first()
#    
#    if not admin:
#        flash('E-mail ou senha inválidos.', 'danger')
#        return redirect(url_for('main.admin_login'))
#    
#    if check_password_hash(admin.admin_senha, senha):
#        session['admin_id'] = admin.id
#      return redirect(url_for('main.admin_dashboard'))
#    else:
#        flash('E-mail ou senha inválidos.', 'danger')
#        return redirect(url_for('main.admin_login'))

@main_bp.route('/admin/dashboard') # Dashboard do admin
def admin_dashboard():
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    # Redirecionar para listar_clientes que já mostra tudo
    return redirect(url_for('main.listar_clientes'))

# Atualizar rota listar_clientes para usar template correto
@main_bp.route('/listar_clientes')  # Rota que lista todos os clientes (principal view do admin).
def listar_clientes():
    # Verificar se é admin
    if 'admin_id' not in session or not session.get('is_admin'):
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('main.admin_login'))
    
    clientes = Cliente.query.all()  # Busca TODOS os clientes no banco de dados.
    return render_template('admin_dashboard.html', clientes=clientes)  # Renderiza o dashboard do admin, passando a lista de clientes.

@main_bp.route('/admin/logout')  # Rota de logout do admin.
def admin_logout():
    session.clear() # Limpa a sessão.
    flash('Você saiu da área administrativa.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/download_relatorio/<int:relatorio_id>/<tipo>')
def download_relatorio(relatorio_id, tipo):
    if 'cliente_id' not in session:
        flash('Você precisa estar logado para baixar relatórios.', 'warning')
        return redirect(url_for('main.login'))

    cliente = Cliente.query.get(session['cliente_id'])

    # --- LÓGICA DE BUSCA SIMPLIFICADA ---
    conteudo = ""
    if tipo == 'basico':
        relatorio = RelatorioBasico.query.get_or_404(relatorio_id)
        conteudo = relatorio.conteudo
    elif tipo == 'intermediario':
        relatorio = RelatorioIntermediario.query.get_or_404(relatorio_id)
        conteudo = relatorio.conteudo
    elif tipo == 'avancado':
        relatorio = RelatorioAvancado.query.get_or_404(relatorio_id)
        conteudo = relatorio.conteudo # <-- CORRIGIDO
    else:
        flash('Tipo de relatório inválido.', 'danger')
    return redirect(url_for('main.relatorios_recentes'))

    # --- O RESTO DO SEU CÓDIGO ESTÁ PERFEITO ---
    if relatorio.cliente_id != cliente.id:
        flash('Você não tem permissão para baixar este relatório.', 'danger')
        return redirect(url_for('main.relatorios_recentes'))

    # GERA O PDF
#    pdf = FPDF()
#    pdf.add_page()
#    pdf.set_font('Arial', '', 12)
#    pdf.cell(0, 10, f'Relatorio Tecnico - {tipo.title()}', ln=True, align='C')
#    pdf.cell(0, 10, f"Gerado em: {relatorio.data_criacao.strftime('%d/%m/%Y')}", ln=True, align='C')
#    pdf.ln(10)
#    pdf.multi_cell(0, 5, conteudo)
#    pdf_output = pdf.output() 
    
#    return Response(
#        pdf_output,
#        mimetype='application/pdf',
#        headers={
#            'Content-Disposition': f'attachment; filename="relatorio_{tipo}_{relatorio_id}.pdf"'
#        }
#    )
'''