"""Regras de nivel e persistencia de XP do jogador."""

from utils.database import salvar_usuario


def calcular_nivel(xp):
    """Mapeia XP acumulado para o nível do jogador usando limiares fixos.

    Limiares: nível 1 < 100 XP, nível 2 < 250, nível 3 < 450, nível 4 < 700,
    nível 5 a partir de 700 XP.

    Recebe:
        xp (int): Total de XP acumulado pelo usuário.

    Retorna:
        int: Nível entre 1 e 5 correspondente ao XP informado.
    """
    if xp < 100:
        return 1
    if xp < 250:
        return 2
    if xp < 450:
        return 3
    if xp < 700:
        return 4
    return 5


def adicionar_xp(usuario, quantidade):
    """Soma XP ao usuário, recalcula o nível e persiste o estado no banco.

    Recebe:
        usuario (Usuario): Instância do usuário ativo; modificada in-place.
        quantidade (int): Pontos de XP a adicionar.

    Retorna:
        tuple[bool, int]: Par (subiu_nivel, novo_nivel) repassado de
        Usuario.adicionar_xp, onde subiu_nivel é True quando o nível aumentou.
    """
    subiu, novo_nivel = usuario.adicionar_xp(quantidade, calcular_nivel)
    salvar_usuario(usuario)

    return subiu, novo_nivel


def xp_para_proximo_nivel(xp_atual):
    """Calcula quantos pontos de XP faltam para o jogador alcançar o próximo nível.

    Recebe:
        xp_atual (int): Total de XP atual do usuário.

    Retorna:
        int: XP restante até o próximo limiar; 0 quando o jogador estiver
        no nível máximo (>= 700 XP).
    """
    if xp_atual < 100:
        return 100 - xp_atual
    if xp_atual < 250:
        return 250 - xp_atual
    if xp_atual < 450:
        return 450 - xp_atual
    if xp_atual < 700:
        return 700 - xp_atual
    return 0
