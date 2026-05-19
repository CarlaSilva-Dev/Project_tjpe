# =========================================================
# INIT DB - SISTEMA TJPE USUCAPIÃO
# =========================================================

import sqlite3
from projeto_tj import hash_senha

DATABASE = "database.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_connection()

    # =====================================================
    # USUÁRIOS
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL
    )
    """)

    # =====================================================
    # COMARCAS
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS comarcas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # =====================================================
    # TIPOS USUCAPIÃO
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tipos_usucapiao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # =====================================================
    # STATUS PROCESSO
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS status_processo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # =====================================================
    # PROCESSOS (CORRIGIDO)
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS processos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT UNIQUE NOT NULL,
        autor TEXT NOT NULL,
        reu TEXT NOT NULL,
        comarca TEXT NOT NULL,
        status TEXT NOT NULL,
        tipo_usucapiao TEXT NOT NULL,
        observacoes TEXT,
        data_cadastro TEXT
    )
    """)

    # =====================================================
    # AUDITORIA (CORRIGIDO)
    # =====================================================
    conn.execute("""
    CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acao TEXT,
        data TEXT
    )
    """)

    # =====================================================
    # SEED COMARCAS
    # =====================================================
    comarcas = [
        "Recife", "Olinda", "Paulista", "Jaboatão dos Guararapes",
        "Abreu e Lima", "Igarassu", "Camaragibe", "Moreno",
        "Ipojuca", "São Lourenço da Mata", "Itamaracá",
        "Araçoiaba", "Itapissuma"
    ]

    for c in comarcas:
        try:
            conn.execute("INSERT INTO comarcas (nome) VALUES (?)", (c,))
        except:
            pass

    # =====================================================
    # TIPOS
    # =====================================================
    tipos = [
        "Extraordinária",
        "Ordinária",
        "Especial Urbana",
        "Especial Rural",
        "Familiar",
        "Coletiva",
        "Indígena"
    ]

    for t in tipos:
        try:
            conn.execute("INSERT INTO tipos_usucapiao (nome) VALUES (?)", (t,))
        except:
            pass

    # =====================================================
    # STATUS
    # =====================================================
    status_lista = [
        "Em tramitação",
        "Julgado",
        "Arquivado",
        "Suspenso"
    ]

    for s in status_lista:
        try:
            conn.execute("INSERT INTO status_processo (nome) VALUES (?)", (s,))
        except:
            pass

    # =====================================================
    # ADMIN PADRÃO
    # =====================================================
    admin_email = "admin@tjpe.jus.br"

    admin = conn.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        (admin_email,)
    ).fetchone()

    if not admin:
        conn.execute("""
        INSERT INTO usuarios (nome, email, senha, perfil)
        VALUES (?, ?, ?, ?)
        """, (
            "Administrador",
            admin_email,
            hash_senha("Admin123"),
            "Administrador"
        ))

    conn.commit()
    conn.close()


# =========================================================
# EXECUÇÃO
# =========================================================
if __name__ == "__main__":
    init_db()
    print("Banco criado com sucesso!")