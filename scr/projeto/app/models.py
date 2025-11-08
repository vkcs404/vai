from . import db
from datetime import datetime # Importe o datetime para usar em timestamps

# ######################################################################
# MODELO CLIENTE (Com o campo 'nivel_acesso')
# ######################################################################

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    cliente_nome = db.Column(db.String(80), nullable=False) 
    cliente_email = db.Column(db.String(320), unique=True, nullable=False)
    cliente_senha = db.Column(db.String(128))
    cliente_status = db.Column(db.String(10), nullable=False, default='ativo')
    nivel_acesso = db.Column(db.String(20), nullable=False, default='basico') #1 cliente só pode ter 1 nível
    relatorios_basicos = db.relationship('RelatorioBasico', backref='cliente', lazy=True, cascade="all, delete-orphan")  #    # Um cliente pode ter VÁRIOS relatórios básicos
    relatorios_intermediarios = db.relationship('RelatorioIntermediario', backref='cliente', lazy=True, cascade="all, delete-orphan")       # Um cliente pode ter VÁRIOS relatórios intermediários
    relatorios_avancados = db.relationship('RelatorioAvancado', backref='cliente', lazy=True, cascade="all, delete-orphan")       # Um cliente pode ter VÁRIOS relatórios avançados

    def __repr__(self):
        return f'<Cliente {self.cliente_nome} ({self.nivel_acesso})>'

# MODELOS DE RELATÓRIO (Requisito: 3 níveis)


# --- MODELO BÁSICO ---
class RelatorioBasico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.Text, nullable=False)  #conteudo eh texto
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Regra dos 30 dias (baseada na data de criação)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False) # ID(O 'Dono' do relatório)

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


# ######################################################################
# MODELO ADMINISTRADOR
# ######################################################################

class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_nome = db.Column(db.String(80), nullable=False)
    admin_email = db.Column(db.String(320), unique=True, nullable=False)
    admin_senha = db.Column(db.String(128), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Administrador {self.admin_nome}>'
