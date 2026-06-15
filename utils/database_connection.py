"""Abertura da conexão SQLite e criação das tabelas necessárias."""

import os
import sqlite3
from contextlib import closing

from utils import database_config


def conectar():
    """Abre e retorna uma conexão com o banco SQLite local definido em database_config.

    Cria o diretório data/ se não existir. Configura row_factory para sqlite3.Row,
    permitindo acesso às colunas pelo nome em vez de índice.

    Retorna:
        sqlite3.Connection: Conexão aberta e configurada; deve ser fechada pelo
        chamador, preferencialmente via contextlib.closing.
    """
    os.makedirs(database_config.DATA_DIR, exist_ok=True)
    conexao = sqlite3.connect(database_config.DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    """Cria as tabelas do banco caso ainda não existam (CREATE TABLE IF NOT EXISTS).

    Garante a existência das tabelas de usuário, exercícios, mundos e erros,
    com suas respectivas chaves primárias e estrangeiras.
    Seguro para chamadas repetidas; não destrói dados existentes.
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
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS mundos_concluidos (
                usuario_id INTEGER NOT NULL,
                mundo_id TEXT NOT NULL,
                concluido INTEGER NOT NULL DEFAULT 0,
                data_conclusao TEXT,
                PRIMARY KEY (usuario_id, mundo_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuario_conquistas (
                usuario_id INTEGER NOT NULL,
                conquista_id TEXT NOT NULL,
                data_desbloqueio TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (usuario_id, conquista_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            """
        )
