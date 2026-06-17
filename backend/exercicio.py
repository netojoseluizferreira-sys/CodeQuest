"""Leitura dos arquivos JSON de aulas e exercicios do CodeQuest."""

import json

from utils.asset_paths import content_path


AULAS_PATH = content_path("aulas.json")
EXERCICIOS_PATH = content_path("exercicios.json")


def carregar_aula(mundo, aula_id):
    """Retorna uma aula configurada para o mundo informado.

    Args:
        mundo: Identificador do mundo, como ``"mundo_1"``.
        aula_id: Identificador da aula dentro do mundo, como ``"aula_1"``.

    Returns:
        Dicionario da aula quando existe; ``None`` quando o arquivo ou as chaves
        nao forem encontrados.
    """
    try:
        with open(AULAS_PATH, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados[mundo][aula_id]
    except FileNotFoundError:
        print(f"ERRO: Arquivo nao encontrado em: {AULAS_PATH}")
        return None
    except KeyError:
        print(f"ERRO: Mundo '{mundo}' ou aula '{aula_id}' nao encontrado")
        return None


def carregar_exercicios(mundo):
    """Retorna os exercicios configurados para um mundo.

    Args:
        mundo: Identificador do mundo, como ``"mundo_1"``.

    Returns:
        Dicionario indexado por ID de exercicio. Retorna vazio quando o mundo
        nao existe, o arquivo nao existe ou o JSON esta invalido.
    """
    try:
        with open(EXERCICIOS_PATH, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados.get(mundo, {})
    except FileNotFoundError:
        print(f"ERRO: Arquivo nao encontrado em: {EXERCICIOS_PATH}")
        return {}
    except json.JSONDecodeError:
        print(f"ERRO: Arquivo JSON invalido em: {EXERCICIOS_PATH}")
        return {}
