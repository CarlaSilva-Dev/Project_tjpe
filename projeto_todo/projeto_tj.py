# =========================================================
# PROJETO TJPE - SISTEMA DE USUCAPIÃO
# projeto_tj.py
# =========================================================

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file
)

import sqlite3
import hashlib
import re
import io
import os

from functools import wraps
from datetime import datetime
from dotenv import load_dotenv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# =========================================================
# CARREGAMENTO DE VARIÁVEIS DE AMBIENTE
# =========================================================

load_dotenv()

# =========================================================
# APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "tjpe_secret_key_2026_dev")

DATABASE = os.getenv("DATABASE_PATH", "database.db")

# =========================================================
# CONEXÃO
# =========================================================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# HASH SENHA
# =========================================================

def hash_senha(senha):

    return hashlib.sha256(
        senha.encode()
    ).hexdigest()


# =========================================================
# EMAIL
# =========================================================

def email_valido(email):

    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return re.match(regex, email)


# =========================================================
# SENHA
# =========================================================

def senha_valida(senha):

    if len(senha) < 8:
        return False

    tem_numero = any(c.isdigit() for c in senha)

    tem_letra = any(c.isalpha() for c in senha)

    return tem_numero and tem_letra


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(f):

    @wraps(f)

    def decorated_function(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Faça login primeiro.",
                "warning"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# CONTROLE DE PERMISSÕES
# =========================================================

def require_permission(perfis_permitidos):

    def decorator(f):

        @wraps(f)

        def decorated_function(*args, **kwargs):

            if "perfil" not in session or session["perfil"] not in perfis_permitidos:

                flash(
                    "Acesso negado. Permissão insuficiente.",
                    "danger"
                )

                return redirect(url_for("dashboard"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# =========================================================
# LOG AUDITORIA
# =========================================================

def registrar_log(acao):

    conn = get_db_connection()

    usuario = session.get("usuario_nome", "Sistema")
    detalhes = None
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # tenta inserir em campos novos (usuario, detalhes, data_hora)
    try:
        conn.execute(
            """
            INSERT INTO auditoria (
                usuario,
                acao,
                detalhes,
                data_hora
            )
            VALUES (?, ?, ?, ?)
            """,
            (usuario, acao, detalhes, data_hora)
        )

    except Exception:
        # esquema antigo: apenas acao e data
        conn.execute(
            """
            INSERT INTO auditoria (
                acao,
                data
            )
            VALUES (?, ?)
            """,
            (acao, data_hora)
        )

    conn.commit()

    conn.close()


# =========================================================
# INIT DB
# =========================================================

def init_db():

    conn = get_db_connection()

    # =========================
    # USUÁRIOS
    # =========================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        perfil TEXT NOT NULL
    )
    """)

    # =========================
    # COMARCAS
    # =========================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS comarcas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # =========================
    # TIPOS USUCAPIÃO
    # =========================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS tipos_usucapiao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # =========================
    # STATUS
    # =========================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS status_processo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    """)

    # =========================
    # PROCESSOS
    # =========================

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

    # =========================
    # AUDITORIA
    # =========================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        acao TEXT,
        detalhes TEXT,
        data_hora TEXT
    )
    """)

    # =========================
    # RELATÓRIOS SALVOS
    # =========================

    conn.execute("""
    CREATE TABLE IF NOT EXISTS relatorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nome TEXT NOT NULL,
        descricao TEXT,
        status TEXT,
        comarca TEXT,
        tipo_usucapiao TEXT,
        data_criacao TEXT,
        data_atualizacao TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    # compatibilidade: se existir tabela antiga com coluna 'data' ou sem colunas novas,
    # tenta adicionar colunas que possam faltar
    try:
        conn.execute("ALTER TABLE auditoria ADD COLUMN usuario TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE auditoria ADD COLUMN detalhes TEXT")
    except:
        pass

    try:
        conn.execute("ALTER TABLE auditoria ADD COLUMN data_hora TEXT")
    except:
        pass

    # =====================================================
    # SEED COMARCAS
    # =====================================================

    comarcas = [
        "Recife",
        "Olinda",
        "Paulista",
        "Jaboatão dos Guararapes",
        "Abreu e Lima",
        "Igarassu",
        "Camaragibe",
        "Moreno",
        "Ipojuca",
        "São Lourenço da Mata",
        "Ilha de Itamaracá",
        "Araçoiaba",
        "Itapissuma"
    ]

    for comarca in comarcas:

        try:

            conn.execute(
                """
                INSERT INTO comarcas (nome)
                VALUES (?)
                """,
                (comarca,)
            )

        except:
            pass

    # =====================================================
    # SEED TIPOS
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

    for tipo in tipos:

        try:

            conn.execute(
                """
                INSERT INTO tipos_usucapiao (nome)
                VALUES (?)
                """,
                (tipo,)
            )

        except:
            pass

    # =====================================================
    # SEED STATUS
    # =====================================================

    status_lista = [
        "Em tramitação",
        "Julgado",
        "Arquivado",
        "Suspenso"
    ]

    for status in status_lista:

        try:

            conn.execute(
                """
                INSERT INTO status_processo (nome)
                VALUES (?)
                """,
                (status,)
            )

        except:
            pass

    # =====================================================
    # ADMIN PADRÃO
    # =====================================================

    admin_email = "admin@tjpe.jus.br"

    admin = conn.execute(
        """
        SELECT *
        FROM usuarios
        WHERE email = ?
        """,
        (admin_email,)
    ).fetchone()

    if not admin:

        conn.execute(
            """
            INSERT INTO usuarios (
                nome,
                email,
                senha,
                perfil
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "Administrador",
                admin_email,
                hash_senha("Admin123"),
                "Administrador"
            )
        )

    conn.commit()

    conn.close()


# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET", "POST"])

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        email = request.form["email"]

        senha = request.form["senha"]

        if not email_valido(email):

            flash(
                "Email inválido!",
                "danger"
            )

            return redirect(
                url_for("login")
            )

        senha_hash = hash_senha(senha)

        conn = get_db_connection()

        usuario = conn.execute(
            """
            SELECT *
            FROM usuarios
            WHERE email = ?
            AND senha = ?
            """,
            (
                email,
                senha_hash
            )
        ).fetchone()

        conn.close()

        if usuario:

            session["usuario_id"] = usuario["id"]

            session["usuario_nome"] = usuario["nome"]

            session["perfil"] = usuario["perfil"]

            registrar_log(
                f"Login realizado: {usuario['nome']}"
            )

            flash(
                "Login realizado com sucesso!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        else:

            flash(
                "Email ou senha incorretos!",
                "danger"
            )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")

@login_required

def logout():

    registrar_log(
        f"Logout usuário {session['usuario_nome']}"
    )

    session.clear()

    flash(
        "Logout realizado.",
        "info"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")

@login_required

def dashboard():

    conn = get_db_connection()

    total = conn.execute(
        "SELECT COUNT(*) total FROM processos"
    ).fetchone()["total"]

    julgados = conn.execute(
        """
        SELECT COUNT(*) total
        FROM processos
        WHERE status='Julgado'
        """
    ).fetchone()["total"]

    andamento = conn.execute(
        """
        SELECT COUNT(*) total
        FROM processos
        WHERE status='Em tramitação'
        """
    ).fetchone()["total"]

    arquivados = conn.execute(
        """
        SELECT COUNT(*) total
        FROM processos
        WHERE status='Arquivado'
        """
    ).fetchone()["total"]

    processos = conn.execute(
        """
        SELECT *
        FROM processos
        ORDER BY id DESC
        """
    ).fetchall()

    grafico = conn.execute(
        """
        SELECT comarca,
        COUNT(*) total
        FROM processos
        GROUP BY comarca
        """
    ).fetchall()

    conn.close()

    labels = [g["comarca"] for g in grafico]

    valores = [g["total"] for g in grafico]

    return render_template(
        "dashboard.html",
        total=total,
        julgados=julgados,
        andamento=andamento,
        arquivados=arquivados,
        processos=processos,
        labels=labels,
        valores=valores
    )


# =========================================================
# PROCESSOS
# =========================================================

@app.route("/processos")

@login_required

def processos():

    filtro = request.args.get("filtro", "")

    comarca = request.args.get("comarca", "")

    status = request.args.get("status", "")

    conn = get_db_connection()

    query = """
    SELECT *
    FROM processos
    WHERE 1=1
    """

    params = []

    if filtro:

        query += """
        AND (
            numero LIKE ?
            OR autor LIKE ?
            OR reu LIKE ?
        )
        """

        params.extend([
            f"%{filtro}%",
            f"%{filtro}%",
            f"%{filtro}%"
        ])

    if comarca:

        query += " AND comarca = ? "

        params.append(comarca)

    if status:

        query += " AND status = ? "

        params.append(status)

    query += " ORDER BY id DESC "

    processos = conn.execute(
        query,
        params
    ).fetchall()

    comarcas = conn.execute(
        "SELECT * FROM comarcas"
    ).fetchall()

    status_lista = conn.execute(
        "SELECT * FROM status_processo"
    ).fetchall()

    conn.close()

    return render_template(
        "processos_lista.html",
        processos=processos,
        comarcas=comarcas,
        status_lista=status_lista
    )


# =========================================================
# NOVO PROCESSO
# =========================================================

@app.route("/processo/novo", methods=["GET", "POST"])
@login_required
def novo_processo():
    conn = get_db_connection()

    comarcas = conn.execute("SELECT * FROM comarcas").fetchall()
    tipos = conn.execute("SELECT * FROM tipos_usucapiao").fetchall()
    status_lista = conn.execute("SELECT * FROM status_processo").fetchall()

    if request.method == "POST":
        numero = request.form.get("numero", "").strip()
        autor = request.form.get("autor", "").strip()
        reu = request.form.get("reu", "").strip()
        comarca = request.form.get("comarca", "").strip()
        status = request.form.get("status", "").strip()
        tipo_usucapiao = request.form.get("tipo_usucapiao", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        # Verifica se já existe processo com mesmo número
        processo_existente = conn.execute(
            "SELECT * FROM processos WHERE numero = ?", (numero,)
        ).fetchone()

        if processo_existente:
            flash("Já existe processo com este número!", "danger")
            conn.close()
            return redirect(url_for("novo_processo"))

        conn.execute(
            """
            INSERT INTO processos (
                numero, autor, reu, comarca, status, tipo_usucapiao, observacoes, data_cadastro
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (numero, autor, reu, comarca, status, tipo_usucapiao, observacoes, datetime.now().strftime("%d/%m/%Y"))
        )
        conn.commit()
        conn.close()

        registrar_log(f"Novo processo criado: {numero}")
        flash("Processo cadastrado!", "success")
        return redirect(url_for("processos"))

    conn.close()
    return render_template(
        "processo_form.html",
        comarcas=comarcas,
        tipos=tipos,
        status_lista=status_lista
    )



# =========================================================
# DETALHE PROCESSO
# =========================================================

@app.route("/processo/<int:id>")

@login_required

def detalhe_processo(id):

    conn = get_db_connection()

    processo = conn.execute(
        """
        SELECT *
        FROM processos
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "processo_detalhe.html",
        processo=processo
    )


# =========================================================
# EDITAR PROCESSO
# =========================================================

@app.route("/processo/editar/<int:id>", methods=["GET", "POST"])
@login_required
@require_permission(["Administrador"])
def editar_processo(id):
    conn = get_db_connection()

    processo = conn.execute("SELECT * FROM processos WHERE id = ?", (id,)).fetchone()
    if not processo:
        flash("Processo não encontrado.", "danger")
        conn.close()
        return redirect(url_for("processos"))

    comarcas = conn.execute("SELECT * FROM comarcas").fetchall()
    tipos = conn.execute("SELECT * FROM tipos_usucapiao").fetchall()
    status_lista = conn.execute("SELECT * FROM status_processo").fetchall()

    if request.method == "POST":
        numero = request.form.get("numero", "").strip()
        autor = request.form.get("autor", "").strip()
        reu = request.form.get("reu", "").strip()
        comarca = request.form.get("comarca", "").strip()
        status = request.form.get("status", "").strip()
        tipo_usucapiao = request.form.get("tipo_usucapiao", "").strip()
        observacoes = request.form.get("observacoes", "").strip()

        resultado = conn.execute(
            """
            UPDATE processos
            SET numero=?, autor=?, reu=?, comarca=?, status=?, tipo_usucapiao=?, observacoes=?
            WHERE id=?
            """,
            (numero, autor, reu, comarca, status, tipo_usucapiao, observacoes, id)
        ).rowcount

        conn.commit()
        conn.close()

        if resultado == 0:
            flash("Nenhum dado foi alterado.", "warning")
        else:
            registrar_log(f"Processo editado ID {id}")
            flash("Processo atualizado!", "success")

        return redirect(url_for("processos"))

    conn.close()
    return render_template(
        "processo_form.html",
        processo=processo,
        comarcas=comarcas,
        tipos=tipos,
        status_lista=status_lista
    )


# =========================================================
# EXCLUIR PROCESSO
# =========================================================

@app.route("/processo/excluir/<int:id>")

@login_required
@require_permission(["Administrador"])

def excluir_processo(id):

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM processos
        WHERE id = ?
        """,
        (id,)
    )

    conn.commit()

    conn.close()

    registrar_log(
        f"Processo excluído ID {id}"
    )

    flash(
        "Processo excluído!",
        "success"
    )

    return redirect(
        url_for("processos")
    )


# =========================================================
# PDF INDIVIDUAL
# =========================================================

@app.route("/processo/pdf/<int:id>")

@login_required

def gerar_pdf(id):

    conn = get_db_connection()

    processo = conn.execute(
        """
        SELECT *
        FROM processos
        WHERE id = ?
        """,
        (id,)
    ).fetchone()

    conn.close()

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    pdf.setFont("Helvetica-Bold", 16)

    pdf.drawString(
        180,
        800,
        "RELATÓRIO PROCESSUAL"
    )

    pdf.setFont("Helvetica", 12)

    y = 760

    campos = [
        ("Número", processo["numero"]),
        ("Autor", processo["autor"]),
        ("Réu", processo["reu"]),
        ("Comarca", processo["comarca"]),
        ("Status", processo["status"]),
        ("Tipo", processo["tipo_usucapiao"]),
        ("Data", processo["data_cadastro"]),
        ("Observações", processo["observacoes"])
    ]

    for campo, valor in campos:

        pdf.drawString(
            80,
            y,
            f"{campo}: {valor}"
        )

        y -= 30

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="processo.pdf",
        mimetype="application/pdf"
    )


# =========================================================
# RELATÓRIO GERAL PDF
# =========================================================

@app.route("/relatorio/pdf")

@login_required

def relatorio_pdf():

    conn = get_db_connection()

    processos = conn.execute(
        """
        SELECT *
        FROM processos
        ORDER BY comarca
        """
    ).fetchall()

    conn.close()

    buffer = io.BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    pdf.setFont("Helvetica-Bold", 16)

    pdf.drawString(
        180,
        800,
        "RELATÓRIO GERAL"
    )

    y = 760

    pdf.setFont("Helvetica", 10)

    for processo in processos:

        linha = (
            f"{processo['numero']} | "
            f"{processo['autor']} | "
            f"{processo['comarca']} | "
            f"{processo['status']}"
        )

        pdf.drawString(
            40,
            y,
            linha
        )

        y -= 20

        if y < 40:

            pdf.showPage()

            y = 800

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="relatorio_geral.pdf",
        mimetype="application/pdf"
    )


# =========================================================
# USUÁRIOS
# =========================================================
@app.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
@login_required
@require_permission(["Administrador"])
def editar_usuario(id):

    conn = get_db_connection()

    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        conn.execute("""
            UPDATE usuarios
            SET nome = ?,
                email = ?,
                perfil = ?
            WHERE id = ?
        """, (
            request.form["nome"],
            request.form["email"],
            request.form["perfil"],
            id
        ))

        conn.commit()
        conn.close()

        flash("Usuário atualizado!", "success")
        return redirect(url_for("usuarios"))

    conn.close()

    return render_template(
        "usuario_form.html",
        usuario=usuario
    )
@app.route("/usuarios")

@login_required
@require_permission(["Administrador"])

def usuarios():

    conn = get_db_connection()

    usuarios = conn.execute(
        "SELECT * FROM usuarios"
    ).fetchall()

    conn.close()

    return render_template(
        "usuarios_lista.html",
        usuarios=usuarios
    )
@app.route("/usuario/excluir/<int:id>")
@login_required
@require_permission(["Administrador"])
def excluir_usuario(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM usuarios WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    registrar_log(f"Usuário excluído ID {id}")

    flash("Usuário excluído com sucesso!", "success")

    return redirect(url_for("usuarios"))

# =========================================================
# NOVO USUÁRIO
# =========================================================

@app.route(
    "/usuario/novo",
    methods=["GET", "POST"]
)

@login_required
@require_permission(["Administrador"])

def novo_usuario():

    if request.method == "POST":

        nome = request.form["nome"]

        email = request.form["email"]

        senha = request.form["senha"]

        perfil = request.form["perfil"]

        if not email_valido(email):

            flash(
                "Email inválido!",
                "danger"
            )

            return redirect(
                url_for("novo_usuario")
            )

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO usuarios (
                nome,
                email,
                senha,
                perfil
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                nome,
                email,
                hash_senha(senha),
                perfil
            )
        )

        conn.commit()

        conn.close()

        registrar_log(
            f"Usuário criado: {nome}"
        )

        flash(
            "Usuário cadastrado!",
            "success"
        )

        return redirect(
            url_for("usuarios")
        )

    return render_template(
        "usuario_form.html"
    )


# =========================================================
# AUDITORIA
# =========================================================

@app.route("/auditoria")

@login_required

def auditoria():

    conn = get_db_connection()

    logs = conn.execute(
        """
        SELECT *
        FROM auditoria
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    # normaliza campos para compatibilidade com esquema antigo
    logs_norm = []

    for l in logs:

        d = dict(l)

        usuario = d.get("usuario") or d.get("user") or "Sistema"

        acao = d.get("acao") or d.get("acao")

        detalhes = d.get("detalhes") or d.get("detalhe") or ""

        data_hora = d.get("data_hora") or d.get("data") or ""

        logs_norm.append({
            "id": d.get("id"),
            "usuario": usuario,
            "acao": acao,
            "detalhes": detalhes,
            "data_hora": data_hora
        })

    return render_template(
        "auditoria.html",
        logs=logs_norm
    )


@app.route("/auditoria/novo", methods=["GET", "POST"])
@login_required
def novo_auditoria():

    if request.method == "POST":

        usuario = request.form.get("usuario") or session.get("usuario_nome", "Sistema")

        acao = request.form.get("acao", "")

        detalhes = request.form.get("detalhes", "")

        data_hora = request.form.get("data_hora") or datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO auditoria (usuario, acao, detalhes, data_hora) VALUES (?, ?, ?, ?)",
            (usuario, acao, detalhes, data_hora)
        )

        conn.commit()

        conn.close()

        flash("Entrada de auditoria criada.", "success")

        return redirect(url_for("auditoria"))

    return render_template("auditoria_form.html")


@app.route("/auditoria/editar/<int:id>", methods=["GET", "POST"])
@login_required
@require_permission(["Administrador"])
def editar_auditoria(id):

    conn = get_db_connection()

    log = conn.execute("SELECT * FROM auditoria WHERE id = ?", (id,)).fetchone()

    if not log:

        conn.close()

        flash("Registro não encontrado.", "danger")

        return redirect(url_for("auditoria"))

    if request.method == "POST":

        usuario = request.form.get("usuario") or session.get("usuario_nome", "Sistema")

        acao = request.form.get("acao", "")

        detalhes = request.form.get("detalhes", "")

        data_hora = request.form.get("data_hora") or datetime.now().strftime("%d/%m/%Y %H:%M")

        conn.execute(
            "UPDATE auditoria SET usuario=?, acao=?, detalhes=?, data_hora=? WHERE id=?",
            (usuario, acao, detalhes, data_hora, id)
        )

        conn.commit()

        conn.close()

        registrar_log(f"Registro de auditoria editado ID {id}")

        flash("Registro atualizado.", "success")

        return redirect(url_for("auditoria"))

    # GET
    d = dict(log)

    log_norm = {
        "id": d.get("id"),
        "usuario": d.get("usuario") or "",
        "acao": d.get("acao") or "",
        "detalhes": d.get("detalhes") or "",
        "data_hora": d.get("data_hora") or d.get("data") or ""
    }

    conn.close()

    return render_template("auditoria_form.html", log=log_norm)


@app.route("/auditoria/excluir/<int:id>")
@login_required
@require_permission(["Administrador"])
def excluir_auditoria(id):

    conn = get_db_connection()

    conn.execute("DELETE FROM auditoria WHERE id = ?", (id,))

    conn.commit()

    conn.close()

    registrar_log(f"Registro de auditoria excluído ID {id}")

    flash("Registro excluído.", "success")

    return redirect(url_for("auditoria"))
@app.route("/relatorios")
@login_required
def relatorios():
    conn = get_db_connection()

    # ==============================
    # LISTA DE RELATÓRIOS SALVOS
    # ==============================
    usuario_id = session["usuario_id"]
    perfil = session["perfil"]

    # Admin vê todos, outros veem só os deles
    if perfil == "Administrador":
        relatorios_list = conn.execute(
            "SELECT r.*, u.nome as usuario_nome FROM relatorios r JOIN usuarios u ON r.usuario_id = u.id ORDER BY r.data_atualizacao DESC"
        ).fetchall()
    else:
        relatorios_list = conn.execute(
            "SELECT r.*, u.nome as usuario_nome FROM relatorios r JOIN usuarios u ON r.usuario_id = u.id WHERE r.usuario_id = ? ORDER BY r.data_atualizacao DESC",
            (usuario_id,)
        ).fetchall()

    conn.close()

    return render_template(
        "relatorios_lista.html",
        relatorios=relatorios_list
    )


@app.route("/relatorio/novo", methods=["GET", "POST"])
@login_required
def novo_relatorio():
    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        status = request.form.get("status", "").strip()
        comarca = request.form.get("comarca", "").strip()
        tipo_usucapiao = request.form.get("tipo_usucapiao", "").strip()

        if not nome:
            flash("Nome do relatório é obrigatório.", "danger")
            return redirect(url_for("novo_relatorio"))

        conn = get_db_connection()

        conn.execute(
            """INSERT INTO relatorios (usuario_id, nome, descricao, status, comarca, tipo_usucapiao, data_criacao, data_atualizacao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session["usuario_id"],
                nome,
                descricao,
                status,
                comarca,
                tipo_usucapiao,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                datetime.now().strftime("%d/%m/%Y %H:%M")
            )
        )

        conn.commit()
        conn.close()

        registrar_log(f"Relatório criado: {nome}")
        flash("Relatório salvo com sucesso!", "success")
        return redirect(url_for("relatorios"))

    conn = get_db_connection()
    comarcas = conn.execute("SELECT * FROM comarcas").fetchall()
    tipos = conn.execute("SELECT * FROM tipos_usucapiao").fetchall()
    status_lista = conn.execute("SELECT * FROM status_processo").fetchall()
    conn.close()

    return render_template(
        "relatorio_form.html",
        comarcas=comarcas,
        tipos=tipos,
        status_lista=status_lista
    )


@app.route("/relatorio/editar/<int:id>", methods=["GET", "POST"])
@login_required
@require_permission(["Administrador"])
def editar_relatorio(id):
    conn = get_db_connection()

    relatorio = conn.execute("SELECT * FROM relatorios WHERE id = ?", (id,)).fetchone()

    if not relatorio:
        conn.close()
        flash("Relatório não encontrado.", "danger")
        return redirect(url_for("relatorios"))

    # Verifica permissão: admin pode editar qualquer um, outros só o deles
    if session["perfil"] != "Administrador" and relatorio["usuario_id"] != session["usuario_id"]:
        conn.close()
        flash("Acesso negado.", "danger")
        return redirect(url_for("relatorios"))

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        status = request.form.get("status", "").strip()
        comarca = request.form.get("comarca", "").strip()
        tipo_usucapiao = request.form.get("tipo_usucapiao", "").strip()

        conn.execute(
            """UPDATE relatorios SET nome=?, descricao=?, status=?, comarca=?, tipo_usucapiao=?, data_atualizacao=?
               WHERE id=?""",
            (nome, descricao, status, comarca, tipo_usucapiao, datetime.now().strftime("%d/%m/%Y %H:%M"), id)
        )

        conn.commit()
        conn.close()

        registrar_log(f"Relatório editado ID {id}: {nome}")
        flash("Relatório atualizado!", "success")
        return redirect(url_for("relatorios"))

    comarcas = conn.execute("SELECT * FROM comarcas").fetchall()
    tipos = conn.execute("SELECT * FROM tipos_usucapiao").fetchall()
    status_lista = conn.execute("SELECT * FROM status_processo").fetchall()
    conn.close()

    return render_template(
        "relatorio_form.html",
        relatorio=dict(relatorio),
        comarcas=comarcas,
        tipos=tipos,
        status_lista=status_lista
    )


@app.route("/relatorio/excluir/<int:id>")
@login_required
@require_permission(["Administrador"])
def excluir_relatorio(id):
    conn = get_db_connection()

    relatorio = conn.execute("SELECT * FROM relatorios WHERE id = ?", (id,)).fetchone()

    if not relatorio:
        conn.close()
        flash("Relatório não encontrado.", "danger")
        return redirect(url_for("relatorios"))

    # Verifica permissão
    if session["perfil"] != "Administrador" and relatorio["usuario_id"] != session["usuario_id"]:
        conn.close()
        flash("Acesso negado.", "danger")
        return redirect(url_for("relatorios"))

    conn.execute("DELETE FROM relatorios WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    registrar_log(f"Relatório excluído ID {id}")
    flash("Relatório excluído com sucesso.", "success")
    return redirect(url_for("relatorios"))


@app.route("/relatorio/visualizar/<int:id>")
@login_required
def visualizar_relatorio(id):
    conn = get_db_connection()

    relatorio = conn.execute(
        "SELECT r.*, u.nome as usuario_nome FROM relatorios r JOIN usuarios u ON r.usuario_id = u.id WHERE r.id = ?", 
        (id,)
    ).fetchone()

    if not relatorio:
        conn.close()
        flash("Relatório não encontrado.", "danger")
        return redirect(url_for("relatorios"))

    # Verifica permissão: admin vê todos, outros só os seus
    if session["perfil"] != "Administrador" and relatorio["usuario_id"] != session["usuario_id"]:
        conn.close()
        flash("Acesso negado.", "danger")
        return redirect(url_for("relatorios"))

    # ==============================
    # APLICA FILTROS DO RELATÓRIO
    # ==============================
    query = "SELECT * FROM processos WHERE 1=1"
    params = []

    if relatorio["status"]:
        query += " AND status LIKE ?"
        params.append(f"%{relatorio['status']}%")
    if relatorio["comarca"]:
        query += " AND comarca LIKE ?"
        params.append(f"%{relatorio['comarca']}%")
    if relatorio["tipo_usucapiao"]:
        query += " AND tipo_usucapiao LIKE ?"
        params.append(f"%{relatorio['tipo_usucapiao']}%")

    query += " ORDER BY id DESC"

    processos = conn.execute(query, params).fetchall()
    processos = [dict(p) for p in processos]

    # ==============================
    # KPIs
    # ==============================
    total_processos = len(processos)
    total_andamento = sum(1 for p in processos if p["status"] == "Em tramitação")
    total_julgados = sum(1 for p in processos if p["status"] == "Julgado")
    total_arquivados = sum(1 for p in processos if p["status"] == "Arquivado")

    conn.close()

    return render_template(
        "relatorio_visualizar.html",
        relatorio=dict(relatorio),
        processos=processos,
        total_processos=total_processos,
        total_andamento=total_andamento,
        total_julgados=total_julgados,
        total_arquivados=total_arquivados
    )


@app.route('/processo/modal/<int:id>')
@login_required
def processo_modal(id):
    conn = get_db_connection()

    processo = conn.execute("SELECT * FROM processos WHERE id = ?", (id,)).fetchone()

    conn.close()

    if not processo:
        return "<div class='p-3'>Processo não encontrado.</div>", 404

    return render_template('processo_modal.html', processo=processo)
# =========================================================
# EXECUÇÃO
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True
    )