"""Validação de respostas, cálculo de XP e registro de progresso."""

import unicodedata

from backend.xp_system import adicionar_xp
from utils.database import (
    exercicio_foi_concluido,
    marcar_exercicio_concluido,
    obter_erros_exercicio,
    registrar_erro_exercicio,
)


XP_BASE = 10
XP_PENALIDADE_ERRO = 2
XP_MINIMO = 2


def calcular_xp_potencial(erros):
    """Calcula o XP máximo que ainda pode ser ganho em um exercício dado o número de erros.

    Recebe:
        erros (int): Quantidade de erros já registrados no exercício.

    Retorna:
        int: XP entre XP_MINIMO (2) e XP_BASE (10), reduzindo XP_PENALIDADE_ERRO
        (2 pontos) por erro acumulado.
    """
    return max(XP_BASE - (int(erros) * XP_PENALIDADE_ERRO), XP_MINIMO)


def frase_xp(xp):
    """Retorna a mensagem de feedback correspondente ao XP recebido ou potencial.

    Recebe:
        xp (int): Quantidade de XP (0, 2, 4, 6, 8 ou 10).

    Retorna:
        str: Mensagem amigável mapeada ao valor de XP, ou mensagem genérica
        para valores não mapeados.
    """
    frases = {
        10: "Perfeito! Você garantiu 10 XP.",
        8: "Muito bom! Um tropeço pequeno, 8 XP.",
        6: "Boa recuperação! Você levou 6 XP.",
        4: "Persistência conta: 4 XP.",
        2: "Conseguiu no limite mínimo: 2 XP.",
        0: "Exercício já concluído antes. Sem XP extra.",
    }
    return frases.get(xp, f"Você recebeu {xp} XP.")


def normalizar_resposta(resposta):
    """Normaliza texto livre para comparação insensível a maiúsculas, acentos e pontuação.

    Remove acentos via decomposição NFD, converte para minúsculas e substitui
    vírgulas, barras e hífens por espaços antes de colapsar múltiplos espaços.

    Recebe:
        resposta (str | any): Texto digitado pelo jogador; convertido para str.

    Retorna:
        str: Texto em minúsculas, sem marcas diacríticas e com espaços normalizados.
    """
    texto = unicodedata.normalize("NFD", str(resposta).strip().lower())
    texto = "".join(char for char in texto if unicodedata.category(char) != "Mn")
    return " ".join(texto.replace(",", " ").replace("/", " ").replace("-", " ").split())


def resposta_esta_correta(exercicio, resposta):
    """Valida a resposta enviada pelo jogador para um exercício.

    Para múltipla escolha, compara o índice numérico com o campo "resposta" do
    exercício. Para texto livre, normaliza a resposta e verifica se ela está na
    lista "respostas_aceitas".

    Recebe:
        exercicio (dict): Dicionário do exercício com campos "tipo", "resposta"
        (int para múltipla escolha) e "respostas_aceitas" (list[str] para texto livre).
        resposta (int | str): Índice da alternativa escolhida ou texto digitado.

    Retorna:
        bool: True quando a resposta for aceita; False caso contrário.
    """
    if exercicio["tipo"] == "multipla_escolha":
        return int(resposta) == int(exercicio["resposta"])

    resposta_normalizada = normalizar_resposta(resposta)
    respostas_aceitas = exercicio.get("respostas_aceitas", [])
    return resposta_normalizada in {
        normalizar_resposta(resposta_aceita) for resposta_aceita in respostas_aceitas
    }


def registrar_resposta(mundo, exercicio, resposta, usuario):
    """Registra uma tentativa de resposta, aplica XP e retorna o resultado.

    Se a resposta estiver correta e o exercício ainda não tiver sido concluído,
    calcula o XP pelo número de erros acumulados, chama adicionar_xp e persiste
    a conclusão. Se já concluído, retorna acerto sem XP. Se incorreta, incrementa
    o contador de erros e retorna o XP potencial restante.

    Recebe:
        mundo (str): Identificador do mundo do exercício, ex.: "mundo_1".
        exercicio (dict): Dicionário do exercício com pelo menos os campos
        "id" e "tipo".
        resposta (int | str): Índice da alternativa ou texto livre enviado.
        usuario (Usuario): Instância do usuário ativo que receberá o XP.

    Retorna:
        dict: Dicionário com as chaves:
            "acertou" (bool): Se a resposta foi aceita.
            "xp" (int): XP concedido nesta tentativa (0 em erros ou re-acerto).
            "erros" (int): Total de erros do exercício antes desta tentativa.
            "mensagem" (str): Feedback textual para exibição no Pygame.
    """
    exercicio_id = str(exercicio["id"])
    ja_concluido = exercicio_foi_concluido(mundo, exercicio_id, usuario)
    erros_antes = obter_erros_exercicio(mundo, exercicio_id, usuario)

    if resposta_esta_correta(exercicio, resposta):
        if ja_concluido:
            return {
                "acertou": True,
                "xp": 0,
                "erros": erros_antes,
                "mensagem": frase_xp(0),
            }

        xp_ganho = calcular_xp_potencial(erros_antes)
        adicionar_xp(usuario, xp_ganho)
        marcar_exercicio_concluido(mundo, exercicio_id, xp_ganho, usuario)
        return {
            "acertou": True,
            "xp": xp_ganho,
            "erros": erros_antes,
            "mensagem": frase_xp(xp_ganho),
        }

    erros_depois = registrar_erro_exercicio(mundo, exercicio_id, usuario)
    xp_potencial = 0 if ja_concluido else calcular_xp_potencial(erros_depois)
    return {
        "acertou": False,
        "xp": 0,
        "erros": erros_depois,
        "mensagem": f"Quase. Agora este exercício vale até {xp_potencial} XP.",
    }
