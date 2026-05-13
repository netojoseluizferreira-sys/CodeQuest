from pick import pick
from time import sleep
from backend.usuario import criar_usuario, padronizar_idade
from backend.exercicios import carregar_aula
from utils.json_utils import salvar_usuario, carregar_usuario

aula = {}

# Menus apenas com os nomes das opções
menu_principal = [
    'FECHAR O APP',
    'MEU PERFIL',
    'MUNDOS',
    'RANKEAMENTO'
]

menu_mundo1 = [
    'VOLTAR PARA O MENU',
    'AULA 1: VARIÁVEIS E VALORES',
    'EXERCICIO 1',
    'EXERCICIO 2',
    'AULA 2: OPERADORES MATEMÁTICO',
    'EXERCICIO 3',
    'EXERCICIO 4',
    'AULA 3: ENTRADA/SAIDA',
    'EXERCICIO 5',
    'EXERCICIO 6'
]

usuario = carregar_usuario()
if usuario:
    tem_perfil = True
else:
    tem_perfil = False

while True:
    print('\n=== Bem vindo ao CodeQuest ===\n')
    
    # Usando pick - retorna a opção selecionada e o índice
    opcao, index = pick(menu_principal, "MENU PRINCIPAL", indicator='=>')

    match opcao:
        case 'FECHAR O APP':
            print('\nFechando APP...\n')
            sleep(1.0)
            break
            
        case 'MEU PERFIL':
            if not tem_perfil:
                print('\nEstou vendo que você ainda não tem um perfil, vamos criar ele primeiro\n')
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
                print('\n✅ PERFIL CRIADO COM SUCESSO!')
                sleep(1.0)
                tem_perfil = True
                
            if tem_perfil:
                print('\n📋 SEU PERFIL:')
                print('=' * 30)
                for chave, valor in usuario.items():
                    print(f"  {chave.upper()}: {valor}")
                print('=' * 30)
                input('\nPressione ENTER para continuar...')
                
        case 'MUNDOS':
            sleep(1.0)
            print('\n🌍 POR ENQUANTO O CODEQUEST SÓ TEM UM MUNDO, EM BREVE MAIS...\n')
            sleep(1.5)
            
            while True:
                print('\n🏰 MUNDO 1 DO CODEQUEST 🏰\n')
                
                # Usando pick para o menu do mundo 1
                opcao_mundo, index_mundo = pick(menu_mundo1, "CODEQUEST - MUNDO 1", indicator='=>')

                match opcao_mundo:
                    case 'VOLTAR PARA O MENU':
                        print('\n⬅️ Voltando ao menu principal...\n')
                        sleep(1.0)
                        break
                        
                    case 'AULA 1: VARIÁVEIS E VALORES':
                        aula = carregar_aula('mundo_1', 'aula_1')
                        if aula:
                            print(f'\n📚 {aula["titulo"]}\n')
                            print('=' * 50)
                            for linha in aula['conteudo']:
                                print(f'  ➤ {linha}')
                                # Ajustando o tempo de exibição
                                tempo = 1.2 if len(linha) < 40 else 2.2
                                sleep(tempo)
                            print('=' * 50)
                            input('\n📖 Pressione ENTER para continuar...')
                        else:
                            print('\n❌ Erro ao carregar a aula!\n')
                            sleep(1)
                            
                    case 'EXERCICIO 1' | 'EXERCICIO 2' | 'EXERCICIO 3' | 'EXERCICIO 4' | 'EXERCICIO 5' | 'EXERCICIO 6':
                        print(f"\n🚧 Opção '{opcao_mundo}' em desenvolvimento... Em breve! 🚧\n")
                        sleep(1.5)
                        
                    case 'AULA 2: OPERADORES MATEMÁTICO' | 'AULA 3: ENTRADA/SAIDA':
                        print(f"\n🚧 '{opcao_mundo}' em desenvolvimento... Em breve! 🚧\n")
                        sleep(1.5)
                        
                    case _:
                        print("\n❌ OPÇÃO INVÁLIDA, TENTE NOVAMENTE\n")
                        sleep(1.0)
                        
        case 'RANKEAMENTO':
            print('\n🏆 RANKEAMENTO - Em breve... 🏆\n')
            sleep(1.0)
            
        case _:
            print('\n❌ OPÇÃO INEXISTENTE\nTENTE NOVAMENTE...\n')
            sleep(1.0)