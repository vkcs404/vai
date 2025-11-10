from . import db  # Importa a instância do SQLAlchemy (db) que foi criada em app/__init__.py. 
from datetime import datetime # Importa classe datetime para registrar quando os relatórios foram criados.

#Define as estruturas de dados do seu banco - Crucial para a consulta de dados.

# ######################################################################
# MODELO CLIENTE (Com o campo 'nivel_acesso')
# ######################################################################

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Define a coluna ID como chave primária, única e autoincrementável.
    cliente_nome = db.Column(db.String(80), nullable=False)  # Define a coluna nome do cliente
    cliente_email = db.Column(db.String(320), unique=True, nullable=False)  # Armazena o e-mail, deve ser único e é obrigatório (usado para login).
    cliente_senha = db.Column(db.String(128), nullable=False)  # Armazena o hash da senha
    nome_bia = db.Column(db.String(80), nullable=False) 
    cliente_status = db.Column(db.String(10), nullable=False, default='ativo')
    nivel_acesso = db.Column(db.String(20), nullable=False, default='basico') #1 cliente só pode ter 1 nível
    relatorios_basicos = db.relationship('RelatorioBasico', backref='cliente', lazy=True, cascade="all, delete-orphan")  # # Define a relação "Um para Muitos" com RelatorioBasico. 'backref' permite acessar o cliente a partir do relatório, e 'cascade' garante que relatórios sejam excluídos ao deletar o cliente.
    relatorios_intermediarios = db.relationship('RelatorioIntermediario', backref='cliente', lazy=True, cascade="all, delete-orphan")       # Um cliente pode ter VÁRIOS relatórios intermediários
    relatorios_avancados = db.relationship('RelatorioAvancado', backref='cliente', lazy=True, cascade="all, delete-orphan")       # Um cliente pode ter VÁRIOS relatórios avançados

    def __repr__(self):
        return f'<Cliente {self.cliente_nome} ({self.nivel_acesso})>'


# MODELOS DE RELATÓRIO

# --- MODELO BÁSICO ---
class RelatorioBasico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)  ## Armazena o resultado textual do escaneamento (o relatório em si).
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Regra dos 30 dias (baseada na data de criação) - # Registra a data de criação. 'datetime.utcnow' garante o uso de fuso horário UTC 
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False) # Chave estrangeira que liga o relatório ao seu cliente via ID(Dono).

    def __repr__(self):
        return f'<RelatorioBasico {self.id}>'
    

    #RELATORIO INTERMEDIARIO
class RelatorioIntermediario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    def __repr__(self):
        return f'<RelatorioIntermediario {self.id}>'


    #RELATORIO AVANÇADO
class RelatorioAvancado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

    def __repr__(self):
        return f'<RelatorioAvancado {self.id}>'


# ADMINISTRADOR
class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_nome = db.Column(db.String(80), nullable=False)
    admin_email = db.Column(db.String(320), unique=True, nullable=False)
    admin_senha = db.Column(db.String(128), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Administrador {self.admin_nome}>'
