# Arquitetura Interna do CodeQuest

Este documento descreve como o CodeQuest está organizado na versão Pygame, quais módulos conversam entre si e onde mexer para evoluir o jogo.

## Visão Geral

O ponto de entrada é `app.py`. Ele chama `pygame_client.menu_app.main()`, que inicializa o Pygame, cria a classe `CodeQuestPygameMenu` e entra no loop principal do jogo.

```mermaid
flowchart TD
    A["app.py"] --> B["pygame_client.menu_app.main"]
    B --> C["CodeQuestPygameMenu.run"]
    C --> D["Eventos do Pygame"]
    C --> E["Renderização da tela atual"]
    D --> F["Ações dos botões e formulários"]
    F --> G["utils/database.py"]
    F --> H["pygame_client/content.py"]
    F --> I["pygame_client/learning_progress.py"]
```

## Camadas do Projeto

### `pygame_client/`

Contém a interface jogável:

- `menu_app.py`: orquestra telas, eventos, estado de navegação, aulas, exercícios, perfil e créditos.
- `ui.py`: componentes reutilizáveis de interface, como `Button`, quebra de texto e texto centralizado.
- `content.py`: adapta os JSONs de aula e exercícios para o Pygame, corrigindo textos quando necessário.
- `learning_progress.py`: valida respostas, calcula XP potencial e registra conclusão de exercícios.
- `audio.py`: inicializa trilha e efeitos sonoros gerados em tempo de execução.
- `credits.py`: define o conteúdo estruturado da tela de créditos.
- `palette.py` e `settings.py`: concentram cores, tamanhos, FPS e caminhos visuais.

### `backend/`

Contém regras de domínio independentes da tela:

- `usuario.py`: dataclass `Usuario`, criação, carregamento a partir de dicionário e soma de XP.
- `xp_system.py`: regras de nível, XP para próximo nível e persistência após ganhar XP.
- `exercicio.py`: leitura bruta dos arquivos `data/aulas.json` e `data/exercicios.json`.

### `utils/`

Contém persistência SQLite:

- `database.py`: fachada pública usada pelo resto do projeto.
- `database_config.py`: caminhos, constantes e ID do usuário ativo.
- `database_connection.py`: conexão e criação de tabelas.
- `user_repository.py`: CRUD do usuário ativo e migração do JSON legado.
- `user_mapper.py`: conversão entre linhas SQLite, dicionários e `Usuario`.
- `exercise_progress_repository.py`: erros por exercício e bloqueio de XP duplicado.

### `data/`

Guarda conteúdo e assets versionados:

- `aulas.json`: textos e trilhas pedagógicas.
- `exercicios.json`: perguntas, alternativas, respostas e respostas aceitas.
- fontes, imagens, cutscenes e frames animados.

O save local fica em `data/codequest.db`, gerado em execução e ignorado pelo Git.

## Fluxo de Telas

O atributo `screen_name` em `CodeQuestPygameMenu` decide qual tela é renderizada.

Fluxo principal:

1. `start`: menu inicial com novo jogo, continuar, créditos e sair.
2. `create`: criação do personagem quando um novo save é necessário.
3. `hub`: menu principal após existir usuário.
4. `worlds`: seleção do Arquipélago de Bythos.
5. `learning`: aula e exercícios em sequência.
6. `profile`: visualização de nome, idade, XP e nível.
7. `credits`: créditos do projeto.
8. `complete`: encerramento temporário do conteúdo disponível.

## Novo Jogo e Continuar

`_novo_jogo()` limpa o banco com `resetar_banco_de_dados()` e leva para a tela de criação de personagem.

`_continuar()` tenta carregar o usuário ativo com `carregar_usuario()`. Se houver usuário, segue para o `hub`; se não houver, exibe uma mensagem pedindo criação de personagem.

`_criar_usuario()` valida nome e idade, chama `criar_usuario()` e avança para o `hub`.

## Fluxo de Aula e Exercícios

O Mundo 1 começa em `_iniciar_mundo_1()`. A função carrega a aula com `carregar_aula_pygame("mundo_1", "aula_1")` e os exercícios com `carregar_exercicios_pygame("mundo_1")`.

A trilha pedagógica é lida em blocos. Cada bloco pode ser:

- `aula`: renderiza um trecho de explicação.
- `exercicios`: mostra um exercício por vez.

O fluxo planejado é:

```text
texto da aula -> 5 exercícios -> texto da aula -> 5 exercícios -> texto da aula -> 5 exercícios
```

Quando o jogador responde, `_responder_exercicio()` chama `registrar_resposta()`.

## Regras de XP

Cada exercício começa valendo 10 XP. A cada erro, o XP potencial cai 2 pontos:

```text
0 erros: 10 XP
1 erro: 8 XP
2 erros: 6 XP
3 erros: 4 XP
4 ou mais erros: 2 XP
```

Depois que um exercício foi concluído, ele continua podendo ser respondido, mas não concede XP de novo. Esse bloqueio vem da tabela `exercicios_concluidos`.

## SQLite

As tabelas são criadas por `inicializar_banco()`:

- `usuarios`: save do jogador ativo.
- `exercicios_concluidos`: exercícios que já deram XP.
- `exercicio_erros`: contador de erros por usuário, mundo e exercício.

O repositório usa `INSERT ... ON CONFLICT` para atualizar o usuário ativo sem duplicar registros.

## Pontos de Extensão

Para adicionar uma nova aula:

1. Inclua os textos em `data/aulas.json`.
2. Inclua os exercícios em `data/exercicios.json`.
3. Atualize o fluxo em `menu_app.py` para iniciar o novo mundo ou aula.
4. Adicione testes cobrindo carregamento de conteúdo e regras novas.

Para alterar regras de XP, mexa em `pygame_client/learning_progress.py` e, se necessário, em `backend/xp_system.py`.

Para mudar o visual, prefira `pygame_client/palette.py`, `pygame_client/settings.py` e componentes de `pygame_client/ui.py`.
