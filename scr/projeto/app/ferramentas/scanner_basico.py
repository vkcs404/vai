import socket

# --- Função Auxiliar ---

def checar_porta(alvo, porta):
    """
    Verifica se uma porta específica está aberta em um domínio.
    """
    try:
        # Cria um "conector" de rede
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Define um tempo limite curto (1 segundo)
        sock.settimeout(1)
        # Tenta se conectar à porta
        resultado = sock.connect_ex((alvo, porta))
        # Fecha a conexão
        sock.close()
        # Se o resultado for 0, a porta está aberta
        return resultado == 0
    except (socket.gaierror, socket.error):
        # Se o domínio não existir ou der erro, assume que está fechada
        return False

# ###############################################################
# --- FUNÇÃO PRINCIPAL DO SCAN BÁSICO ---
# ###############################################################
def rodar_scan_basico(dominio_alvo):
    """
    Executa um scan focado em linguagem simples, explicando
    os conceitos de HTTP e HTTPS.
    """
    print(f"[SCAN BÁSICO] Iniciando scan básico em {dominio_alvo}...")

    # --- Passo 1: Coletar os dados ---
    # O scan básico foca apenas nas duas portas principais da web

    # Porta 80 = HTTP (A conexão "normal", insegura)
    http_ativo = checar_porta(dominio_alvo, 80)
    
    # Porta 443 = HTTPS (A conexão "segura", com cadeado)
    https_ativo = checar_porta(dominio_alvo, 443)

    # --- Passo 2: Construir o relatório educativo ---
    
    relatorio = "" # Começa com a string vazia
    
    relatorio += "--- Relatório de Segurança Básico ---\n\n"

    # --- Verificação 1: HTTPS (O Cadeado 🔒) ---
    relatorio += "1. Conexão Segura (HTTPS / Porta 443)\n"
    relatorio += "   " + ("-" * 20) + "\n"
    
    if https_ativo:
        relatorio += "   [BOM]  Seu site parece ter uma conexão segura (HTTPS) ativa.\n"
        relatorio += "   Isso é ótimo! É o que permite o 'cadeado' 🔒 no navegador.\n"
    else:
        relatorio += "   [RISCO] ❌ Seu site NÃO parece ter uma conexão segura (HTTPS).\n"
        relatorio += "   Sem isso, os dados dos seus visitantes não são protegidos.\n"
    
    relatorio += "\n\n" # Duas linhas em branco

    # --- Verificação 2: HTTP (A Conexão Antiga) ---
    relatorio += "2. Conexão Insegura (HTTP / Porta 80)\n"
    relatorio += "   " + ("-" * 20) + "\n"
    
    if http_ativo:
        relatorio += "   [ALERTA] ⚠️ Seu site ainda permite conexões inseguras (HTTP).\n"
        relatorio += "   Isso é um risco. O ideal é que todos que tentam acessar\n"
        relatorio += "   a versão 'http://' sejam forçados a usar a 'https://'.\n"
    else:
        relatorio += "   [BOM] ✅ Seu site parece bloquear conexões inseguras.\n"
        relatorio += "   Isso é uma boa prática de segurança.\n"

    relatorio += "\n\n"

    # --- Seção Educativa ---
    relatorio += "--- O que isso significa? ---\n\n"
    
    relatorio += "Pense no HTTPS (Porta 443) como uma 'carta registrada e lacrada'.\n"
    relatorio += "Só você e seu visitante podem ler. Isso protege senhas e dados.\n\n"
    
    relatorio += "Pense no HTTP (Porta 80) como um 'cartão-postal'.\n"
    relatorio += "Qualquer um no caminho (hackers, provedor de internet) pode ler\n"
    relatorio += "o que está escrito. \n\n"
    
    relatorio += "RECOMENDAÇÃO BÁSICA:\n"
    relatorio += "1. Garanta que seu site tenha um 'Certificado SSL' (para ativar o HTTPS).\n"
    relatorio += "2. Configure seu servidor para redirecionar todo o tráfego da Porta 80\n"
    relatorio += "   (HTTP) para a Porta 443 (HTTPS).\n"
    
    
    print(f"[SCAN BÁSICO] Scan em {dominio_alvo} concluído.")
    
    return relatorio