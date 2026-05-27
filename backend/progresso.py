# backend/progresso.py
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESSO_FILE = os.path.join(BASE_DIR, "data", "progresso.json")

def salvar_progresso(usuario_nome, modulo, exercicio_id):
    """Salva qual exercício o usuário concluiu"""
    progresso = carregar_progresso()
    
    if usuario_nome not in progresso:
        progresso[usuario_nome] = {
            "modulo_atual": modulo,
            "concluidos": []
        }
    
    if exercicio_id not in progresso[usuario_nome]["concluidos"]:
        progresso[usuario_nome]["concluidos"].append(exercicio_id)
    
    # Atualiza módulo atual se for maior
    if modulo > progresso[usuario_nome]["modulo_atual"]:
        progresso[usuario_nome]["modulo_atual"] = modulo
    
    os.makedirs(os.path.dirname(PROGRESSO_FILE), exist_ok=True)
    with open(PROGRESSO_FILE, "w", encoding="utf-8") as f:
        json.dump(progresso, f, indent=4, ensure_ascii=False)

def carregar_progresso(usuario_nome=None):
    """Carrega progresso de um usuário ou de todos"""
    try:
        with open(PROGRESSO_FILE, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if usuario_nome:
                return dados.get(usuario_nome, {})
            return dados
    except FileNotFoundError:
        return {} if usuario_nome is None else {}
