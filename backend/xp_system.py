"""Regras de nivel e persistencia de XP do jogador."""

from math import ceil

from backend.achievements import xp_maximo_disponivel
from utils.database import salvar_usuario


NIVEL_MINIMO = 1
NIVEL_MAXIMO = 10


def xp_maximo_para_niveis():
    """Retorna o teto de XP usado para distribuir os niveis."""
    return max(0, int(xp_maximo_disponivel()))


def limiares_niveis(xp_maximo=None):
    """Calcula limiares de nivel a partir do XP maximo disponivel."""
    xp_total = xp_maximo_para_niveis() if xp_maximo is None else max(0, int(xp_maximo))
    if xp_total <= 0:
        return []

    etapas = NIVEL_MAXIMO - NIVEL_MINIMO
    return [ceil((xp_total * passo) / etapas) for passo in range(1, etapas + 1)]


def calcular_nivel(xp):
    """Mapeia XP acumulado para um nivel entre 1 e 10."""
    xp_atual = max(0, int(xp))
    nivel = NIVEL_MINIMO
    for limiar in limiares_niveis():
        if xp_atual < limiar:
            return nivel
        nivel += 1
    return NIVEL_MAXIMO


def adicionar_xp(usuario, quantidade):
    """Soma XP ao usuario, recalcula o nivel e persiste o estado no banco."""
    subiu, novo_nivel = usuario.adicionar_xp(quantidade, calcular_nivel)
    salvar_usuario(usuario)

    return subiu, novo_nivel


def xp_para_proximo_nivel(xp_atual):
    """Calcula quanto XP falta para o proximo nivel."""
    xp_atual = max(0, int(xp_atual))
    for limiar in limiares_niveis():
        if xp_atual < limiar:
            return limiar - xp_atual
    return 0
