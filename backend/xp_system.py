from utils.database import salvar_usuario


def calcular_nivel(xp):
    """Calcula o nivel do usuario a partir do XP acumulado.

    Recebe:
        xp: Quantidade total de XP do usuario.

    Retorna:
        Numero inteiro do nivel correspondente ao XP informado.
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
    """Adiciona XP ao usuario, atualiza seu nivel e persiste a alteracao.

    Recebe:
        usuario: Instancia de Usuario que recebera o XP.
        quantidade: Total de XP a ser somado.

    Retorna:
        Uma tupla com um booleano indicando subida de nivel e o novo nivel.
    """
    subiu, novo_nivel = usuario.adicionar_xp(quantidade, calcular_nivel)
    salvar_usuario(usuario)

    return subiu, novo_nivel


def xp_para_proximo_nivel(xp_atual):
    """Calcula quanto XP falta para o proximo nivel.

    Recebe:
        xp_atual: Quantidade total de XP atual do usuario.

    Retorna:
        Quantidade de XP restante ate o proximo nivel, ou 0 no nivel maximo.
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


def progresso_para_proximo_nivel(xp_atual):
    """Calcula a porcentagem de progresso dentro do nivel atual.

    Recebe:
        xp_atual: Quantidade total de XP atual do usuario.

    Retorna:
        Valor entre 0.0 e 1.0 usado pelo componente de progresso.
    """
    if xp_atual >= 700:
        return 1.0
    if xp_atual < 100:
        return xp_atual / 100
    if xp_atual < 250:
        return (xp_atual - 100) / 150
    if xp_atual < 450:
        return (xp_atual - 250) / 200
    return (xp_atual - 450) / 250
