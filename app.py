from time import sleep

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
        print('EM BREVE...\n')
        sleep(1.0)
    elif menu == '2':
        print('EM BREVE...\n')
        sleep(1.0)
    elif menu == '3':
        print('EM BREVE...\n')
        sleep(1.0)
    else: 
        print('OPÇÃO INEXISTENTE\nTENTE NOVAMENTE...\n')
        sleep(1.0)