# backend/xp_system.py
from utils.json_utils import salvar_usuario

def calcular_nivel(xp):
    """Calcula o nível baseado no XP"""
    # Nível 1: 0-99 XP
    # Nível 2: 100-249 XP
    # Nível 3: 250-449 XP
    # Nível 4: 450-699 XP
    # Nível 5: 700+ XP
    if xp < 100:
        return 1
    elif xp < 250:
        return 2
    elif xp < 450:
        return 3
    elif xp < 700:
        return 4
    else:
        return 5

def adicionar_xp(usuario, quantidade):
    """Adiciona XP ao usuário e atualiza nível"""
    usuario['xp'] += quantidade
    novo_nivel = calcular_nivel(usuario['xp'])
    
    if novo_nivel > usuario.get('nivel', 1):
        usuario['nivel'] = novo_nivel
        return True, novo_nivel  # Subiu de nível!
    
    usuario['nivel'] = novo_nivel
    salvar_usuario(usuario)
    return False, novo_nivel

def xp_para_proximo_nivel(xp_atual):
    """Retorna quanto XP falta para o próximo nível"""
    if xp_atual < 100:
        return 100 - xp_atual
    elif xp_atual < 250:
        return 250 - xp_atual
    elif xp_atual < 450:
        return 450 - xp_atual
    elif xp_atual < 700:
        return 700 - xp_atual
    else:
        return 0  # Nível máximo
    
# backend/xp_system.py (adicione no final)

def progresso_para_proximo_nivel(xp_atual):
    """Retorna porcentagem de progresso para o próximo nível (0 a 1)"""
    if xp_atual >= 700:
        return 1.0
    
    if xp_atual < 100:
        return xp_atual / 100
    elif xp_atual < 250:
        return (xp_atual - 100) / 150
    elif xp_atual < 450:
        return (xp_atual - 250) / 200
    else:  # xp_atual < 700
        return (xp_atual - 450) / 250