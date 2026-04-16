def criar_usuario(nome, idade):
    return {
        "nome": nome,
        "idade": idade,
        "xp": 0,
        "nivel": 0
    }

def padronizar_idade(texto):
    try:
        return int(texto.lower().replace(' anos', '').strip())
    except ValueError:
        return None
    


