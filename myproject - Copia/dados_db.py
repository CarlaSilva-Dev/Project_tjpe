# =========================================================
# INSERIR DADOS ALEATÓRIOS - PROCESSOS
# =========================================================

import sqlite3
from datetime import datetime
import random

DATABASE = "database.db"

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Listas para gerar dados aleatórios
comarcas = [
    "Recife", "Olinda", "Paulista", "Jaboatão dos Guararapes",
    "Abreu e Lima", "Igarassu", "Camaragibe", "Moreno",
    "Ipojuca", "São Lourenço da Mata", "Itamaracá",
    "Araçoiaba", "Itapissuma"
]

status_lista = [
    "Em tramitação", "Julgado", "Arquivado"
]

tipos_usucapiao = [
    "Extraordinária", "Ordinária", "Especial Urbana", 
    "Especial Rural", "Familiar", "Coletiva", "Indígena"
]

autores = ["João Silva", "Maria Oliveira", "Carlos Santos", "Ana Souza"]
reus = ["Pedro Lima", "Lucas Rocha", "Fernanda Costa", "Rafael Alves"]
observacoes = [
    "Processo urgente.",
    "Aguardando documentação.",
    "Revisão necessária.",
    "Prioridade baixa."
]

# Conexão com o banco
conn = get_connection()
cursor = conn.cursor()

# Gerar 20 processos aleatórios
for i in range(20):
    numero = f"PROC{1000 + i}"
    autor = random.choice(autores)
    reu = random.choice(reus)
    comarca = random.choice(comarcas)
    status = random.choice(status_lista)
    tipo_usucapiao = random.choice(tipos_usucapiao)
    observacao = random.choice(observacoes)
    data_cadastro = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        INSERT INTO processos (
            numero, autor, reu, comarca, status, tipo_usucapiao, observacoes, data_cadastro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (numero, autor, reu, comarca, status, tipo_usucapiao, observacao, data_cadastro))

conn.commit()
conn.close()
print("20 processos aleatórios inseridos com sucesso!")