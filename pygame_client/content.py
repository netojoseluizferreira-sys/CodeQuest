from backend.exercicio import carregar_aula, carregar_exercicios


def corrigir_texto(texto):
    """Corrige textos UTF-8 lidos como Latin-1 quando necessario.

    Recebe:
        texto: Valor textual vindo dos arquivos de conteudo.

    Retorna:
        Texto corrigido quando houver mojibake; caso contrario, o texto original.
    """
    if not isinstance(texto, str):
        return texto
    try:
        return texto.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texto


def corrigir_conteudo(valor):
    """Aplica correcao de texto recursivamente em estruturas de conteudo.

    Recebe:
        valor: Dicionario, lista, texto ou valor primitivo.

    Retorna:
        Estrutura equivalente com textos corrigidos.
    """
    if isinstance(valor, dict):
        return {chave: corrigir_conteudo(item) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [corrigir_conteudo(item) for item in valor]
    return corrigir_texto(valor)


def carregar_aula_pygame(mundo, aula_id):
    """Carrega uma aula preparada para exibicao no Pygame.

    Recebe:
        mundo: Identificador do mundo da aula.
        aula_id: Identificador da aula.

    Retorna:
        Dicionario da aula com textos corrigidos ou None.
    """
    aula = carregar_aula(mundo, aula_id)
    return None if aula is None else corrigir_conteudo(aula)


def carregar_exercicios_pygame(mundo):
    """Carrega os exercicios de um mundo para uso no Pygame.

    Recebe:
        mundo: Identificador do mundo desejado.

    Retorna:
        Dicionario de exercicios com textos corrigidos.
    """
    return corrigir_conteudo(carregar_exercicios(mundo))


def obter_exercicio(exercicios, exercicio_id):
    """Busca um exercicio por ID dentro do conjunto de um mundo.

    Recebe:
        exercicios: Dicionario de exercicios do mundo.
        exercicio_id: Identificador numerico ou textual do exercicio.

    Retorna:
        Dicionario do exercicio ou None quando nao existir.
    """
    return exercicios.get(str(exercicio_id))
