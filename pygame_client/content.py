"""Adaptadores de conteúdo usados pelo fluxo de aula no Pygame."""

from backend.exercicio import carregar_aula, carregar_exercicios


def corrigir_texto(texto):
    """Corrige mojibake UTF-8 lido como Latin-1 em arquivos de conteúdo legados.

    Recebe:
        texto: Valor que pode ser string ou qualquer outro tipo. Tipos não-string
        são devolvidos sem alteração.

    Retorna:
        str: Texto recodificado de latin-1 para utf-8 quando a conversão for válida;
        o valor original quando o texto já estiver correto ou não for string.
    """
    if not isinstance(texto, str):
        return texto
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def corrigir_conteudo(valor):
    """Aplica corrigir_texto recursivamente em dicionários, listas e valores primitivos.

    Recebe:
        valor: Estrutura arbitrária de dados — dict, list, str ou primitivo.

    Retorna:
        Estrutura de mesmo formato com todos os textos corrigidos por corrigir_texto.
    """
    if isinstance(valor, dict):
        return {chave: corrigir_conteudo(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [corrigir_conteudo(item) for item in valor]
    return corrigir_texto(valor)


def carregar_aula_pygame(mundo, aula_id):
    """Carrega os dados de uma aula do JSON e corrige encodings para uso no Pygame.

    Recebe:
        mundo (str): Identificador do mundo, ex.: "mundo_1".
        aula_id (str): Identificador da aula dentro do mundo, ex.: "aula_1".

    Retorna:
        dict | None: Dicionário da aula com todos os textos corrigidos,
        ou None quando o mundo ou aula não existir no JSON.
    """
    aula = carregar_aula(mundo, aula_id)
    return None if aula is None else corrigir_conteudo(aula)


def carregar_exercicios_pygame(mundo):
    """Carrega os exercícios de um mundo do JSON e corrige encodings para uso no Pygame.

    Recebe:
        mundo (str): Identificador do mundo, ex.: "mundo_1".

    Retorna:
        dict: Dicionário de exercícios indexado por ID com textos corrigidos.
        Retorna dicionário vazio em caso de erro de leitura.
    """
    return corrigir_conteudo(carregar_exercicios(mundo))


def obter_exercicio(exercicios, exercicio_id):
    """Busca um exercício pelo seu ID dentro do dicionário de exercícios de um mundo.

    Recebe:
        exercicios (dict): Dicionário retornado por carregar_exercicios_pygame,
        com IDs de exercício como chaves string.
        exercicio_id (str | int): ID do exercício; convertido para str internamente.

    Retorna:
        dict | None: Dicionário com os dados do exercício, ou None quando o ID
        não existir no dicionário.
    """
    return exercicios.get(str(exercicio_id))
