"""Testes das regras de nivel e ganho de XP."""

from backend.usuario import Usuario
from backend import xp_system


def test_calcular_nivel_respeita_limites():
    assert xp_system.calcular_nivel(0) == 1
    assert xp_system.calcular_nivel(99) == 1
    assert xp_system.calcular_nivel(100) == 2
    assert xp_system.calcular_nivel(249) == 2
    assert xp_system.calcular_nivel(250) == 3
    assert xp_system.calcular_nivel(449) == 3
    assert xp_system.calcular_nivel(450) == 4
    assert xp_system.calcular_nivel(699) == 4
    assert xp_system.calcular_nivel(700) == 5


def test_xp_para_proximo_nivel_no_maximo_retorna_zero():
    assert xp_system.xp_para_proximo_nivel(0) == 100
    assert xp_system.xp_para_proximo_nivel(100) == 150
    assert xp_system.xp_para_proximo_nivel(450) == 250
    assert xp_system.xp_para_proximo_nivel(700) == 0
    assert xp_system.xp_para_proximo_nivel(999) == 0


def test_adicionar_xp_persiste_usuario(monkeypatch):
    salvos = []
    monkeypatch.setattr(xp_system, "salvar_usuario", salvos.append)
    usuario = Usuario(nome="Ada", idade=12, xp=95, nivel=1)

    subiu, novo_nivel = xp_system.adicionar_xp(usuario, 10)

    assert subiu is True
    assert novo_nivel == 2
    assert usuario.xp == 105
    assert salvos == [usuario]
