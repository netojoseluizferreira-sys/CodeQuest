import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CAMINHO = os.path.join(BASE_DIR, "data", "usuarios.json")

def salvar_usuario(usuario):
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(CAMINHO), exist_ok=True)
    
    with open(CAMINHO, "w", encoding="utf-8") as f:
        json.dump(usuario, f, indent=4, ensure_ascii=False)

def carregar_usuario():
    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None  # Retorna None em vez de {} para melhor controle