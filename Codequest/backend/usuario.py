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
    
def menus(texto, menu):
    print(f'----{texto}----')
    for chave, valor in menu.items():
        print(f'[{chave}] - {valor}')

    return input('Digite a ação que deseja realizar: ')
