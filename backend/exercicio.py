# backend/exercicio.py
import json
import os
import sys

def get_base_dir():
    """Encontra o diretório raiz do projeto"""
    # Tenta encontrar onde está app_streamlit.py
    if hasattr(sys, '_getframe'):
        current_file = os.path.abspath(__file__)
        # Sobe duas pastas (backend -> raiz)
        return os.path.dirname(os.path.dirname(current_file))
    
    # Fallback
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = get_base_dir()

def carregar_aula(mundo, aula_id):
    caminho_aula = os.path.join(BASE_DIR, "data", "aulas.json")
    
    print(f"Procurando arquivo em: {caminho_aula}")  # Debug
    
    try:
        with open(caminho_aula, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados[mundo][aula_id]
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em: {os.path.abspath(caminho_aula)}")
        print(f"BASE_DIR = {BASE_DIR}")
        return None