import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar_aula(mundo, aula_id):
    """Carrega os dados de uma aula cadastrada no JSON de aulas.

    Recebe:
        mundo: Identificador do mundo onde a aula esta cadastrada.
        aula_id: Identificador da aula dentro do mundo.

    Retorna:
        Dicionario com os dados da aula ou None quando nao existir.
    """
    caminho_aula = os.path.join(BASE_DIR, "data", "aulas.json")

    try:
        with open(caminho_aula, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados[mundo][aula_id]
    except FileNotFoundError:
        print(f"ERRO: Arquivo nao encontrado em: {os.path.abspath(caminho_aula)}")
        return None
    except KeyError:
        print(f"ERRO: Mundo '{mundo}' ou aula '{aula_id}' nao encontrado")
        return None


def carregar_exercicios(mundo):
    """Carrega os exercicios cadastrados para um mundo.

    Recebe:
        mundo: Identificador do mundo desejado.

    Retorna:
        Dicionario de exercicios do mundo ou um dicionario vazio em caso de erro.
    """
    caminho_exercicios = os.path.join(BASE_DIR, "data", "exercicios.json")

    try:
        with open(caminho_exercicios, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados.get(mundo, {})
    except FileNotFoundError:
        print(f"ERRO: Arquivo nao encontrado em: {os.path.abspath(caminho_exercicios)}")
        return {}
    except json.JSONDecodeError:
        print(f"ERRO: Arquivo JSON invalido em: {caminho_exercicios}")
        return {}
