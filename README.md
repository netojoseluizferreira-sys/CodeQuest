# CodeQuest

**Versão 1.5**

CodeQuest é um jogo educacional em Pygame para ensinar lógica de programação e Python por meio de aulas curtas, exercícios, XP, níveis, persistência local e progressão por mundos no Arquipélago de Bythos.

## Status

O projeto está em versão jogável local, centralizado no Pygame. A antiga abordagem com Streamlit/API foi removida do fluxo principal; o jogo agora roda por `app.py`, usa SQLite para salvar progresso e mantém aulas/exercícios em JSON versionado.

### Já Implementado

- Menu inicial com Novo jogo, Continuar, Créditos e Sair.
- Criação de personagem e hub de jornada.
- Tela de perfil com nome, idade, XP, nível e progresso.
- Cutscene inicial com imagens, texto e avanço manual.
- Arquipélago de Bythos com seleção de mundos.
- Mundo 1 completo: 3 textos de aula e 15 exercícios em blocos.
- Mundo 2 inicial: textos e exercícios no mesmo padrão visual do Mundo 1.
- Bloqueio do Mundo 2 até concluir os 15 exercícios do Mundo 1.
- Exercícios concluídos são pulados ao reiniciar o app, preservando os textos de aula.
- XP dinâmico: começa em 10, perde 2 por erro e respeita mínimo de 2 XP.
- Bloqueio de XP duplicado por exercício concluído.
- Trilhas sonoras por contexto: menu, hub, cutscene, mundos, aula, exercícios, perfil e créditos.
- Testes unitários em `tests/` cobrindo banco, XP, conteúdo, áudio, UI e fluxo de menu.
- Documentação técnica em `docs/`.

### Em Implementação

- Expansão dos mundos 3 a 9.
- Mais exercícios e textos de revisão.
- Conquistas no perfil.
- Melhorias de acessibilidade visual e empacotamento para execução local mais simples.

## Como Rodar

Crie e ative um ambiente virtual:

```bash
python -m venv venv
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o jogo:

```bash
python app.py
```

## Estrutura

```text
CodeQuest/
|-- app.py
|-- backend/
|   |-- exercicio.py
|   |-- usuario.py
|   `-- xp_system.py
|-- data/
|   |-- aulas.json
|   |-- exercicios.json
|   |-- cutscenes/
|   |-- music/
|   |-- hub_frames/
|   |-- mundos_frames/
|   |-- perfil_frames/
|   |-- creditos_frames/
|   `-- video_frames/
|-- docs/
|   `-- arquitetura.md
|-- pygame_client/
|   |-- audio.py
|   |-- content.py
|   |-- credits.py
|   |-- learning_progress.py
|   |-- menu_app.py
|   |-- menu_buttons.py
|   |-- menu_config.py
|   |-- menu_events.py
|   |-- menu_learning_rendering.py
|   |-- menu_navigation.py
|   |-- menu_rendering.py
|   |-- palette.py
|   |-- settings.py
|   `-- ui.py
|-- tests/
|-- utils/
|-- requirements.txt
`-- README.md
```

## Dados e Persistência

Conteúdo versionado:

- `data/aulas.json`
- `data/exercicios.json`

Progresso local:

- `data/codequest.db`, gerado automaticamente e ignorado pelo Git.

Tabelas principais:

- `usuarios`: save ativo do jogador.
- `exercicios_concluidos`: impede XP duplicado e permite pular exercícios já feitos.
- `exercicio_erros`: registra erros por usuário, mundo e exercício para calcular XP potencial.

## Testes

```bash
python -m pytest tests
```

## Documentação Técnica

Veja [docs/arquitetura.md](docs/arquitetura.md) para detalhes sobre módulos, fluxo de telas, persistência, regras de XP e pontos de extensão.

## Roadmap

- Implementar Mundo 3: Operadores.
- Implementar mundos 4 a 9.
- Criar tela de conquistas funcional.
- Adicionar mais feedback visual de progresso.
- Revisar licenciamento/autoria de assets externos.
- Empacotar versão executável para distribuição local.
