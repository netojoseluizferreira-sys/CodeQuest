import json
import os
import sqlite3
from contextlib import closing


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "codequest.db")
LEGACY_USUARIO_JSON_PATH = os.path.join(DATA_DIR, "usuarios.json")
LEGACY_PROGRESSO_JSON_PATH = os.path.join(DATA_DIR, "progresso.json")
USUARIO_ATIVO_ID = 1


def conectar():
    """Abre uma conexao SQLite com rows acessiveis por nome."""
    os.makedirs(DATA_DIR, exist_ok=True)
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """Cria as tabelas da persistencia local, se ainda nao existirem."""
    with closing(conectar()) as conexao, conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                idade INTEGER NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                nivel INTEGER NOT NULL DEFAULT 1,
                conquistas TEXT NOT NULL DEFAULT '[]'
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS exercicios_concluidos (
                usuario_id INTEGER NOT NULL,
                mundo TEXT NOT NULL,
                exercicio_id TEXT NOT NULL,
                xp_ganho INTEGER NOT NULL DEFAULT 0,
                concluido_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (usuario_id, mundo, exercicio_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS exercicio_erros (
                usuario_id INTEGER NOT NULL,
                mundo TEXT NOT NULL,
                exercicio_id TEXT NOT NULL,
                erros INTEGER NOT NULL DEFAULT 0,
                atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (usuario_id, mundo, exercicio_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )


def salvar_usuario(usuario):
    """Salva o usuario ativo no SQLite."""
    inicializar_banco()
    conquistas = usuario.get("conquistas", [])

    with closing(conectar()) as conexao, conexao:
        conexao.execute(
            """
            INSERT INTO usuarios (id, nome, idade, xp, nivel, conquistas)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nome = excluded.nome,
                idade = excluded.idade,
                xp = excluded.xp,
                nivel = excluded.nivel,
                conquistas = excluded.conquistas
            """,
            (
                usuario.get("id", USUARIO_ATIVO_ID),
                usuario["nome"],
                usuario["idade"],
                usuario.get("xp", 0),
                usuario.get("nivel", 1),
                json.dumps(conquistas, ensure_ascii=False),
            ),
        )


def carregar_usuario():
    """Carrega o usuario ativo salvo no SQLite."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        linha = conexao.execute(
            """
            SELECT id, nome, idade, xp, nivel, conquistas
            FROM usuarios
            WHERE id = ?
            """,
            (USUARIO_ATIVO_ID,),
        ).fetchone()

    if linha is None:
        return migrar_usuario_json_legado()

    return {
        "id": linha["id"],
        "nome": linha["nome"],
        "idade": linha["idade"],
        "xp": linha["xp"],
        "nivel": linha["nivel"],
        "conquistas": json.loads(linha["conquistas"] or "[]"),
    }


def migrar_usuario_json_legado():
    """Migra o usuario antigo salvo em JSON para SQLite, se existir."""
    if not os.path.exists(LEGACY_USUARIO_JSON_PATH):
        return None

    with open(LEGACY_USUARIO_JSON_PATH, "r", encoding="utf-8") as arquivo:
        usuario = json.load(arquivo)

    usuario["id"] = usuario.get("id", USUARIO_ATIVO_ID)
    usuario["nivel"] = usuario.get("nivel", 1)
    usuario["conquistas"] = usuario.get("conquistas", [])
    salvar_usuario(usuario)
    return usuario


def obter_usuario_id(usuario=None):
    """Retorna o ID usado nas tabelas relacionadas ao usuario ativo."""
    if usuario and usuario.get("id"):
        return usuario["id"]
    return USUARIO_ATIVO_ID


def exercicio_foi_concluido(mundo, exercicio_id, usuario=None):
    """Verifica se um exercicio ja foi concluido pelo usuario."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        linha = conexao.execute(
            """
            SELECT 1
            FROM exercicios_concluidos
            WHERE usuario_id = ? AND mundo = ? AND exercicio_id = ?
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id)),
        ).fetchone()

    return linha is not None


def marcar_exercicio_concluido(mundo, exercicio_id, xp_ganho=0, usuario=None):
    """Marca um exercicio como concluido para impedir nova recompensa apos restart."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        conexao.execute(
            """
            INSERT OR IGNORE INTO exercicios_concluidos
                (usuario_id, mundo, exercicio_id, xp_ganho)
            VALUES (?, ?, ?, ?)
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id), xp_ganho),
        )


def obter_erros_exercicio(mundo, exercicio_id, usuario=None):
    """Carrega a quantidade de erros persistida para um exercicio."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        linha = conexao.execute(
            """
            SELECT erros
            FROM exercicio_erros
            WHERE usuario_id = ? AND mundo = ? AND exercicio_id = ?
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id)),
        ).fetchone()

    return 0 if linha is None else linha["erros"]


def registrar_erro_exercicio(mundo, exercicio_id, usuario=None):
    """Incrementa e persiste a quantidade de erros de um exercicio."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        conexao.execute(
            """
            INSERT INTO exercicio_erros (usuario_id, mundo, exercicio_id, erros)
            VALUES (?, ?, ?, 1)
            ON CONFLICT(usuario_id, mundo, exercicio_id) DO UPDATE SET
                erros = erros + 1,
                atualizado_em = CURRENT_TIMESTAMP
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id)),
        )
        linha = conexao.execute(
            """
            SELECT erros
            FROM exercicio_erros
            WHERE usuario_id = ? AND mundo = ? AND exercicio_id = ?
            """,
            (obter_usuario_id(usuario), mundo, str(exercicio_id)),
        ).fetchone()

    return linha["erros"]


def salvar_progresso(usuario_nome, modulo, exercicio_id):
    """Compatibilidade para chamadas antigas de progresso."""
    inicializar_banco()
    mundo = str(modulo)
    marcar_exercicio_concluido(mundo, exercicio_id)


def carregar_progresso(usuario_nome=None):
    """Carrega progresso concluido em formato simples para compatibilidade."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        linhas = conexao.execute(
            """
            SELECT mundo, exercicio_id
            FROM exercicios_concluidos
            WHERE usuario_id = ?
            ORDER BY mundo, exercicio_id
            """,
            (USUARIO_ATIVO_ID,),
        ).fetchall()

    concluidos = [linha["exercicio_id"] for linha in linhas]
    return {"modulo_atual": None, "concluidos": concluidos} if usuario_nome else {
        "usuario_ativo": {"modulo_atual": None, "concluidos": concluidos}
    }


def resetar_banco_de_dados():
    """Remove todos os dados locais salvos no SQLite."""
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        conexao.execute("DELETE FROM exercicios_concluidos")
        conexao.execute("DELETE FROM exercicio_erros")
        conexao.execute("DELETE FROM usuarios")

    for caminho_legado in (LEGACY_USUARIO_JSON_PATH, LEGACY_PROGRESSO_JSON_PATH):
        if os.path.exists(caminho_legado):
            os.remove(caminho_legado)
