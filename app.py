from time import sleep
from backend.usuario import criar_usuario, padronizar_idade, menus
from utils.json_utils import salvar_usuario, carregar_usuario

menu_principal = {
    '0':'FECHAR O APP',
    '1': 'MEU PERFIL',
    '2': 'MUNDOS',
    '3': 'RANKEAMENTO'
}

menu_mundo1 = {
    '1':'AULA 1: VARIÁVEIS E VALORES',
    '2':'EXERCICIO 1',
    '3':'EXERCICIO 2',
    '4':'AULA 2: OPERADORES MATEMÁTICO',
    '5':'EXERCICIO 3',
    '6':'EXERCICIO 4',
    '7':'AULA 3: ENTRADA/SAIDA',
    '8':'EXERCICIO 5',
    '9':'EXERCICIO 6',
    '0':'VOLTAR PARA O MENU'
}


usuario = carregar_usuario()
if usuario:
    tem_perfil =  True
else:
    tem_perfil = False

while True:
    print('Bem vindo ao CodeQuest')
    menu = menus('MENU PRINCIPAL', menu_principal)
    
    if menu == '0':
        print('Fechando APP...\n')
        sleep(1.0)
        break
    elif menu == '1':
        if not tem_perfil:
            print('Estou vendo que você ainda não tem um perfil, vamos criar ele primeiro')
            sleep(1.0)

            nome = input("Digite seu nome: ").title()

            while True:
                idade_input = input("Digite sua idade: ")
                idade = padronizar_idade(idade_input)

                if idade is not None:
                    break
                else:
                    print("ERRO, tente novamente")

            usuario = criar_usuario(nome, idade)
            salvar_usuario(usuario)
            print('PERFIL CRIADO COM SUCESSO')
            sleep(1.0)
            tem_perfil = True
        if tem_perfil:
            print('\nSeu PERFIL:')
            for chave, valor in usuario.items():
                print(f"{chave}: {valor}")
            print('\n')
            sleep(1)
    elif menu == '2':
        sleep(1.0)
        print('\nPOR ENQUANTO O CODEQUEST SÓ TEM UM MUNDO, EM BREVE MAIS...\n')
        sleep(1.5)
        while True:
            print('ESSE É O MUNDO 1 DO CODEQUEST')
            percurso = menus('CODEQUEST - MUNDO 1',menu_mundo1)

            sleep(1.0)
            if percurso == '0':
                print('ABRINDO MENU...')
                sleep(1.0)
                break
            elif percurso == '1':
                print("EM BREVE...")
            elif percurso == '2':
                print("EM BREVE...")
            elif percurso == '3':
                print("EM BREVE...")
            elif percurso == '4':
                print("EM BREVE...")
            elif percurso == '5':
                print("EM BREVE...")
            elif percurso == '6':
                print("EM BREVE...")
            elif percurso == '7':
                print("EM BREVE...")
            elif percurso == '8':
                print("EM BREVE...")
            else:
                print("OPÇÃO INVÁLIDA, TENTE NOVAMENTE")
            sleep(1.0)
            
    elif menu == '3':
        print('EM BREVE...\n')
        sleep(1.0)
    else: 
        print('OPÇÃO INEXISTENTE\nTENTE NOVAMENTE...\n')
        sleep(1.0)