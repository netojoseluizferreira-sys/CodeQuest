# backend/exercicio.py
import json
import os

def carregar_aula(mundo, aula_id):
    diretorio_atual = os.path.dirname(__file__)
    caminho_aula = os.path.join(diretorio_atual, "..", "data", "aulas.json")
    
    try:
        with open(caminho_aula, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados[mundo][aula_id]
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em: {os.path.abspath(caminho_aula)}")
        return None

def carregar_exercicios(mundo):
    """Carrega exercícios de um mundo"""
    caminho_exercicios = os.path.join(diretorio_atual, "..", "data", "exercicios.json")
    
    try:
        with open(caminho_exercicios, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados.get(mundo, {})
    except FileNotFoundError:
        return {}