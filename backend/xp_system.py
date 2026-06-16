"""Regras de nivel e persistencia de XP do jogador."""

from backend.achievements import xp_maximo_disponivel
from utils.database import salvar_usuario


NIVEL_MINIMO = 1
NIVEL_MAXIMO = 5
LIMIARES_NIVEIS = (100, 200, 300, 600, 1200)


def xp_maximo_para_niveis():
    """Retorna o teto de XP usado para distribuir os niveis."""
    return max(0, int(xp_maximo_disponivel()))


def limiares_niveis(xp_maximo=None):
    """Retorna os marcos de XP de cada nivel.

    O parametro opcional existe para manter compatibilidade com testes e usos
    antigos; a curva oficial foi definida para o teto atual de 1200 XP.
    """
    return list(LIMIARES_NIVEIS)


def calcular_nivel(xp):
    """Mapeia XP acumulado para um nivel entre 1 e 5."""
    xp_atual = max(0, int(xp))
    for indice, limiar in enumerate(limiares_niveis(), start=NIVEL_MINIMO):
        if xp_atual <= limiar:
            return indice
    return NIVEL_MAXIMO


def adicionar_xp(usuario, quantidade):
    """Soma XP ao usuario, recalcula o nivel e persiste o estado no banco."""
    subiu, novo_nivel = usuario.adicionar_xp(quantidade, calcular_nivel)
    salvar_usuario(usuario)

    return subiu, novo_nivel


def xp_para_proximo_nivel(xp_atual):
    """Calcula quanto XP falta para o proximo nivel."""
    xp_atual = max(0, int(xp_atual))
    for limiar in limiares_niveis()[1:]:
        if xp_atual < limiar:
            return limiar - xp_atual
    return 0
