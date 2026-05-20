import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def carregar_aula(mundo, aula_id):
    caminho_aula = os.path.join(BASE_DIR, "data", "aulas.json")
    
    try:
        with open(caminho_aula, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados[mundo][aula_id]
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em: {os.path.abspath(caminho_aula)}")
        return None
    except KeyError:
        print(f"ERRO: Mundo '{mundo}' ou aula '{aula_id}' não encontrado")
        return None

# ✅ ADICIONE ESTA FUNÇÃO ABAIXO:
def carregar_exercicios(mundo):
    """Carrega exercícios de um mundo específico"""
    caminho_exercicios = os.path.join(BASE_DIR, "data", "exercicios.json")
    
    try:
        with open(caminho_exercicios, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados.get(mundo, {})
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em: {os.path.abspath(caminho_exercicios)}")
        return {}
    except json.JSONDecodeError:
        print(f"ERRO: Arquivo JSON inválido em: {caminho_exercicios}")
        return {}