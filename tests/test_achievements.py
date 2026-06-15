"""Testes do sistema de conquistas visuais."""

import pytest

from backend.achievements import (
    FENOMENO,
    MELHOR_PROFESSOR_UFAL,
    QUASE_HEXA,
    XP_MINIMO_EXERCICIO,
    avaliar_progresso_usuario,
    nome_desbloqueia_melhor_professor,
    xp_maximo_disponivel,
)
from backend.worlds import exercicios_obrigatorios, listar_mundos, mundo_implementado
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


def test_fenomeno_so_desbloqueia_com_xp_maximo_possivel(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)
    usuario.xp = xp_maximo_disponivel() - 1

    assert avaliar_progresso_usuario(usuario) == []
    assert database.usuario_tem_conquista(usuario, FENOMENO) is False

    usuario.xp = xp_maximo_disponivel()
    desbloqueadas = avaliar_progresso_usuario(usuario)

    assert [conquista["id"] for conquista in desbloqueadas] == [FENOMENO]
    assert database.usuario_tem_conquista(usuario, FENOMENO) is True


def test_quase_hexa_nao_desbloqueia_no_inicio_com_xp_zero(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)

    avaliar_progresso_usuario(usuario)

    assert database.usuario_tem_conquista(usuario, QUASE_HEXA) is False


def test_quase_hexa_desbloqueia_com_todo_conteudo_no_xp_minimo(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)

    for mundo in listar_mundos():
        if not mundo_implementado(mundo["id"]):
            continue
        for exercicio_id in exercicios_obrigatorios(mundo["id"]):
            database.marcar_exercicio_concluido(
                mundo["id"],
                exercicio_id,
                XP_MINIMO_EXERCICIO,
                usuario,
            )

    desbloqueadas = avaliar_progresso_usuario(usuario)

    assert [conquista["id"] for conquista in desbloqueadas] == [QUASE_HEXA]
    assert database.usuario_tem_conquista(usuario, QUASE_HEXA) is True
