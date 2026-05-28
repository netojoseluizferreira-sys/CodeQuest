XP_BASE_PADRAO = 10
XP_MINIMO_POR_EXERCICIO = 2
PENALIDADE_XP_POR_ERRO = 2


def calcular_xp_disponivel(exercicio, erros):
    """Calcula o XP disponivel apos penalidades por erro.

    Recebe:
        exercicio: Dicionario com dados e XP base do exercicio.
        erros: Quantidade de erros ja cometidos no exercicio.

    Retorna:
        XP que ainda pode ser recebido, respeitando o minimo configurado.
    """
    xp_base = exercicio.get("xp", XP_BASE_PADRAO)
    xp_com_penalidade = xp_base - (erros * PENALIDADE_XP_POR_ERRO)
    return max(XP_MINIMO_POR_EXERCICIO, xp_com_penalidade)


def frase_xp_disponivel(xp):
    """Seleciona a mensagem exibida para o XP disponivel.

    Recebe:
        xp: Quantidade de XP disponivel no exercicio.

    Retorna:
        Texto de feedback correspondente ao XP informado.
    """
    frases = {
        10: "🌟 Perfeito ate aqui: este desafio ainda vale 10 XP!",
        8: "💪 Um tropeco so: ainda da para garantir 8 XP.",
        6: "🧠 Ajustando a rota: agora este desafio vale 6 XP.",
        4: "🔥 Persistencia conta: voce ainda pode ganhar 4 XP.",
        2: "🛡️ Modo resgate: o minimo garantido agora e 2 XP.",
    }
    return frases.get(xp, f"⭐ Este desafio vale {xp} XP agora.")
