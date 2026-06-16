"""Testes das regras de nivel e ganho de XP."""

from backend import xp_system
from backend.usuario import Usuario


def test_xp_maximo_para_niveis_reflete_conteudo_implementado():
    assert xp_system.xp_maximo_para_niveis() == 1200


def test_limiares_niveis_sao_distribuidos_ate_o_xp_maximo():
    assert xp_system.limiares_niveis(1200) == [134, 267, 400, 534, 667, 800, 934, 1067, 1200]


def test_calcular_nivel_respeita_limites_dinamicos():
    assert xp_system.calcular_nivel(0) == 1
    assert xp_system.calcular_nivel(133) == 1
    assert xp_system.calcular_nivel(134) == 2
    assert xp_system.calcular_nivel(399) == 3
    assert xp_system.calcular_nivel(400) == 4
    assert xp_system.calcular_nivel(1199) == 9
    assert xp_system.calcular_nivel(1200) == 10
    assert xp_system.calcular_nivel(9999) == 10


def test_xp_para_proximo_nivel_no_maximo_retorna_zero():
    assert xp_system.xp_para_proximo_nivel(0) == 134
    assert xp_system.xp_para_proximo_nivel(134) == 133
    assert xp_system.xp_para_proximo_nivel(400) == 134
    assert xp_system.xp_para_proximo_nivel(1199) == 1
    assert xp_system.xp_para_proximo_nivel(1200) == 0
    assert xp_system.xp_para_proximo_nivel(9999) == 0


def test_adicionar_xp_persiste_usuario(monkeypatch):
    salvos = []
    monkeypatch.setattr(xp_system, "salvar_usuario", salvos.append)
    usuario = Usuario(nome="Ada", idade=12, xp=130, nivel=1)

    subiu, novo_nivel = xp_system.adicionar_xp(usuario, 10)

    assert subiu is True
    assert novo_nivel == 2
    assert usuario.xp == 140
    assert salvos == [usuario]
