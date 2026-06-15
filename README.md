# CodeQuest

CodeQuest é um jogo educacional em Pygame para ensinar lógica de programação e Python por meio de aulas curtas, exercícios, XP, níveis e progressão por mundos.

## Status

Versão atual: beta 0.9.

O projeto está centralizado no Pygame. O fluxo principal roda em janela local, com persistência em SQLite e conteúdo versionado em JSON.

Fluxo implementado:

- menu inicial com Novo jogo, Continuar, Créditos e Sair;
- criação de personagem;
- hub principal após existir usuário;
- tela de perfil com nome, idade, XP e nível;
- tela Arquipélago de Bythos com Mundo 1;
- Aula 1 no formato texto -> 5 exercícios -> texto -> 5 exercícios -> texto -> 5 exercícios;
- persistência local em SQLite;
- bloqueio de XP duplicado para exercícios já concluídos;
- XP dinâmico: começa em 10, perde 2 por erro e respeita piso mínimo de 2;
- créditos atualizados para a versão Pygame.

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
|   |-- palette.py
|   |-- settings.py
|   `-- ui.py
|-- tests/
|   |-- conftest.py
|   |-- test_content_and_credits.py
|   |-- test_database.py
|   |-- test_learning_progress.py
|   |-- test_ui_components.py
|   `-- test_xp_system.py
|-- utils/
|   |-- database.py
|   |-- database_config.py
|   |-- database_connection.py
|   |-- exercise_progress_repository.py
|   |-- user_mapper.py
|   `-- user_repository.py
|-- requirements.txt
`-- README.md
```

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

## Dados e Persistência

Os conteúdos versionados ficam em:

- `data/aulas.json`
- `data/exercicios.json`

O progresso local usa SQLite em `data/codequest.db`. Esse arquivo é gerado automaticamente durante a execução.

Tabelas principais:

- `usuarios`: guarda o save ativo.
- `exercicios_concluidos`: impede XP duplicado em exercícios já finalizados.
- `exercicio_erros`: registra erros para calcular o XP potencial.

## Testes

Execute a suite com:

```bash
python -m pytest tests
```

Os testes cobrem persistência, regras de XP, validação de respostas, carregamento de conteúdo, créditos e componentes básicos de UI em modo headless.

## Documentação Técnica

A documentação detalhada da arquitetura está em:

- [docs/arquitetura.md](docs/arquitetura.md)

Ela explica o fluxo interno, as camadas do projeto, a chamada entre módulos, as tabelas SQLite e os pontos de extensão.

## Roadmap

- expandir o mapa do Arquipélago de Bythos;
- adicionar novos mundos e módulos de Python;
- criar novas cutscenes entre mundos;
- melhorar acessibilidade de leitura e contraste;
- adicionar conquistas e itens cosméticos;
- revisar trilha sonora e efeitos de interface;
- empacotar o jogo para execução local mais simples.
