// Ouve o evento de submissão do formulário. Quando o botão é clicado, esta função é executada.
document.getElementById('urlForm').addEventListener('submit', function(event) {
    
    // Impede que a página recarregue ao submeter o formulário.
    event.preventDefault(); 
    
    // 1. Obtém o valor digitado no campo de input.
    const urlInput = document.getElementById('urlInput');
    const url = urlInput.value.trim(); // Pega o texto e remove espaços extras
    const feedbackDiv = document.getElementById('feedback');
    
    // Limpa mensagens e estilos de feedback anteriores.
    feedbackDiv.textContent = '';
    feedbackDiv.className = '';

    // ====================================================================
    // LÓGICA DE VALIDAÇÃO SIMPLIFICADA
    // Verifica duas condições básicas para ser "válida"
    // 1. Se a URL não está vazia (url.length > 0)
    // 2. Se a URL contém um ponto (url.includes('.'))
    // ====================================================================

    if (url.length > 0 && url.includes('.')) {
        
        // --- Critério de Aceite 1: URL Válida -> Inicia a Análise ---
        
        // Informa que a análise foi iniciada (simulação).
        feedbackDiv.textContent = `✅ URL APROVADA: Análise de portas iniciada para "${url}".`;
        
        // Aplica o estilo de sucesso.
        feedbackDiv.classList.add('valid');
        
        // Se estivéssemos em um projeto real, aqui você faria a chamada para o servidor.
        // Exemplo: enviarParaServidor(url); 

    } else {
        
        // --- Critério de Aceite 2: URL Inválida -> Exibe Mensagem de Erro ---
        
        // Mensagem de erro.
        feedbackDiv.textContent = '❌ Erro: URL/IP inválida. Deve conter um endereço (ex: site.com) e um ponto.';
        
        // Aplica o estilo de erro.
        feedbackDiv.classList.add('invalid');
    }
});