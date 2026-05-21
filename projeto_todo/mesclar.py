# =========================================================
# MESCLAR DOIS BANCOS DE DADOS
# projeto_todo/database.db  +  projeto_todo - copia/database.db
# =========================================================

import sqlite3
import os

DB_PRINCIPAL = "database.db"                                
DB_COPIA     = "../../database.db"  # banco na pasta Projetos

# =========================================================
# CONEXÕES
# =========================================================

conn_principal = sqlite3.connect(DB_PRINCIPAL)
conn_principal.row_factory = sqlite3.Row

conn_copia = sqlite3.connect(DB_COPIA)
conn_copia.row_factory = sqlite3.Row

cur = conn_principal.cursor()

print("Iniciando mesclagem...\n")

# =========================================================
# USUÁRIOS
# =========================================================

usuarios = conn_copia.execute("SELECT * FROM usuarios").fetchall()
inseridos_u = 0

for u in usuarios:
    try:
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha, perfil)
            VALUES (?, ?, ?, ?)
        """, (u["nome"], u["email"], u["senha"], u["perfil"]))
        inseridos_u += 1
    except sqlite3.IntegrityError:
        pass  # email duplicado, ignora

print(f"Usuários mesclados: {inseridos_u} novos")

# =========================================================
# COMARCAS
# =========================================================

comarcas = conn_copia.execute("SELECT * FROM comarcas").fetchall()
inseridos_c = 0

for c in comarcas:
    try:
        cur.execute("INSERT INTO comarcas (nome) VALUES (?)", (c["nome"],))
        inseridos_c += 1
    except sqlite3.IntegrityError:
        pass

print(f"Comarcas mescladas: {inseridos_c} novas")

# =========================================================
# TIPOS USUCAPIÃO
# =========================================================

tipos = conn_copia.execute("SELECT * FROM tipos_usucapiao").fetchall()
inseridos_t = 0

for t in tipos:
    try:
        cur.execute("INSERT INTO tipos_usucapiao (nome) VALUES (?)", (t["nome"],))
        inseridos_t += 1
    except sqlite3.IntegrityError:
        pass

print(f"Tipos mesclados: {inseridos_t} novos")

# =========================================================
# STATUS
# =========================================================

status_lista = conn_copia.execute("SELECT * FROM status_processo").fetchall()
inseridos_s = 0

for s in status_lista:
    try:
        cur.execute("INSERT INTO status_processo (nome) VALUES (?)", (s["nome"],))
        inseridos_s += 1
    except sqlite3.IntegrityError:
        pass

print(f"Status mesclados: {inseridos_s} novos")

# =========================================================
# PROCESSOS
# =========================================================

processos = conn_copia.execute("SELECT * FROM processos").fetchall()
inseridos_p = 0

for p in processos:
    try:
        cur.execute("""
            INSERT INTO processos (
                numero, autor, reu, comarca, status,
                tipo_usucapiao, observacoes, data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["numero"], p["autor"], p["reu"], p["comarca"],
            p["status"], p["tipo_usucapiao"], p["observacoes"], p["data_cadastro"]
        ))
        inseridos_p += 1
    except sqlite3.IntegrityError:
        pass  # número duplicado, ignora

print(f"Processos mesclados: {inseridos_p} novos")

# =========================================================
# AUDITORIA
# =========================================================

logs = conn_copia.execute("SELECT * FROM auditoria").fetchall()
inseridos_a = 0

for l in logs:
    try:
        cur.execute("""
            INSERT INTO auditoria (usuario, acao, detalhes, data_hora)
            VALUES (?, ?, ?, ?)
        """, (
            l["usuario"] if "usuario" in l.keys() else "Sistema",
            l["acao"],
            l["detalhes"] if "detalhes" in l.keys() else "",
            l["data_hora"] if "data_hora" in l.keys() else l["data"] if "data" in l.keys() else ""
        ))
        inseridos_a += 1
    except Exception:
        pass

print(f"Logs de auditoria mesclados: {inseridos_a} novos")

# =========================================================
# RELATÓRIOS
# =========================================================

try:
    relatorios = conn_copia.execute("SELECT * FROM relatorios").fetchall()
    inseridos_r = 0

    for r in relatorios:
        # Busca o usuario_id equivalente no banco principal pelo email
        usuario_copia = conn_copia.execute(
            "SELECT * FROM usuarios WHERE id = ?", (r["usuario_id"],)
        ).fetchone()

        if usuario_copia:
            usuario_principal = conn_principal.execute(
                "SELECT id FROM usuarios WHERE email = ?", (usuario_copia["email"],)
            ).fetchone()
            novo_usuario_id = usuario_principal["id"] if usuario_principal else 1
        else:
            novo_usuario_id = 1

        cur.execute("""
            INSERT INTO relatorios (
                usuario_id, nome, descricao, status, comarca,
                tipo_usucapiao, data_criacao, data_atualizacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            novo_usuario_id,
            r["nome"], r["descricao"], r["status"],
            r["comarca"], r["tipo_usucapiao"],
            r["data_criacao"], r["data_atualizacao"]
        ))
        inseridos_r += 1

    print(f"Relatórios mesclados: {inseridos_r} novos")

except Exception as e:
    print(f"Relatórios: {e}")

# =========================================================
# FINALIZAR
# =========================================================

conn_principal.commit()
conn_principal.close()
conn_copia.close()

print("\nMesclagem concluída com sucesso!")
print(f"Banco principal atualizado: {os.path.abspath(DB_PRINCIPAL)}")