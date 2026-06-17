"""Leitura e consulta dos metadados configuraveis dos mundos."""

import json

from utils.asset_paths import content_path


MUNDOS_CONFIG_PATH = content_path("mundos.json")

MUNDO_INICIAL = "mundo_1"
MUNDO_2_ID = "mundo_2"
AULA_PADRAO = "aula_1"


def carregar_mundos_config():
    """Carrega o arquivo central de metadados dos mundos."""
    with open(MUNDOS_CONFIG_PATH, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def listar_mundos():
    """Retorna todos os mundos configurados, ordenados para exibicao."""
    mundos = []
    for mundo_id, metadados in carregar_mundos_config().items():
        mundos.append({"id": mundo_id, **metadados})
    return sorted(mundos, key=lambda mundo: mundo.get("ordem", 999))


def obter_mundo(mundo_id):
    """Retorna os metadados de um mundo ou ``None`` quando ele nao existe."""
    metadados = carregar_mundos_config().get(mundo_id)
    return None if metadados is None else {"id": mundo_id, **metadados}


def mundo_implementado(mundo_id):
    """Indica se o mundo esta implementado na configuracao."""
    mundo = obter_mundo(mundo_id)
    return bool(mundo and mundo.get("implementado"))


def mundo_requisito(mundo_id):
    """Retorna o ID do mundo requisito, quando existir."""
    mundo = obter_mundo(mundo_id)
    return None if mundo is None else mundo.get("requer")


def aula_inicial(mundo_id):
    """Retorna a aula inicial configurada para o mundo."""
    mundo = obter_mundo(mundo_id)
    return AULA_PADRAO if mundo is None else mundo.get("aula_inicial", AULA_PADRAO)


def exercicios_obrigatorios(mundo_id):
    """Retorna a lista configurada de exercicios obrigatorios do mundo."""
    mundo = obter_mundo(mundo_id)
    if mundo is None:
        return []
    return [str(exercicio_id) for exercicio_id in mundo.get("exercicios_obrigatorios", [])]


def numero_mundo(mundo_id):
    """Retorna o rotulo numerico exibido do mundo."""
    mundo = obter_mundo(mundo_id)
    return mundo_id if mundo is None else mundo.get("numero", mundo_id)


def nome_mundo(mundo_id):
    """Retorna o rotulo principal do mundo para mensagens de interface."""
    return numero_mundo(mundo_id)


def titulo_botao_mundo(mundo):
    """Monta o texto de botao para um mundo configurado."""
    return f"{mundo['numero']} - {mundo['nome']}"


def proximo_mundo(mundo_id):
    """Retorna os metadados do proximo mundo na ordem configurada."""
    mundos = listar_mundos()
    for indice, mundo in enumerate(mundos):
        if mundo["id"] == mundo_id and indice + 1 < len(mundos):
            return mundos[indice + 1]
    return None
