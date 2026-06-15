"""Repositorio SQLite e configuracao das conquistas do jogador."""

import json
import os
from contextlib import closing

from utils.database_connection import conectar, inicializar_banco
from utils.user_repository import obter_usuario_id


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONQUISTAS_CONFIG_PATH = os.path.join(BASE_DIR, "data", "conquistas.json")


def carregar_conquistas_config():
    """Carrega a lista de conquistas configuradas em JSON."""
    with open(CONQUISTAS_CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if isinstance(dados, dict):
        return list(dados.values())
    return dados


def obter_conquista(conquista_id):
    """Retorna a configuracao de uma conquista pelo id, ou None."""
    return next(
        (conquista for conquista in carregar_conquistas_config() if conquista["id"] == conquista_id),
        None,
    )


def usuario_tem_conquista(usuario, conquista_id):
    """Verifica se o usuario informado ja possui a conquista."""
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        linha = conexao.execute(
            """
            SELECT 1
            FROM usuario_conquistas
            WHERE usuario_id = ? AND conquista_id = ?
            """,
            (usuario_id, conquista_id),
        ).fetchone()

    return linha is not None


def desbloquear_conquista(usuario, conquista_id):
    """Desbloqueia uma conquista de forma idempotente.

    Retorna True apenas quando uma nova linha foi inserida.
    """
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        cursor = conexao.execute(
            """
            INSERT OR IGNORE INTO usuario_conquistas (usuario_id, conquista_id)
            VALUES (?, ?)
            """,
            (usuario_id, conquista_id),
        )

    return cursor.rowcount == 1


def listar_conquistas_usuario(usuario):
    """Lista os ids das conquistas desbloqueadas pelo usuario."""
    inicializar_banco()
    usuario_id = obter_usuario_id(usuario)

    with closing(conectar()) as conexao, conexao:
        linhas = conexao.execute(
            """
            SELECT conquista_id
            FROM usuario_conquistas
            WHERE usuario_id = ?
            ORDER BY data_desbloqueio, conquista_id
            """,
            (usuario_id,),
        ).fetchall()

    return [linha["conquista_id"] for linha in linhas]


def listar_conquistas_com_estado(usuario):
    """Lista todas as conquistas configuradas com estado visual para o perfil."""
    desbloqueadas = set(listar_conquistas_usuario(usuario))
    conquistas = []

    for conquista in carregar_conquistas_config():
        desbloqueada = conquista["id"] in desbloqueadas
        caminho_imagem = (
            conquista["imagem_desbloqueada"] if desbloqueada else conquista["imagem_bloqueada"]
        )
        conquistas.append(
            {
                **conquista,
                "desbloqueada": desbloqueada,
                "imagem": caminho_imagem,
                "tooltip_titulo": conquista["nome"] if desbloqueada else "???",
                "tooltip_texto": "Conquista desbloqueada." if desbloqueada else f"Dica: {conquista['dica']}",
            }
        )

    return conquistas
