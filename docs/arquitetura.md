# Arquitetura Interna do CodeQuest

Este documento descreve a organização interna do CodeQuest na versão 1.5, com foco no fluxo Pygame, persistência SQLite e separação do menu em módulos menores.

## Visão Geral

`app.py` é o ponto de entrada. Ele chama `pygame_client.menu_app.main()`, que cria `CodeQuestPygameMenu` e inicia o loop principal. A classe principal ficou responsável por inicializar Pygame, fontes, imagens, áudio e estado compartilhado; comportamento de tela foi separado em mixins.

```mermaid
flowchart TD
    A["app.py"] --> B["pygame_client.menu_app.main"]
    B --> C["CodeQuestPygameMenu"]
    C --> D["menu_events.EventMixin"]
    C --> E["menu_buttons.ButtonMixin"]
    C --> F["menu_rendering.RenderMixin"]
    C --> G["menu_learning_rendering.LearningRenderMixin"]
    C --> H["menu_navigation.NavigationMixin"]
    H --> I["utils/database.py"]
    H --> J["pygame_client/content.py"]
    H --> K["pygame_client/learning_progress.py"]
    K --> L["backend/achievements.py"]
    L --> M["utils/achievement_repository.py"]
```

## Camadas

### `pygame_client/`

- `menu_app.py`: inicializa Pygame, carrega assets, cria fontes, mantém estado compartilhado e executa o loop principal.
- `menu_buttons.py`: monta botões por tela.
- `menu_events.py`: processa teclado, mouse, campos de texto e links externos.
- `menu_navigation.py`: controla transições de tela, criação de usuário, início de mundos, respostas e conclusão de aulas.
- `menu_rendering.py`: desenha telas gerais, como início, hub, mundos, perfil, cutscene e créditos.
- `menu_learning_rendering.py`: desenha aulas, exercícios e tela de conclusão.
- `menu_config.py`: concentra constantes do menu, lista de mundos, cores locais e textos da cutscene.
- `audio.py`: controla trilhas MP3 por contexto e efeitos de interface.
- `content.py`: lê e normaliza conteúdo pedagógico vindo dos JSONs.
- `learning_progress.py`: valida respostas, calcula XP potencial e registra progresso.
- `ui.py`: contém `Button`, quebra de texto e helpers de desenho.
- `palette.py` e `settings.py`: centralizam cores, janela, FPS e título.

### `backend/`

- `usuario.py`: dataclass `Usuario` e operações de domínio do usuário.
- `achievements.py`: regras de desbloqueio de conquistas, normalização do nome secreto e cálculo de XP máximo/mínimo disponível.
- `xp_system.py`: cálculo de nível, XP para próximo nível e soma de XP.
- `exercicio.py`: leitura bruta dos arquivos de aula e exercício.
- `worlds.py`: leitura de `data/mundos.json` e helpers para metadados, ordem, requisito, aula inicial e exercícios obrigatórios.

### `utils/`

- `database.py`: fachada pública de persistência.
- `database_connection.py`: conexão SQLite e criação de tabelas.
- `database_config.py`: caminhos e constantes do banco.
- `user_repository.py`: CRUD do usuário ativo e migração de JSON legado.
- `user_mapper.py`: conversão entre SQLite, dicionários e dataclass `Usuario`.
- `exercise_progress_repository.py`: progresso de exercícios, erros e bloqueio de recompensa duplicada.
- `world_progress_repository.py`: progresso por mundo, marcação de conclusão e consulta usada para desbloquear mundos.
- `achievement_repository.py`: leitura de `data/conquistas.json`, desbloqueio idempotente e listagem de conquistas com estado para o perfil.

### `data/`

Contém conteúdo e assets versionados:

- `aulas.json`, `exercicios.json`, `mundos.json` e `conquistas.json`.
- imagens de conquistas em `data/achievements/`.
- fontes: PressStart2P, RammettoOne e WendyOne.
- frames de fundo, imagens de cutscene, fundos de mundo e músicas.

O save local `data/codequest.db` é gerado em execução e ignorado pelo Git.

## Fluxo de Telas

O atributo `screen_name` define a tela ativa:

- `start`: menu inicial.
- `create`: criação de personagem.
- `hub`: menu de jornada.
- `cutscene`: narrativa inicial.
- `worlds`: Arquipélago de Bythos.
- `lesson`: aula ou exercício.
- `profile`: perfil do jogador.
- `credits`: créditos.
- `complete`: conclusão do mundo ativo.

## Fluxo Pedagógico

Os metadados de progressão ficam centralizados em `data/mundos.json`. Cada mundo define ID, rótulo, nome exibido, requisito de desbloqueio, aula inicial, implementação, exercícios obrigatórios e assets opcionais de fundo.

Cada aula em `data/aulas.json` possui uma `trilha`, composta por segmentos:

- `aula`: texto explicativo, com suporte opcional a link externo.
- `exercicios`: lista de IDs carregados de `data/exercicios.json`.

O Mundo 1 segue o formato:

```text
texto -> 5 exercícios -> texto -> 5 exercícios -> texto -> 5 exercícios
```

O Mundo 2 usa o mesmo padrão visual e começa com blocos menores de texto e prática.

## Progresso e Bloqueios

Quando um exercício é concluído, o registro é salvo em `exercicios_concluidos`. Em seguida, `verificar_e_marcar_conclusao_mundo()` confere se todos os exercícios obrigatórios daquele mundo foram concluídos e, quando for o caso, grava a conclusão em `mundos_concluidos`.

Ao reiniciar o app, `NavigationMixin._pular_exercicios_concluidos()` ignora exercícios já feitos, mas preserva os textos de aula para revisão.

O desbloqueio de novos mundos consulta a camada de progresso por mundo e a configuração central em `data/mundos.json`. O Mundo 2, por exemplo, abre quando o requisito configurado para ele está concluído, sem checagens hardcoded de IDs de exercícios na navegação.

A tabela `mundos_concluidos` usa a chave `(usuario_id, mundo_id)` para impedir duplicidade e armazena `concluido` e `data_conclusao`. Para compatibilidade com saves antigos, a consulta de mundo concluído consegue reconhecer mundos que já tenham todos os exercícios salvos em `exercicios_concluidos` e atualiza a nova tabela.

## Regras de XP

Cada exercício começa valendo 10 XP. A cada erro, o ganho potencial cai 2 pontos, até o mínimo de 2 XP.

```text
0 erros: 10 XP
1 erro: 8 XP
2 erros: 6 XP
3 erros: 4 XP
4 ou mais erros: 2 XP
```

Exercícios já concluídos não concedem XP novamente.

O nível do jogador vai de 1 a 5, alinhado ao teto atual de 1200 XP:
nível 1 até 100 XP, nível 2 até 200 XP, nível 3 até 300 XP, nível 4 até
600 XP e nível 5 até 1200 XP.

## Conquistas

As conquistas são configuradas em `data/conquistas.json`. Cada entrada define `id`, `nome`, `dica`, descrição, imagem desbloqueada, imagem bloqueada e a condição conceitual. O Pygame não conhece as regras; ele chama `listar_conquistas_com_estado()` e apenas renderiza slots com a imagem bloqueada ou real.

A persistência fica em `usuario_conquistas`, com chave primária `(usuario_id, conquista_id)` para impedir duplicidade. `desbloquear_conquista()` usa escrita idempotente e retorna sucesso apenas quando a conquista foi gravada pela primeira vez, o que alimenta a notificação temporária.

Regras iniciais:

- `melhor_professor_ufal`: avaliada na criação do usuário. O nome é normalizado com `strip()`, `lower()`, remoção de acentos e colapso de espaços. As variações aceitas incluem `barbosa`, `alexandre`, `alexandre barbosa`, `prof barbosa`, `professor barbosa`, `prof alexandre` e `professor alexandre`.
- `fenomeno`: avaliada após ganho de XP; compara o XP do usuário com a soma do XP máximo dos exercícios obrigatórios dos mundos implementados.
- `quase_hexa`: avaliada após conclusão de exercício; exige todos os exercícios obrigatórios dos mundos implementados concluídos com o XP mínimo.

No perfil, `menu_rendering.py` desenha todos os slots em uma moldura verde. Conquistas bloqueadas mostram `locked_question.png` e tooltip com `???` mais a dica; desbloqueadas mostram o nome e a mensagem `Conquista desbloqueada.`.

## Áudio

`AudioController` mapeia contexto de tela para música:

- `start`: Tela Inicial.
- `hub`: Menu de Jornada.
- `cutscene`: Cutscene.
- `worlds`: Arquipélago.
- `lesson`: Aula.
- `exercise`: Exercícios.
- `profile`: Perfil.
- `credits`: Créditos.

Se uma faixa MP3 não puder ser carregada, o controlador usa fallback sintético simples.

## Pontos de Extensão

Para adicionar um novo mundo:

1. Adicione textos em `data/aulas.json`.
2. Adicione exercícios em `data/exercicios.json`.
3. Inclua os metadados do mundo em `data/mundos.json`.
4. Defina `requer`, `implementado`, `aula_inicial`, `background` e `exercicios_obrigatorios` conforme necessário.
5. Adicione testes de carregamento de conteúdo e fluxo.

Para mudar visual:

1. Prefira `palette.py`, `settings.py`, `ui.py` e os módulos de renderização.
2. Mantenha fontes padronizadas: PressStart2P para títulos, RammettoOne para subtítulos e WendyOne para corpo.

Para mudar persistência:

1. Ajuste os repositórios em `utils/`.
2. Exponha a função pela fachada `utils/database.py` quando outras camadas precisarem usar.
3. Mantenha regras de progresso fora do Pygame; o cliente deve consultar funções de domínio/repositório.

Para adicionar uma conquista:

1. Adicione a entrada em `data/conquistas.json`.
2. Coloque os PNGs em `data/achievements/`.
3. Implemente a regra em `backend/achievements.py`.
4. Use `utils/achievement_repository.py` para persistir o desbloqueio.
5. Adicione testes em `tests/test_achievements.py`.
