import json
import os

def carregar_aula(mundo, aula_id, conteudo):
    diretorio_atual = os.path.dirname(__file__)
   
    caminho_aula = os.path.join(diretorio_atual, "..", "data", "aulas.json")
    
    try:
        with open(caminho_aula, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            return dados[mundo][aula_id][conteudo]
    except FileNotFoundError:
        print(f"ERRO: O arquivo não foi encontrado em: {os.path.abspath(caminho_aula)}")
        return None