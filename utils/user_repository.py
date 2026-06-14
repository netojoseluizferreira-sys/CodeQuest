"""Repositorio de usuarios e funcoes de conveniencia para o save ativo."""

import json
import os
from contextlib import closing
from dataclasses import dataclass

from backend.usuario import Usuario
from utils import database_config
from utils.database_connection import conectar, inicializar_banco
from utils.user_mapper import garantir_usuario, usuario_from_linha


def migrar_usuario_json_legado():
    """Lê o save legado em JSON e o persiste no SQLite, descartando o arquivo original.

    Só executa quando o arquivo definido em database_config.LEGACY_USUARIO_JSON_PATH
    existir. Após a migração o JSON não é removido; a lógica de remoção fica a
    cargo de resetar_banco_de_dados.

    Retorna:
        Usuario | None: Instância migrada e salva, ou None quando o arquivo
        legado não existir.
    """
    if not os.path.exists(database_config.LEGACY_USUARIO_JSON_PATH):
        return None

    with open(database_config.LEGACY_USUARIO_JSON_PATH, "r", encoding="utf-8") as arquivo:
        usuario = Usuario.from_dict(json.load(arquivo))

    salvar_usuario(usuario)
    return usuario


@dataclass
class UsuarioCRUD:
    """Repositório SQLite para operações de leitura e escrita do usuário ativo."""

    usuario_ativo_id: int = database_config.USUARIO_ATIVO_ID

    def criar(self, nome, idade):
        """Instancia um Usuario novo, atribui o ID ativo e persiste no banco.

        Recebe:
            nome (str): Nome informado pelo jogador.
            idade (int | str): Idade informada; convertida para int por Usuario.criar.

        Retorna:
            Usuario: Instância criada e já salva no SQLite.
        """
        usuario = Usuario.criar(nome, idade)
        usuario.id = self.usuario_ativo_id
        self.salvar(usuario)
        return usuario

    def salvar(self, usuario):
        """Persiste um Usuario no banco usando upsert (INSERT … ON CONFLICT DO UPDATE).

        Recebe:
            usuario (Usuario | dict): Instância de Usuario ou dicionário legado;
            normalizado por garantir_usuario antes da escrita.

        Retorna:
            Usuario: Instância normalizada que foi persistida.
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
        """Busca um usuário pelo ID; tenta migração do JSON legado quando não encontrar.

        Recebe:
            usuario_id (int | None): ID a buscar; None usa usuario_ativo_id.

        Retorna:
            Usuario | None: Instância encontrada no banco, migrada do JSON legado
            (quando o ID buscado for o ativo e existir o arquivo legado), ou None
            quando não houver registro nem arquivo legado.
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


def usuario_crud():
    """Cria e retorna uma instância de UsuarioCRUD com a configuração padrão do banco.

    Retorna:
        UsuarioCRUD: Instância pronta para uso com usuario_ativo_id do database_config.
    """
    return UsuarioCRUD()


def criar_usuario(nome, idade):
    """Cria e persiste o usuário ativo com nome e idade informados.

    Recebe:
        nome (str): Nome do jogador.
        idade (int | str): Idade do jogador.

    Retorna:
        Usuario: Instância criada e salva no banco.
    """
    return usuario_crud().criar(nome, idade)


def salvar_usuario(usuario):
    """Persiste as alterações de um usuário existente no SQLite.

    Recebe:
        usuario (Usuario | dict): Dados do usuário; dicionários legados são
        normalizados antes da escrita.

    Retorna:
        Usuario: Instância normalizada que foi persistida.
    """
    return usuario_crud().salvar(usuario)


def carregar_usuario(usuario_id=None):
    """Carrega um usuário do SQLite pelo ID, com fallback para migração do JSON legado.

    Recebe:
        usuario_id (int | None): ID a buscar; None carrega o usuário ativo padrão.

    Retorna:
        Usuario | None: Instância encontrada, migrada do JSON legado, ou None.
    """
    return usuario_crud().carregar(usuario_id)


def obter_usuario_id(usuario=None):
    """Resolve o ID inteiro de um usuário a partir de instâncias, dicionários ou None.

    Recebe:
        usuario (Usuario | dict | None): Valor a resolver.

    Retorna:
        int: ID do objeto informado, ou USUARIO_ATIVO_ID quando usuario for None
        ou não tiver ID definido.
    """
    usuario = garantir_usuario(usuario)
    if usuario and usuario.id:
        return usuario.id
    return database_config.USUARIO_ATIVO_ID
