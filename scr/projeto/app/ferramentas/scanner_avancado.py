import requests
import socket # Para o scan de portas
import ssl      # Para checar HSTS
import json

# Função auxiliar para checar portas (exemplo simples)
def checar_porta(alvo, porta):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # 1 segundo de timeout
        resultado = sock.connect_ex((alvo, porta))
        sock.close()
        return resultado == 0 # True se a porta estiver aberta
    except socket.gaierror:
        return False # Se o domínio não for resolvido
    except socket.error:
        return False

# Função auxiliar para checar HSTS
def checar_hsts(alvo):
    try:
        # Tenta conectar via HTTPS
        conn = ssl.create_default_context().wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=alvo
        )
        conn.connect((alvo, 443))
        
        # O HSTS é um header HTTP, então precisamos fazer uma requisição
        response = requests.get(f"https://{alvo}", timeout=5)
        
        if 'Strict-Transport-Security' in response.headers:
            return f"CONFIGURADO: {response.headers['Strict-Transport-Security']}"
        else:
            return "FALHA: Header 'Strict-Transport-Security' ausente."
            
    except requests.exceptions.SSLError:
        return "FALHA: Erro de SSL (pode não suportar HTTPS)."
    except Exception as e:
        return f"FALHA: Não foi possível conectar em HTTPS ({e})"

# --- Sua Função Principal ---
def rodar_scan_avancado(dominio_alvo):
    """
    Executa os scans avançados e retorna uma string
    com o relatório técnico.
    """
    
    # É uma boa prática formatar relatórios técnicos com JSON ou Markdown
    # Vou usar uma string simples por enquanto.
    
    print(f"[SCAN] Iniciando scan avançado em {dominio_alvo}...")
    
    relatorio_tecnico = f"## Relatório Técnico Avançado: {dominio_alvo}\n\n"
    
    # --- 1. Teste de HSTS ---
    relatorio_tecnico += "### Verificação de HSTS (Strict-Transport-Security):\n"
    resultado_hsts = checar_hsts(dominio_alvo)
    relatorio_tecnico += f"- Status: {resultado_hsts}\n\n"
    
    # --- 2. Scan de Portas ---
    relatorio_tecnico += "### Verificação de Portas Comuns:\n"
    portas_para_checar = [80, 443, 22, 21, 3306, 5432]
    
    for porta in portas_para_checar:
        if checar_porta(dominio_alvo, porta):
            relatorio_tecnico += f"- [ALERTA] Porta {porta} está ABERTA.\n"
        else:
            relatorio_tecnico += f"- [OK] Porta {porta} está FECHADA.\n"
            
    # Adicione mais lógicas de scan aqui...
    
    print(f"[SCAN] Scan em {dominio_alvo} concluído.")
    
    return relatorio_tecnico