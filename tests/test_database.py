"""Testes da fachada pública de persistência SQLite."""

import json
import os

from backend.usuario import Usuario
from backend.worlds import exercicios_obrigatorios
from utils import database
from utils import database_config
from utils.database_connection import conectar


def test_salva_e_carrega_usuario_com_dataclass(banco_temporario):
    usuario = Usuario.criar("Teste", 12)

    database.salvar_usuario(usuario)
    carregado = database.carregar_usuario()

    assert isinstance(carregado, Usuario)
    assert carregado.nome == "Teste"
    assert carregado.id == database.USUARIO_ATIVO_ID
    assert carregado.nivel == 1


def test_salva_usuario_a_partir_de_dicionario_legado(banco_temporario):
    database.salvar_usuario({"nome": "Legado", "idade": 15, "xp": 8})

    carregado = database.carregar_usuario()

    assert carregado.nome == "Legado"
    assert carregado.xp == 8
    assert carregado.nivel == 1


def test_criar_usuario_substitui_save_ativo_por_upsert(banco_temporario):
    primeiro = database.criar_usuario("Primeiro", 12)
    primeiro.xp = 20
    database.salvar_usuario(primeiro)

    segundo = database.criar_usuario("Segundo", 13)
    carregado = database.carregar_usuario()

    assert segundo.id == database.USUARIO_ATIVO_ID
    assert carregado.nome == "Segundo"
    assert carregado.xp == 0


def test_migra_usuario_json_legado_quando_banco_esta_vazio(banco_temporario):
    legado = {"nome": "Json", "idade": 9, "xp": 30, "nivel": 1, "conquistas": ["inicio"]}
    with open(database_config.LEGACY_USUARIO_JSON_PATH, "w", encoding="utf-8") as arquivo:
        json.dump(legado, arquivo)

    usuario = database.carregar_usuario()

    assert usuario.nome == "Json"
    assert usuario.xp == 30
    assert database.carregar_usuario().conquistas == ["inicio"]


def test_carregar_usuario_inexistente_retorna_none(banco_temporario):
    assert database.carregar_usuario(usuario_id=999) is None


def test_persiste_erros_e_exercicio_concluido(banco_temporario):
    usuario = database.criar_usuario("Teste", 12)

    assert database.registrar_erro_exercicio("mundo_1", "1", usuario) == 1
    assert database.registrar_erro_exercicio("mundo_1", "1", usuario) == 2

    database.marcar_exercicio_concluido("mundo_1", "1", 6, usuario)

    assert database.obter_erros_exercicio("mundo_1", "1", usuario) == 2
    assert database.exercicio_foi_concluido("mundo_1", "1", usuario) is True


def test_progresso_de_exercicio_e_isolado_por_usuario(banco_temporario):
    usuario_1 = database.criar_usuario("Um", 10)
    usuario_2 = Usuario(nome="Dois", idade=11, id=2)
    database.salvar_usuario(usuario_2)

    database.marcar_exercicio_concluido("mundo_1", "1", 10, usuario_1)

    assert database.exercicio_foi_concluido("mundo_1", "1", usuario_1) is True
    assert database.exercicio_foi_concluido("mundo_1", "1", usuario_2) is False


def test_mundo_comeca_nao_concluido_e_pode_ser_marcado(banco_temporario):
    usuario = database.criar_usuario("Teste", 12)

    database.garantir_progresso_mundo("mundo_1", usuario)

    assert database.mundo_concluido("mundo_1", usuario) is False

    database.marcar_mundo_concluido("mundo_1", usuario)

    assert database.mundo_concluido("mundo_1", usuario) is True
    assert database.listar_mundos_concluidos(usuario) == ["mundo_1"]


def test_conclusao_de_mundo_nao_duplica_registros(banco_temporario):
    usuario = database.criar_usuario("Teste", 12)

    database.marcar_mundo_concluido("mundo_1", usuario)
    database.marcar_mundo_concluido("mundo_1", usuario)

    with conectar() as conexao:
        total = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM mundos_concluidos
            WHERE usuario_id = ? AND mundo_id = ?
            """,
            (usuario.id, "mundo_1"),
        ).fetchone()["total"]

    assert total == 1


def test_status_de_mundos_respeita_configuracao_de_desbloqueio(banco_temporario):
    usuario = database.criar_usuario("Teste", 12)

    assert database.obter_status_mundo("mundo_1", usuario)["estado"] == database.STATUS_DISPONIVEL
    assert database.obter_status_mundo("mundo_2", usuario)["estado"] == database.STATUS_BLOQUEADO

    database.marcar_mundo_concluido("mundo_1", usuario)

    assert database.obter_status_mundo("mundo_2", usuario)["estado"] == database.STATUS_DISPONIVEL


def test_mundo_nao_implementado_aparece_em_breve(banco_temporario):
    usuario = database.criar_usuario("Teste", 12)
    database.marcar_mundo_concluido("mundo_6", usuario)

    status = database.obter_status_mundo("mundo_7", usuario)

    assert status["estado"] == database.STATUS_EM_BREVE


def test_mundo_concluido_migra_progresso_antigo_de_exercicios(banco_temporario):
    usuario = database.criar_usuario("Teste", 12)

    for exercicio_id in exercicios_obrigatorios("mundo_1"):
        database.marcar_exercicio_concluido("mundo_1", exercicio_id, 10, usuario)

    with conectar() as conexao:
        antes = conexao.execute("SELECT COUNT(*) AS total FROM mundos_concluidos").fetchone()["total"]

    assert antes == 0
    assert database.mundo_concluido("mundo_1", usuario) is True

    with conectar() as conexao:
        depois = conexao.execute("SELECT COUNT(*) AS total FROM mundos_concluidos").fetchone()["total"]

    assert depois == 1


def test_resetar_banco_remove_dados_e_arquivos_legados(banco_temporario):
    database.criar_usuario("Teste", 12)
    database.marcar_mundo_concluido("mundo_1")
    with open(database_config.LEGACY_PROGRESSO_JSON_PATH, "w", encoding="utf-8") as arquivo:
        json.dump({"qualquer": "valor"}, arquivo)

    database.resetar_banco_de_dados()

    assert database.carregar_usuario() is None
    assert database.listar_mundos_concluidos() == []
    assert not os.path.exists(database_config.LEGACY_PROGRESSO_JSON_PATH)
