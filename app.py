from time import sleep
from backend.usuario import criar_usuario, padronizar_idade

usuario = {}
tem_perfil =  False

while True:
    menu = input('Bem vindo ao CodeQuest\nOPÇÕES DO MENU:' + '\n' + 
'''[0] - FECHAR O APP
[1] - MEU PERFIL
[2] - MUNDO 1
[3] - RANKEAMENTO

Digite a ação que deseja realizar: ''')
    if menu == '0':
        print('Fechando APP...\n')
        sleep(1.0)
        break
    elif menu == '1':
        if not tem_perfil:
            print('Estou vendo que você ainda não tem um perfil, vamos criar ele primeiro')
            sleep(1.0)
            usuario = criar_usuario(input("Nome: "), padronizar_idade('Digite sua idade: '))
            print('PERFIL CRIADO COM SUCESSO')
            sleep(1.0)
            perfil = True
        print('\nSeu PERFIL:')
        for chave, valor in usuario.items():
            print(f"{chave}: {valor}")
        print('\n')
        sleep(1)
    elif menu == '2':
        print('EM BREVE...\n')
        sleep(1.0)
    elif menu == '3':
        print('EM BREVE...\n')
        sleep(1.0)
    else: 
        print('OPÇÃO INEXISTENTE\nTENTE NOVAMENTE...\n')
        sleep(1.0)