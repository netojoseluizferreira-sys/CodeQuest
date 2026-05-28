from utils.database import salvar_usuario


def calcular_nivel(xp):
    """Calcula o nivel baseado no XP."""
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
    """Adiciona XP ao usuario e atualiza nivel."""
    subiu, novo_nivel = usuario.adicionar_xp(quantidade, calcular_nivel)
    salvar_usuario(usuario)

    return subiu, novo_nivel


def xp_para_proximo_nivel(xp_atual):
    """Retorna quanto XP falta para o proximo nivel."""
    if xp_atual < 100:
        return 100 - xp_atual
    if xp_atual < 250:
        return 250 - xp_atual
    if xp_atual < 450:
        return 450 - xp_atual
    if xp_atual < 700:
        return 700 - xp_atual
    return 0


def progresso_para_proximo_nivel(xp_atual):
    """Retorna porcentagem de progresso para o proximo nivel (0 a 1)."""
    if xp_atual >= 700:
        return 1.0
    if xp_atual < 100:
        return xp_atual / 100
    if xp_atual < 250:
        return (xp_atual - 100) / 150
    if xp_atual < 450:
        return (xp_atual - 250) / 200
    return (xp_atual - 450) / 250
