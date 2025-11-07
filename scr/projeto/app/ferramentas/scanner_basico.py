import requests
import socket
import ssl
import json

def checar_porta(alvo, porta):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        resultado = sock.connect_ex((alvo, porta))
        sock.close()
        return resultado == 0
    except socket.gaierror:
        return False
    except socket.error:
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

def rodar_scan_basico(dominio_alvo):
    
    print(f"[SCAN] Iniciando scan básico em {dominio_alvo}...")
    
    relatorio_basico = f"Relatório de Saúde do Site: {dominio_alvo}\n\n"
    
    relatorio_basico += "🔒 O 'Cadeado' de Segurança (HTTPS)\n"
    resultado_hsts = checar_hsts(dominio_alvo)
    
    if "CONFIGURADO" in resultado_hsts:
        relatorio_basico += (
            "Status: ✅ Excelente!\n"
            "Seu site está configurado para *sempre* usar a conexão segura (o cadeado). Isso significa que os dados dos seus visitantes estão sendo bem protegidos quando eles navegam no seu site.\n\n"
        )
    else:
        relatorio_basico += (
            "Status: 🔴 Risco!\n"
            "Seu site tem um cadeado (HTTPS), mas ele não está configurado para ser 'permanente'. Isso cria uma brecha de segurança onde invasores podem tentar 'destrancar' a conexão sem que o usuário perceba.\n"
            "Ação Recomendada: Peça ao seu desenvolvedor para ativar o 'HSTS'.\n\n"
        )
            
    relatorio_basico += "### 🚪 Portas de Serviço do Servidor\n"
    
    portas_de_risco = [22, 21, 3306, 5432]
    
    riscos_encontrados = []
    
    for porta in portas_de_risco:
        if checar_porta(dominio_alvo, porta):
            riscos_encontrados.append(porta)
        
    if riscos_encontrados:
        relatorio_basico += (
            "**Status: ⚠️ Atenção!**\n"
            "Nosso scan identificou que algumas 'portas dos fundos' do seu servidor estão destrancadas e visíveis na internet. Pense nisso como deixar a porta da sala de controle ou do cofre aberta.\n"
            "**Ação Recomendada:** Isso é um risco de segurança. Entre em contato com seu técnico de T.I. imediatamente e peça para ele revisar e fechar todas as portas de serviço desnecessárias.\n"
        )
    else:
        relatorio_basico += (
            "**Status: ✅ Ótimo.**\n"
            "As 'portas dos fundos' mais comuns do seu servidor parecem estar devidamente trancadas. Isso é uma ótima prática de segurança e dificulta o acesso de invasores.\n"
        )
            
    print(f"[SCAN] Scan básico em {dominio_alvo} concluído.")
    
    return relatorio_basico