"""Leitura dos arquivos JSON de aulas e exercicios do CodeQuest."""

import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def carregar_aula(mundo, aula_id):
    """Lê e retorna os dados de uma aula do arquivo data/aulas.json.

    Recebe:
        mundo (str): Chave de primeiro nível no JSON, ex.: "mundo_1".
        aula_id (str): Chave de segundo nível dentro do mundo, ex.: "aula_1".

    Retorna:
        dict | None: Dicionário com os dados da aula (título, trilha, conteúdo)
        ou None quando o arquivo não existir ou as chaves não forem encontradas.
        Imprime uma mensagem de erro descritiva no stdout em caso de falha.
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
    """Lê e retorna os exercícios de um mundo do arquivo data/exercicios.json.

    Recebe:
        mundo (str): Chave de primeiro nível no JSON, ex.: "mundo_1".

    Retorna:
        dict: Dicionário de exercícios do mundo indexado por ID string,
        ou dicionário vazio quando o mundo não existir, o arquivo não for
        encontrado ou o JSON estiver malformado. Imprime mensagem de erro no stdout.
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
