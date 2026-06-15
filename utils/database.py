"""Fachada pública das operações de persistência SQLite do CodeQuest."""

import os
from contextlib import closing

from utils import database_config
from utils.database_connection import conectar, inicializar_banco
from utils.exercise_progress_repository import (
    exercicio_foi_concluido,
    marcar_exercicio_concluido,
    obter_erros_exercicio,
    registrar_erro_exercicio,
)
from utils.world_progress_repository import (
    STATUS_BLOQUEADO,
    STATUS_DISPONIVEL,
    STATUS_EM_BREVE,
    garantir_progresso_mundo,
    listar_mundos_concluidos,
    marcar_mundo_concluido,
    mundo_concluido,
    obter_status_mundo,
    verificar_e_marcar_conclusao_mundo,
)
from utils.user_repository import (
    UsuarioCRUD,
    carregar_usuario,
    criar_usuario,
    garantir_usuario,
    obter_usuario_id,
    salvar_usuario,
    usuario_crud,
)


BASE_DIR = database_config.BASE_DIR
DATA_DIR = database_config.DATA_DIR
DB_PATH = database_config.DB_PATH
LEGACY_USUARIO_JSON_PATH = database_config.LEGACY_USUARIO_JSON_PATH
LEGACY_PROGRESSO_JSON_PATH = database_config.LEGACY_PROGRESSO_JSON_PATH
USUARIO_ATIVO_ID = database_config.USUARIO_ATIVO_ID


def resetar_banco_de_dados():
    """Apaga todos os dados das três tabelas e remove os arquivos de save legados.

    Deleta todas as linhas de usuarios, mundos_concluidos,
    exercicios_concluidos e exercicio_erros via DELETE sem cláusula WHERE, e
    remove os JSONs legados de usuário e
    progresso quando existirem. Usado exclusivamente em testes; não deve ser
    chamado em produção.
    """
    inicializar_banco()

    with closing(conectar()) as conexao, conexao:
        conexao.execute("DELETE FROM mundos_concluidos")
        conexao.execute("DELETE FROM exercicios_concluidos")
        conexao.execute("DELETE FROM exercicio_erros")
        conexao.execute("DELETE FROM usuarios")

    caminhos_legados = (
        database_config.LEGACY_USUARIO_JSON_PATH,
        database_config.LEGACY_PROGRESSO_JSON_PATH,
    )
    for caminho_legado in caminhos_legados:
        if os.path.exists(caminho_legado):
            os.remove(caminho_legado)
