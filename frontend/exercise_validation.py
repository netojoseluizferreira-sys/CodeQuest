import re
import unicodedata


def normalizar_resposta_texto(texto):
    """Normaliza texto para comparacao tolerante de respostas abertas.

    Recebe:
        texto: Resposta digitada ou resposta aceita cadastrada.

    Retorna:
        Texto em minusculas, sem acentos e com separadores padronizados.
    """
    sem_acentos = unicodedata.normalize("NFD", texto.lower())
    sem_acentos = "".join(char for char in sem_acentos if unicodedata.category(char) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", sem_acentos).strip()


def resposta_correta(exercicio, resposta):
    """Valida a resposta enviada para um exercicio.

    Recebe:
        exercicio: Dicionario com tipo, opcoes e resposta esperada.
        resposta: Valor informado pelo usuario na interface.

    Retorna:
        True quando a resposta esta correta; caso contrario, False.
    """
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        resposta_normalizada = normalizar_resposta_texto(resposta or "")
        respostas_aceitas = [
            normalizar_resposta_texto(item)
            for item in exercicio.get("respostas_aceitas", [])
        ]
        return resposta_normalizada in respostas_aceitas

    return resposta == exercicio["opcoes"][exercicio["resposta"]]


def resposta_vazia(exercicio, resposta):
    """Verifica se a resposta atual ainda esta vazia.

    Recebe:
        exercicio: Dicionario com dados do exercicio.
        resposta: Valor atual do campo de resposta.

    Retorna:
        True quando nao ha resposta valida; caso contrario, False.
    """
    if exercicio.get("tipo", "multipla_escolha") == "completar":
        return not resposta or not resposta.strip()

    return resposta is None
