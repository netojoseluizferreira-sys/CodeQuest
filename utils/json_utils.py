import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CAMINHO = os.path.join(BASE_DIR, "data", "usuarios.json")

def salvar_usuario(usuario):
    with open(CAMINHO, "w", encoding="utf-8") as f:
        json.dump(usuario, f, indent=4, ensure_ascii=False)