def criar_usuario(nome, idade):
    return {
        "nome": nome,
        "idade": idade,
        "xp": 0,
        "nivel": 0
    }

def padronizar_idade(texto):
    while True:
        try:
            idade = int(input(texto).lower().replace(' anos', '').strip())
            break
        except ValueError:
            print('ERRO, tente novamente, Somente números')
    return idade