# 📋 Project TJPE

Sistema web desenvolvido como projeto prático da disciplina de DevOps (AV2) — UNINASSAU.

## 📖 Descrição

Aplicação web com tema voltado ao Tribunal de Justiça de Pernambuco (TJPE), desenvolvida com arquitetura Full-Stack integrando práticas modernas de DevOps, incluindo controle de versão com Git, containerização com Docker e automação com GitHub Actions.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Banco de Dados | SQL (SQLite) |
| Containerização | Docker |
| CI/CD | GitHub Actions |
| Controle de Versão | Git + GitHub |

---

## 🚀 Guia de Instalação

### Pré-requisitos
- [Docker](https://www.docker.com/) instalado na máquina

### Rodando com Docker

```bash
# 1. Clone o repositório
git clone https://github.com/CarlaSilva-Dev/Project_tjpe.git

# 2. Entre na pasta do projeto
cd Project_tjpe

# 3. Build da imagem Docker
docker build -t project_tjpe .

# 4. Execute o container
docker run -p 5000:5000 project_tjpe
```

Acesse no navegador: [http://localhost:5000](http://localhost:5000)

### Rodando sem Docker (ambiente local)

```bash
# 1. Clone o repositório
git clone https://github.com/CarlaSilva-Dev/Project_tjpe.git
cd Project_tjpe

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
flask run
```

---

## ⚙️ Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_aqui
```

> ⚠️ **Nunca** suba o arquivo `.env` para o repositório!

---

## 👥 Membros da Squad

| Nome | GitHub |
|------|--------|
| Carla Rayanne | [@CarlaSilva-Dev](https://github.com/CarlaSilva-Dev) |
| Arnaldo Reis | [@Arnaldoreisl](https://github.com/Arnaldoreisl) |
| Higor Ricardo | — |
| Gustavo Lopes | [@gustavolopeslima](https://github.com/gustavolopeslima) |

---

## 📊 Status CI/CD

![Docker Build](https://github.com/CarlaSilva-Dev/Project_tjpe/actions/workflows/docker-build.yml/badge.svg)

---

*Projeto desenvolvido para a disciplina de DevOps — UNINASSAU 2026*
