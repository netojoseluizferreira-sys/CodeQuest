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
    """Abre uma conexao com o banco SQLite local.

    Recebe:
        Nenhum parametro.

    Retorna:
        Conexao SQLite configurada para acessar colunas pelo nome.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """Garante que as tabelas usadas pela persistencia existam.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
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
    """Migra o usuario salvo no JSON legado para SQLite quando existir.

    Recebe:
        Nenhum parametro.

    Retorna:
        Usuario migrado ou None quando nao houver arquivo legado.
    """
    if not os.path.exists(LEGACY_USUARIO_JSON_PATH):
        return None

    with open(LEGACY_USUARIO_JSON_PATH, "r", encoding="utf-8") as arquivo:
        usuario = Usuario.from_dict(json.load(arquivo))

    salvar_usuario(usuario)
    return usuario


def garantir_usuario(usuario):
    """Normaliza entradas de usuario para a dataclass Usuario.

    Recebe:
        usuario: Instancia de Usuario, dicionario legado ou None.

    Retorna:
        Instancia de Usuario equivalente ou None quando a entrada for None.
    """
    if usuario is None:
        return None
    if isinstance(usuario, Usuario):
        return usuario
    return Usuario.from_dict(usuario)


def usuario_from_linha(linha):
    """Converte uma linha da tabela usuarios em objeto de dominio.

    Recebe:
        linha: sqlite3.Row com colunas de usuario.

    Retorna:
        Instancia de Usuario preenchida com os dados da linha.
    """
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
    """Repositorio SQLite responsavel pelo CRUD de Usuario."""

    usuario_ativo_id: int = USUARIO_ATIVO_ID

    def criar(self, nome, idade):
        """Cria e persiste o usuario ativo.

        Recebe:
            nome: Nome informado pelo jogador.
            idade: Idade informada pelo jogador.

        Retorna:
            Usuario criado e salvo no banco.
        """
        usuario = Usuario.criar(nome, idade)
        usuario.id = self.usuario_ativo_id
        self.salvar(usuario)
        return usuario

    def salvar(self, usuario):
        """Cria ou atualiza um usuario no banco.

        Recebe:
            usuario: Instancia de Usuario ou dicionario legado com dados do usuario.

        Retorna:
            Usuario normalizado que foi persistido.
        """
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
        """Busca um usuario pelo ID informado.

        Recebe:
            usuario_id: ID do usuario desejado; quando omitido, usa o usuario ativo.

        Retorna:
            Usuario encontrado, usuario migrado do JSON legado ou None.
        """
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
        """Lista todos os usuarios persistidos.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de instancias de Usuario ordenada por ID.
        """
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
        """Remove um usuario e seus dados relacionados.

        Recebe:
            usuario_id: ID do usuario removido; quando omitido, usa o usuario ativo.

        Retorna:
            None.
        """
        inicializar_banco()
        usuario_id = usuario_id or self.usuario_ativo_id

        with closing(conectar()) as conexao, conexao:
            conexao.execute("DELETE FROM exercicios_concluidos WHERE usuario_id = ?", (usuario_id,))
            conexao.execute("DELETE FROM exercicio_erros WHERE usuario_id = ?", (usuario_id,))
            conexao.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))


def usuario_crud():
    """Instancia o repositorio de usuarios.

    Recebe:
        Nenhum parametro.

    Retorna:
        Instancia de UsuarioCRUD usando a configuracao atual do banco.
    """
    return UsuarioCRUD()


def criar_usuario(nome, idade):
    """Cria e salva o usuario ativo.

    Recebe:
        nome: Nome informado pelo jogador.
        idade: Idade informada pelo jogador.

    Retorna:
        Usuario criado e persistido.
    """
    return usuario_crud().criar(nome, idade)


def salvar_usuario(usuario):
    """Persiste dados do usuario ativo no SQLite.

    Recebe:
        usuario: Instancia de Usuario ou dicionario legado com dados do usuario.

    Retorna:
        Usuario normalizado que foi salvo.
    """
    return usuario_crud().salvar(usuario)


def carregar_usuario(usuario_id=None):
    """Carrega um usuario salvo no SQLite.

    Recebe:
        usuario_id: ID do usuario desejado; quando omitido, usa o usuario ativo.

    Retorna:
        Usuario encontrado ou None.
    """
    return usuario_crud().carregar(usuario_id)


def listar_usuarios():
    """Lista os usuarios salvos no SQLite.

    Recebe:
        Nenhum parametro.

    Retorna:
        Lista de instancias de Usuario.
    """
    return usuario_crud().listar()


def deletar_usuario(usuario_id=None):
    """Remove um usuario salvo no SQLite.

    Recebe:
        usuario_id: ID do usuario removido; quando omitido, usa o usuario ativo.

    Retorna:
        None.
    """
    return usuario_crud().deletar(usuario_id)


def obter_usuario_id(usuario=None):
    """Resolve o ID usado nas tabelas relacionadas ao usuario.

    Recebe:
        usuario: Usuario, dicionario legado ou None.

    Retorna:
        ID do usuario informado ou ID padrao do usuario ativo.
    """
    usuario = garantir_usuario(usuario)
    if usuario and usuario.id:
        return usuario.id
    return USUARIO_ATIVO_ID


def exercicio_foi_concluido(mundo, exercicio_id, usuario=None):
    """Verifica se um exercicio ja foi concluido por um usuario.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        True quando o exercicio ja foi concluido; caso contrario, False.
    """
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
    """Marca um exercicio como concluido para bloquear nova recompensa.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        xp_ganho: XP recebido na primeira conclusao.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        None.
    """
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
    """Busca a quantidade de erros persistida para um exercicio.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        Quantidade de erros registrados para o exercicio.
    """
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
    """Incrementa a quantidade de erros de um exercicio.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio_id: Identificador do exercicio.
        usuario: Usuario, dicionario legado ou None para usar o usuario ativo.

    Retorna:
        Nova quantidade total de erros do exercicio.
    """
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
    """Remove todos os dados locais salvos para testes.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        conexao.execute("DELETE FROM exercicios_concluidos")
        conexao.execute("DELETE FROM exercicio_erros")
        conexao.execute("DELETE FROM usuarios")

    for caminho_legado in (LEGACY_USUARIO_JSON_PATH, LEGACY_PROGRESSO_JSON_PATH):
        if os.path.exists(caminho_legado):
            os.remove(caminho_legado)
