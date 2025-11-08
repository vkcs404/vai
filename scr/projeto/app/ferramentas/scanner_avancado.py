# Em app/ferramentas/scanner_avancado.py

import requests
import socket
import ssl
import json

# --- Suas funções auxiliares (checar_porta e checar_hsts) ---
# --- Não precisam de NENHUMA mudança. Deixe-as como estão. ---

def checar_porta(alvo, porta):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        resultado = sock.connect_ex((alvo, porta))
        sock.close()
        return resultado == 0
    except (socket.gaierror, socket.error):
        return False

def checar_hsts(alvo):
    try:
        conn = ssl.create_default_context().wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=alvo
        )
        conn.connect((alvo, 443))
        response = requests.get(f"https://{alvo}", timeout=5)
        
        if 'Strict-Transport-Security' in response.headers:
            return f"CONFIGURADO: {response.headers['Strict-Transport-Security']}"
        else:
            return "FALHA: Header 'Strict-Transport-Security' ausente."
            
    except requests.exceptions.SSLError:
        return "FALHA: Erro de SSL (pode não suportar HTTPS)."
    except Exception as e:
        return f"FALHA: Não foi possível conectar em HTTPS ({e})"

# ###############################################################
# --- SUA FUNÇÃO PRINCIPAL (ATUALIZADA) ---
# ###############################################################
def rodar_scan_avancado(dominio_alvo):
    """
    Executa os scans avançados e retorna uma string
    com o relatório técnico no formato solicitado.
    """
    print(f"[SCAN] Iniciando scan avançado em {dominio_alvo}...")
    
    # --- Passo 1: Coletar os dados primeiro ---
    
    # Coletando Portas
    portas_abertas = []
    portas_para_checar = [80, 443, 22, 21, 3306, 5432]
    for porta in portas_para_checar:
        if checar_porta(dominio_alvo, porta):
            portas_abertas.append(str(porta)) # Salva o número da porta

    # Coletando Cabeçalhos
    # (Por enquanto só temos HSTS, mas podemos adicionar mais)
    status_hsts = checar_hsts(dominio_alvo)
    # Ex: status_x_frame = checar_x_frame(dominio_alvo)
    
    
    # --- Passo 2: Construir a string do relatório ---
    
    relatorio_tecnico = "" # Começa com a string vazia
    
    # --- Seção Portas Abertas ---
    relatorio_tecnico += "Portas Abertas\n"
    relatorio_tecnico += "   " + ("-" * 20) + "\n" # Linha de separação
    
    if not portas_abertas:
        relatorio_tecnico += "   Nenhuma porta comum (80, 443, 22, 21, 3306, 5432) aberta.\n"
    else:
        # Junta a lista de portas: ['80', '443'] -> "80, 443"
        lista_de_portas = ", ".join(portas_abertas)
        relatorio_tecnico += f"   Portas encontradas: {lista_de_portas}\n"
    
    relatorio_tecnico += "\n\n" # Duas linhas em branco
    
    # --- Seção Cabeçalho de Segurança ---
    relatorio_tecnico += "Cabeçalho de Segurança\n"
    relatorio_tecnico += "   " + ("-" * 20) + "\n"
    
    # Nomes técnicos (um por linha)
    relatorio_tecnico += f"   Strict-Transport-Security (HSTS): {status_hsts}\n"
    # relatorio_tecnico += f"   X-Frame-Options: {status_x_frame}\n"
    # relatorio_tecnico += f"   X-Content-Type-Options: ...\n"
    
    print(f"[SCAN] Scan em {dominio_alvo} concluído.")
    
    return relatorio_tecnico