import requests
import socket # Para o scan de portas
import ssl      # Para checar HSTS
import json

# --- Funções Auxiliares (mantidas iguais) ---

# Função auxiliar para checar portas (exemplo simples)
def checar_porta(alvo, porta):
    """Verifica se uma porta está aberta no alvo."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 segundo de timeout
        resultado = sock.connect_ex((alvo, porta))
        sock.close()
        return resultado == 0 # True se a porta estiver aberta
    except socket.gaierror:
        return False
    except socket.error:
        return False

# Função auxiliar para checar HSTS
def checar_hsts(alvo):
    """Verifica a configuração do Strict-Transport-Security (HSTS)."""
    try:
        # Tenta conectar via HTTPS
        conn = ssl.create_default_context().wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=alvo
        )
        conn.connect((alvo, 443))
        
        # Faz uma requisição para obter os headers
        response = requests.get(f"https://{alvo}", timeout=5)
        
        if 'Strict-Transport-Security' in response.headers:
            return f"CONFIGURADO: {response.headers['Strict-Transport-Security']}"
        else:
            return "FALHA: Header 'Strict-Transport-Security' ausente."
            
    except requests.exceptions.SSLError:
        return "FALHA: Erro de SSL (pode não suportar HTTPS)."
    except Exception as e:
        return f"FALHA: Não foi possível conectar em HTTPS ({e})"

# ----------------------------------------------------------------------
# --- NOVA FUNÇÃO: SCAN INTERMEDIÁRIO (Linguagem Simplificada) ---
# ----------------------------------------------------------------------

def rodar_scan_intermediario(dominio_alvo):
    """
    Executa os scans e retorna um relatório com linguagem menos técnica.
    Focado em Segurança e Usabilidade.
    """
    
    print(f"[SCAN] Iniciando scan intermediário em {dominio_alvo}...")
    
    relatorio_intermediario = f"## Relatório Intermediário de Segurança: {dominio_alvo}\n\n"
    
    # --- 1. Checagem de HSTS (Linguagem não técnica) ---
    relatorio_intermediario += "### 🔒 Proteção HTTPS Permanente (HSTS)\n"
    resultado_hsts = checar_hsts(dominio_alvo)
    
    if "CONFIGURADO" in resultado_hsts:
        relatorio_intermediario += (
            "**Status: ✅ Configurado.**\n"
            "O seu site está configurado para forçar a conexão HTTPS (criptografada) de forma permanente nos navegadores dos usuários. Isso aumenta muito a segurança contra ataques de interceptação.\n\n"
        )
    else:
        relatorio_intermediario += (
            f"**Status: 🔴 Atenção!**\n"
            f"A configuração HSTS (Strict-Transport-Security) está ausente ou falhou. Sem essa proteção, seu site está vulnerável a ataques que tentam rebaixar a conexão de HTTPS para HTTP (não seguro).\n"
            f"Detalhe Técnico: {resultado_hsts}\n\n"
        )
            
    # --- 2. Scan de Portas (Focado no risco) ---
    relatorio_intermediario += "### 🚪 Status de Portas de Servidor\n"
    portas_para_checar = {
        80: "HTTP (Web Não Criptografada)", 
        443: "HTTPS (Web Criptografada)", 
        22: "SSH (Acesso Remoto Seguro)", 
        21: "FTP (Transferência de Arquivos)", 
        3306: "MySQL (Banco de Dados)", 
    }
    
    portas_abertas = []
    
    for porta, descricao in portas_para_checar.items():
        if checar_porta(dominio_alvo, porta):
            portas_abertas.append(f"Porta {porta} ({descricao}) está ABERTA.")
        
    if portas_abertas:
        relatorio_intermediario += (
            "**Status: ⚠️ Algumas portas de serviço estão abertas.**\n"
            "Portas abertas podem ser um risco se não estiverem sendo ativamente monitoradas e protegidas. Recomendamos revisar e fechar as portas desnecessárias.\n"
        )
        for p in portas_abertas:
            relatorio_intermediario += f"- {p}\n"
    else:
        relatorio_intermediario += (
            "**Status: ✅ Boas Práticas de Portas.**\n"
            "As portas de serviço mais comuns estão fechadas ou protegidas, indicando uma boa configuração de firewall básica.\n"
        )
            
    print(f"[SCAN] Scan intermediário em {dominio_alvo} concluído.")
    
    return relatorio_intermediario