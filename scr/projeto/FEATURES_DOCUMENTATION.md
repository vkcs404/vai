# Sistema VAI - Documentação das Melhorias

## Visão Geral
Sistema de scanner de segurança para sites com três níveis de relatórios: básico, intermediário e avançado.

## Novas Funcionalidades Implementadas

### 1. Área do Usuário

#### Minha Conta (`/minha_conta`)
- Visualização de informações da conta
- Estatísticas de relatórios gerados
- Acesso rápido aos relatórios e ao scanner
- Opção de logout

#### Relatórios Recentes (`/relatorios_recentes`)
- Visualização de todos os relatórios dos últimos 30 dias
- Filtros por tipo de relatório (básico, intermediário, avançado)
- Acesso direto para visualização de relatórios individuais

#### Visualizar Relatório (`/visualizar_relatorio/<id>/<tipo>`)
- Visualização detalhada de um relatório específico
- Informações completas incluindo data e conteúdo
- Navegação fácil entre relatórios

### 2. Área do Administrador

#### Login Admin (`/admin/login`)
- Página de login exclusiva para administradores
- Autenticação separada do sistema de clientes

**Credenciais padrão:**
- Email: `admin@vai.com`
- Senha: `admin123`
- ⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

#### Dashboard Admin (`/admin/dashboard` ou `/listar_clientes`)
- Visualização de todos os clientes cadastrados
- Gerenciamento de status de clientes (ativar/desativar)
- Alteração de nível de acesso dos clientes
- Estatísticas do sistema

**Funcionalidades:**
- Ativar/Desativar clientes
- Alterar nível de acesso (básico, intermediário, avançado)
- Visualizar estatísticas gerais

### 3. Melhorias no Fluxo de Cadastro e Login

#### Página de Cadastro (`/cadastro`)
- Modal com Termos de Uso e LGPD
- Checkbox obrigatório para aceite
- Botão "Voltar para escolher relatório"
- Design consistente com o restante do sistema

#### Página de Login (`/login`)
- Design atualizado seguindo o padrão visual
- Botão "Voltar para escolher relatório"
- Validação de usuários ativos

#### Termos de Uso (`/termos`)
- Página dedicada com termos formatados
- Estilização consistente com o sistema
- Informações sobre LGPD e proteção de dados

### 4. Melhorias na Página de Scanner (`/scaner`)
- Seção "Relatórios Recentes" movida para página dedicada
- Link direto para visualizar relatórios emitidos
- Informações do tipo de relatório selecionado mantidas

### 5. Banco de Dados

#### Nova Tabela: Administrador
```python
Campos:
- id: Integer (Primary Key)
- admin_nome: String(80)
- admin_email: String(320) - Unique
- admin_senha: String(128) - Hash
- data_criacao: DateTime
```

#### Correções nos Modelos Existentes
- Corrigido `cliente_id` nas tabelas RelatorioIntermediario e RelatorioAvancado
- Corrigido método `__repr__` em RelatorioIntermediario

## Estrutura de Navegação

### Usuário Comum:
```
Home → Escolher Relatório → Login/Cadastro → Pagamento → Scanner
                                                              ↓
                                        Minha Conta ← Relatórios Recentes
```

### Administrador:
```
Home → Admin Login → Dashboard Admin
                          ↓
                    Gerenciar Clientes
```

## Rotas Adicionadas

### Rotas de Usuário:
- `GET /minha_conta` - Página da conta do usuário
- `GET /relatorios_recentes` - Lista de relatórios dos últimos 30 dias
- `GET /visualizar_relatorio/<id>/<tipo>` - Visualizar relatório específico
- `POST /logout` - Logout do usuário
- `GET /termos` - Página de termos de uso

### Rotas de Administrador:
- `GET /admin/login` - Página de login do admin
- `POST /admin/entrar` - Processar login do admin
- `GET /admin/dashboard` - Dashboard administrativo
- `GET /listar_clientes` - Listar todos os clientes
- `POST /admin/alternar_status/<id>` - Ativar/Desativar cliente
- `POST /admin/alterar_nivel/<id>` - Alterar nível de acesso
- `GET /admin/logout` - Logout do admin

## Como Usar

### Criando um Administrador
Execute o script `create_admin.py` para criar o usuário admin padrão:
```bash
python create_admin.py
```

### Iniciar o Sistema
```bash
python main.py
```

O sistema estará disponível em `http://localhost:5000`

## Padrão Visual

Todo o sistema mantém consistência visual com:
- Gradiente de fundo: `#000000` → `#03002b`
- Cor primária: `#00d4ff` (azul ciano)
- Cor secundária: `#ff9500` (laranja)
- Cor de destaque: `#ff0080` (rosa)
- Tipografia: Montserrat, Poppins, Roboto

## Segurança

### Autenticação
- Senhas criptografadas com `pbkdf2:sha256`
- Sessões separadas para usuários e administradores
- Verificação de status de conta no login
- Proteção de rotas administrativas

### Validações
- Verificação de propriedade de relatórios
- Validação de níveis de acesso
- Proteção contra injeção de dados
- Verificação de status de usuário (ativo/inativo)

## Próximos Passos Sugeridos

1. Adicionar campo `alvo` (URL escaneada) nas tabelas de relatórios
2. Implementar download de relatórios em PDF
3. Adicionar filtros e pesquisa na página de relatórios
4. Criar dashboard com gráficos e estatísticas
5. Implementar sistema de notificações
6. Adicionar recuperação de senha
7. Implementar auditoria de ações administrativas

## Suporte

Para questões ou suporte, entre em contato com a equipe de desenvolvimento.
