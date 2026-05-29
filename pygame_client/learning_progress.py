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
    """Calcula o XP que ainda pode ser ganho em um exercicio.

    Recebe:
        erros: Quantidade de erros ja registrados no exercicio.

    Retorna:
        XP entre 2 e 10, reduzindo 2 pontos por erro.
    """
    return max(XP_BASE - (int(erros) * XP_PENALIDADE_ERRO), XP_MINIMO)


def frase_xp(xp):
    """Retorna uma frase curta para o resultado de XP.

    Recebe:
        xp: Quantidade de XP recebida ou potencial.

    Retorna:
        Mensagem amigavel para exibicao no Pygame.
    """
    frases = {
        10: "Perfeito! Voce garantiu 10 XP.",
        8: "Muito bom! Um tropeco pequeno, 8 XP.",
        6: "Boa recuperacao! Voce levou 6 XP.",
        4: "Persistencia conta: 4 XP.",
        2: "Conseguiu no limite minimo: 2 XP.",
        0: "Exercicio ja concluido antes. Sem XP extra.",
    }
    return frases.get(xp, f"Voce recebeu {xp} XP.")


def normalizar_resposta(resposta):
    """Normaliza texto livre para comparacao de respostas.

    Recebe:
        resposta: Texto digitado pelo jogador.

    Retorna:
        Texto em minusculas, sem acentos e com espacos normalizados.
    """
    texto = unicodedata.normalize("NFD", str(resposta).strip().lower())
    texto = "".join(char for char in texto if unicodedata.category(char) != "Mn")
    return " ".join(texto.replace(",", " ").replace("/", " ").replace("-", " ").split())


def resposta_esta_correta(exercicio, resposta):
    """Valida a resposta enviada para um exercicio.

    Recebe:
        exercicio: Dicionario do exercicio atual.
        resposta: Indice escolhido ou texto digitado pelo jogador.

    Retorna:
        True quando a resposta esta correta; caso contrario, False.
    """
    if exercicio["tipo"] == "multipla_escolha":
        return int(resposta) == int(exercicio["resposta"])

    resposta_normalizada = normalizar_resposta(resposta)
    respostas_aceitas = exercicio.get("respostas_aceitas", [])
    return resposta_normalizada in {
        normalizar_resposta(resposta_aceita) for resposta_aceita in respostas_aceitas
    }


def registrar_resposta(mundo, exercicio, resposta, usuario):
    """Registra uma tentativa de resposta e aplica XP quando cabivel.

    Recebe:
        mundo: Identificador do mundo do exercicio.
        exercicio: Dicionario do exercicio respondido.
        resposta: Indice ou texto informado pelo jogador.
        usuario: Usuario ativo que recebera XP quando aplicavel.

    Retorna:
        Dicionario com acerto, XP ganho, erros e mensagem.
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
        "mensagem": f"Quase. Agora este exercicio vale ate {xp_potencial} XP.",
    }
