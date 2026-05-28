import os
import sqlite3
from contextlib import closing

from utils import database_config


def conectar():
    """Abre uma conexao com o banco SQLite local.

    Recebe:
        Nenhum parametro.

    Retorna:
        Conexao SQLite configurada para acessar colunas pelo nome.
    """
    os.makedirs(database_config.DATA_DIR, exist_ok=True)
    conexao = sqlite3.connect(database_config.DB_PATH)
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
