import json
import os
import sqlite3
from contextlib import closing
from dataclasses import dataclass

from backend.usuario import Usuario


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


def migrar_usuario_json_legado():
    """Migra o usuario antigo salvo em JSON para SQLite, se existir."""
    if not os.path.exists(LEGACY_USUARIO_JSON_PATH):
        return None

    with open(LEGACY_USUARIO_JSON_PATH, "r", encoding="utf-8") as arquivo:
        usuario = Usuario.from_dict(json.load(arquivo))

    salvar_usuario(usuario)
    return usuario


def garantir_usuario(usuario):
    """Aceita Usuario ou dicionario legado e retorna Usuario."""
    if usuario is None:
        return None
    if isinstance(usuario, Usuario):
        return usuario
    return Usuario.from_dict(usuario)


def usuario_from_linha(linha):
    """Converte uma linha SQLite em Usuario."""
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        idade=linha["idade"],
        xp=linha["xp"],
        nivel=linha["nivel"],
        conquistas=json.loads(linha["conquistas"] or "[]"),
    )


@dataclass
class UsuarioCRUD:
    """Repositorio SQLite para operacoes de CRUD do Usuario."""

    usuario_ativo_id: int = USUARIO_ATIVO_ID

    def criar(self, nome, idade):
        """Cria e persiste um novo usuario ativo."""
        usuario = Usuario.criar(nome, idade)
        usuario.id = self.usuario_ativo_id
        self.salvar(usuario)
        return usuario

    def salvar(self, usuario):
        """Cria ou atualiza o usuario no SQLite."""
        inicializar_banco()
        usuario = garantir_usuario(usuario)

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
                    usuario.id,
                    usuario.nome,
                    usuario.idade,
                    usuario.xp,
                    usuario.nivel,
                    json.dumps(usuario.conquistas, ensure_ascii=False),
                ),
            )

        return usuario

    def carregar(self, usuario_id=None):
        """Busca um usuario por ID e migra o JSON legado quando necessario."""
        inicializar_banco()
        usuario_id = usuario_id or self.usuario_ativo_id

        with closing(conectar()) as conexao, conexao:
            linha = conexao.execute(
                """
                SELECT id, nome, idade, xp, nivel, conquistas
                FROM usuarios
                WHERE id = ?
                """,
                (usuario_id,),
            ).fetchone()

        if linha is None and usuario_id == self.usuario_ativo_id:
            return migrar_usuario_json_legado()

        return None if linha is None else usuario_from_linha(linha)

    def listar(self):
        """Lista todos os usuarios salvos."""
        inicializar_banco()

        with closing(conectar()) as conexao, conexao:
            linhas = conexao.execute(
                """
                SELECT id, nome, idade, xp, nivel, conquistas
                FROM usuarios
                ORDER BY id
                """
            ).fetchall()

        return [usuario_from_linha(linha) for linha in linhas]

    def deletar(self, usuario_id=None):
        """Remove um usuario e seus registros relacionados."""
        inicializar_banco()
        usuario_id = usuario_id or self.usuario_ativo_id

        with closing(conectar()) as conexao, conexao:
            conexao.execute("DELETE FROM exercicios_concluidos WHERE usuario_id = ?", (usuario_id,))
            conexao.execute("DELETE FROM exercicio_erros WHERE usuario_id = ?", (usuario_id,))
            conexao.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))


def usuario_crud():
    """Cria um repositorio de usuario usando a configuracao atual do banco."""
    return UsuarioCRUD()


def criar_usuario(nome, idade):
    """Cria e salva o usuario ativo."""
    return usuario_crud().criar(nome, idade)


def salvar_usuario(usuario):
    """Salva o usuario ativo no SQLite."""
    return usuario_crud().salvar(usuario)


def carregar_usuario(usuario_id=None):
    """Carrega um usuario salvo no SQLite."""
    return usuario_crud().carregar(usuario_id)


def listar_usuarios():
    """Lista usuarios salvos no SQLite."""
    return usuario_crud().listar()


def deletar_usuario(usuario_id=None):
    """Remove um usuario salvo no SQLite."""
    return usuario_crud().deletar(usuario_id)


def obter_usuario_id(usuario=None):
    """Retorna o ID usado nas tabelas relacionadas ao usuario ativo."""
    usuario = garantir_usuario(usuario)
    if usuario and usuario.id:
        return usuario.id
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
