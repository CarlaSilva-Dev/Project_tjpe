# Projeto TJPE - Sistema de Processos Judiciais

## Descrição

Sistema web para gerenciamento de processos judiciais do Tribunal de Justiça de Pernambuco (TJPE). A aplicação permite o registro, acompanhamento e análise de processos, com funcionalidades de auditoria, geração de relatórios e visualização em dashboard.

**Problema Resolvido**: Centralizar e automatizar o gerenciamento de processos judiciais, facilitando o acesso às informações e a geração de relatórios para análise de dados.

---

## Tecnologias Utilizadas

### Backend
- **Flask** 3.0.3 - Framework web Python
- **SQLite** - Banco de dados (development)
- **ReportLab** - Geração de PDF

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização
- **JavaScript** - Interatividade e dashboard

### DevOps
- **Docker** - Containerização
- **GitHub Actions** - CI/CD
- **Git** - Controle de versão

---

## Requisitos Atendidos

**Controle de Versão (Git)**
- Repositório limpo com `.gitignore`
- Histórico de commits rastreável
- Variáveis sensíveis em `.env`

**Containerização (Docker)**
- Dockerfile otimizado com multi-stage build
- Isolamento completo de dependências
- Health check integrado

**CI/CD (GitHub Actions)**
- Workflow automático de build a cada push
- Validação da imagem Docker
- Cache inteligente de layers

**Documentação**
- README.md completo
- Instruções de execução
- Guias de instalação

---

## Guia de Instalação e Execução

### Pré-requisitos
- Git
- Docker e Docker Compose (para execução com Docker)
- Python 3.11+ (para execução local)

### Clone o Repositório

```bash
git clone <seu-repositorio>
cd Project_tjpe
```

---

## Opção 1: Execução com Docker (Recomendado)

### Build da Imagem

```bash
docker build -t project-tjpe:latest .
```

### Executar o Container

```bash
docker run -d \
  --name project-tjpe \
  -p 5000:5000 \
  -v $(pwd)/projeto_todo/database.db:/app/database.db \
  project-tjpe:latest
```

**Ou com Docker Compose**:

```bash
docker-compose up -d
```

A aplicação estará disponível em: **http://localhost:5000**

### Verificar Status

```bash
docker ps
docker logs project-tjpe
docker exec project-tjpe curl http://localhost:5000/health
```

### Parar o Container

```bash
docker stop project-tjpe
docker rm project-tjpe
```

---

## Opção 2: Execução Local (Sem Docker)

### 1. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r projeto_todo/requirements.txt
```

### 3. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env (já incluído no repositório)
# As variáveis já estão configuradas em .env
```

### 4. Inicializar Banco de Dados

```bash
cd projeto_todo
python init_db.py
```

### 5. Executar a Aplicação

```bash
python projeto_tj.py
```

A aplicação estará disponível em: **http://localhost:5000**

---

## Funcionalidades Implementadas

### Autenticação
- Sistema de login com hash de senha
- Controle de sessão

### Gerenciamento de Processos
- CRUD completo de processos
- Visualização em lista e detalhes
- Modal de edição

### Auditoria
- Registro de alterações
- Histórico de operações

### Relatórios
- Geração de relatórios em PDF
- Visualização de relatórios salvos
- Dashboard com estatísticas

### Usuários
- Gestão de usuários
- Diferentes perfis de acesso

---

## Estrutura do Projeto

```
Project_tjpe/
├── projeto_todo/
│   ├── projeto_tj.py          # Aplicação principal Flask
│   ├── init_db.py             # Inicialização do banco de dados
│   ├── dados_db.py            # Dados iniciais
│   ├── mesclar.py             # Utilitário de merge de dados
│   ├── requirements.txt        # Dependências Python
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── dashboard.js
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── dashboard.html
│       ├── usuarios_lista.html
│       ├── processos_lista.html
│       ├── relatorios.html
│       └── ...
├── Dockerfile                 # Containerização
├── .github/
│   └── workflows/
│       └── docker-build.yml   # CI/CD Pipeline
├── .gitignore                 # Arquivos ignorados pelo Git
├── .env                       # Variáveis de ambiente
└── README.md                  # Este arquivo
```

---

## Segurança

- Secret key gerenciado via `.env`
- Arquivo `.env` adicionado ao `.gitignore`
- Nenhuma credencial hardcoded no código
- Hash de senhas com SHA-256
- Validação de entrada em formulários

---

## Variáveis de Ambiente

Edite o arquivo `.env` para configurar:

```env
FLASK_ENV=development|production
SECRET_KEY=sua_chave_secreta
DATABASE_PATH=caminho/do/banco.db
FLASK_DEBUG=0|1
```

---

## Testes

```bash
# Verificar se a aplicação inicia
python projeto_tj.py

# Acessar em um navegador
# http://localhost:5000
```

---

## Membros da Equipe

- [Nome do Integrante 1]
- [Nome do Integrante 2]
- [Nome do Integrante 3]
- [Nome do Integrante 4]

---

## Licença

Este projeto está licenciado sob a [Especificar Licença]

        
---

**Última atualização**: 20 de maio de 2026