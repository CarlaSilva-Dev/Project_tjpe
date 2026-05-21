# =========================================================
# INSERIR DADOS ALEATÓRIOS - PROCESSOS + USUÁRIOS
# =========================================================

import sqlite3
from datetime import datetime, timedelta
import random
import hashlib

DATABASE = "database.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# =========================================================
# LISTAS
# =========================================================

comarcas = [
    "Recife", "Olinda", "Paulista", "Jaboatão dos Guararapes",
    "Abreu e Lima", "Igarassu", "Camaragibe", "Moreno",
    "Ipojuca", "São Lourenço da Mata", "Itamaracá",
    "Araçoiaba", "Itapissuma"
]

status_lista = [
    "Em tramitação", "Julgado", "Arquivado", "Suspenso"
]

tipos_usucapiao = [
    "Extraordinária", "Ordinária", "Especial Urbana",
    "Especial Rural", "Familiar", "Coletiva", "Indígena"
]

autores = [
    "João Silva", "Maria Oliveira", "Carlos Santos", "Ana Souza",
    "Beatriz Ferreira", "Ricardo Mendes", "Patrícia Nunes", "Eduardo Lima",
    "Fernanda Costa", "Marcos Pereira", "Juliana Alves", "Rodrigo Gomes",
    "Camila Barros", "Diego Carvalho", "Larissa Monteiro", "Felipe Ramos",
    "Tatiane Moura", "Gustavo Freitas", "Renata Cavalcanti", "André Pinto"
]

reus = [
    "Pedro Lima", "Lucas Rocha", "Rafael Alves", "Vanessa Teixeira",
    "Bruno Cardoso", "Isabela Martins", "Thiago Araújo", "Natália Ribeiro",
    "Caio Lopes", "Priscila Nascimento", "Henrique Vieira", "Amanda Correia",
    "Leandro Fonseca", "Simone Batista", "Fábio Rezende", "Carla Melo",
    "Sérgio Andrade", "Mônica Dias", "Vinícius Castro", "Luciana Sampaio"
]

observacoes = [
    "Processo urgente.",
    "Aguardando documentação.",
    "Revisão necessária.",
    "Prioridade baixa.",
    "Citação realizada, aguardando resposta.",
    "Perícia técnica solicitada.",
    "Audiência agendada.",
    "Recurso interposto.",
    "Aguardando manifestação do MP.",
    "Documentação incompleta.",
    "Prazo em curso.",
    "Processo em fase de instrução.",
    "Sentença proferida, aguardando trânsito em julgado.",
    "Réu não localizado para citação.",
    "Processo redistribuído por prevenção."
]

# =========================================================
# CONEXÃO
# =========================================================

conn = get_connection()
cursor = conn.cursor()

# =========================================================
# USUÁRIOS
# =========================================================

usuarios_novos = [
    {
        "nome": "Servidor TJPE",
        "email": "ser@tjpe.jus.br",
        "senha": hash_senha("ser123"),
        "perfil": "Servidor"
    },
    {
        "nome": "Magistrado TJPE",
        "email": "mag@tjpe.jus.br",
        "senha": hash_senha("mag123"),
        "perfil": "Magistrado"
    }
]

for u in usuarios_novos:
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, (u["nome"], u["email"], u["senha"], u["perfil"]))
        print(f"Usuário criado: {u['email']} ({u['perfil']})")
    except sqlite3.IntegrityError:
        print(f"Usuário já existe: {u['email']} — pulando.")

# =========================================================
# PROCESSOS
# =========================================================

# Gera datas aleatórias nos últimos 2 anos
def data_aleatoria():
    dias = random.randint(0, 730)
    data = datetime.now() - timedelta(days=dias)
    return data.strftime("%d/%m/%Y")

inseridos = 0
tentativas = 0

while inseridos < 100 and tentativas < 500:
    tentativas += 1
    numero = f"PROC{2000 + tentativas:04d}"

    # Verifica se número já existe
    existente = cursor.execute(
        "SELECT id FROM processos WHERE numero = ?", (numero,)
    ).fetchone()

    if existente:
        continue

    autor = random.choice(autores)
    reu = random.choice(reus)
    comarca = random.choice(comarcas)
    status = random.choice(status_lista)
    tipo_usucapiao = random.choice(tipos_usucapiao)
    observacao = random.choice(observacoes)
    data_cadastro = data_aleatoria()

    cursor.execute("""
        INSERT INTO processos (
            numero, autor, reu, comarca, status, tipo_usucapiao, observacoes, data_cadastro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (numero, autor, reu, comarca, status, tipo_usucapiao, observacao, data_cadastro))

    inseridos += 1

conn.commit()
conn.close()

print(f"\n{inseridos} processos inseridos com sucesso!")
print("Usuários disponíveis:")
print("  admin@tjpe.jus.br  |  senha: Admin123  |  perfil: Administrador")
print("  ser@tjpe.jus.br  |  senha: ser123  |  perfil: Servidor")
print("  mag@tjpe.jus.br  |  senha: mag123  |  perfil: Magistrado")