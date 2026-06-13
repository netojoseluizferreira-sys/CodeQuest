import json
import os
from contextlib import closing
from dataclasses import dataclass

from backend.usuario import Usuario
from utils import database_config
from utils.database_connection import conectar, inicializar_banco
from utils.user_mapper import garantir_usuario, usuario_from_linha


def migrar_usuario_json_legado():
    """Migra o usuario salvo no JSON legado para SQLite quando existir.

    Recebe:
        Nenhum parametro.

    Retorna:
        Usuario migrado ou None quando nao houver arquivo legado.
    """
    if not os.path.exists(database_config.LEGACY_USUARIO_JSON_PATH):
        return None

    with open(database_config.LEGACY_USUARIO_JSON_PATH, "r", encoding="utf-8") as arquivo:
        usuario = Usuario.from_dict(json.load(arquivo))

    salvar_usuario(usuario)
    return usuario


@dataclass
class UsuarioCRUD:
    """Repositorio SQLite responsavel pelo CRUD de Usuario."""

    usuario_ativo_id: int = database_config.USUARIO_ATIVO_ID

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
    return database_config.USUARIO_ATIVO_ID
