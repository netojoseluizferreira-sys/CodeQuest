"""Testes do sistema de conquistas visuais."""

import pytest

from backend.achievements import (
    MELHOR_PROFESSOR_UFAL,
    nome_desbloqueia_melhor_professor,
)
from utils import database
from utils.database_connection import conectar


def _estado(conquistas, conquista_id):
    return next(conquista for conquista in conquistas if conquista["id"] == conquista_id)


def test_conquista_comeca_bloqueada_com_dica(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)

    conquistas = database.listar_conquistas_com_estado(usuario)
    conquista = _estado(conquistas, MELHOR_PROFESSOR_UFAL)

    assert conquista["desbloqueada"] is False
    assert conquista["tooltip_titulo"] == "???"
    assert conquista["tooltip_texto"] == "Dica: Quem é o melhor professor da UFAL?"
    assert conquista["imagem"].endswith("locked_question.png")


def test_desbloquear_conquista_salva_no_banco_e_nao_duplica(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)

    assert database.desbloquear_conquista(usuario, MELHOR_PROFESSOR_UFAL) is True
    assert database.desbloquear_conquista(usuario, MELHOR_PROFESSOR_UFAL) is False

    with conectar() as conexao:
        total = conexao.execute(
            """
            SELECT COUNT(*) AS total
            FROM usuario_conquistas
            WHERE usuario_id = ? AND conquista_id = ?
            """,
            (usuario.id, MELHOR_PROFESSOR_UFAL),
        ).fetchone()["total"]

    assert total == 1
    assert database.usuario_tem_conquista(usuario, MELHOR_PROFESSOR_UFAL) is True
    assert database.listar_conquistas_usuario(usuario) == [MELHOR_PROFESSOR_UFAL]


@pytest.mark.parametrize(
    "nome",
    [
        "barbosa",
        "alexandre",
        "alexandre barbosa",
        "prof barbosa",
        "professor barbosa",
        "prof alexandre",
        "professor alexandre",
        "  PROF   BARBOSA  ",
        "Alexandre Barbosa",
    ],
)
def test_variacoes_de_nome_desbloqueiam_melhor_professor(nome, banco_temporario):
    usuario = database.criar_usuario(nome, 12)

    assert nome_desbloqueia_melhor_professor(nome) is True
    assert database.usuario_tem_conquista(usuario, MELHOR_PROFESSOR_UFAL) is True


def test_conquista_desbloqueada_retorna_nome_estado_e_imagem_real(banco_temporario):
    usuario = database.criar_usuario("Alexandre", 12)

    conquista = _estado(database.listar_conquistas_com_estado(usuario), MELHOR_PROFESSOR_UFAL)

    assert conquista["desbloqueada"] is True
    assert conquista["tooltip_titulo"] == "Melhor professor da UFAL"
    assert conquista["tooltip_texto"] == "Conquista desbloqueada."
    assert conquista["imagem"].endswith("melhor_professor_ufal.png")
