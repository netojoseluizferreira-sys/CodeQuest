"""Testes das regras de nivel e ganho de XP."""

from backend import xp_system
from backend.usuario import Usuario


def test_xp_maximo_para_niveis_reflete_conteudo_implementado():
    assert xp_system.xp_maximo_para_niveis() == 1200


def test_limiares_niveis_seguem_curva_definida_para_1200_xp():
    assert xp_system.limiares_niveis() == [100, 200, 300, 600, 1200]


def test_calcular_nivel_respeita_limites_definidos():
    assert xp_system.calcular_nivel(0) == 1
    assert xp_system.calcular_nivel(100) == 1
    assert xp_system.calcular_nivel(101) == 2
    assert xp_system.calcular_nivel(200) == 2
    assert xp_system.calcular_nivel(201) == 3
    assert xp_system.calcular_nivel(300) == 3
    assert xp_system.calcular_nivel(301) == 4
    assert xp_system.calcular_nivel(600) == 4
    assert xp_system.calcular_nivel(601) == 5
    assert xp_system.calcular_nivel(1200) == 5
    assert xp_system.calcular_nivel(9999) == 5


def test_xp_para_proximo_nivel_no_maximo_retorna_zero():
    assert xp_system.xp_para_proximo_nivel(0) == 200
    assert xp_system.xp_para_proximo_nivel(100) == 100
    assert xp_system.xp_para_proximo_nivel(200) == 100
    assert xp_system.xp_para_proximo_nivel(300) == 300
    assert xp_system.xp_para_proximo_nivel(600) == 600
    assert xp_system.xp_para_proximo_nivel(1199) == 1
    assert xp_system.xp_para_proximo_nivel(1200) == 0
    assert xp_system.xp_para_proximo_nivel(9999) == 0


def test_adicionar_xp_persiste_usuario(monkeypatch):
    salvos = []
    monkeypatch.setattr(xp_system, "salvar_usuario", salvos.append)
    usuario = Usuario(nome="Ada", idade=12, xp=95, nivel=1)

    subiu, novo_nivel = xp_system.adicionar_xp(usuario, 10)

    assert subiu is True
    assert novo_nivel == 2
    assert usuario.xp == 105
    assert salvos == [usuario]
