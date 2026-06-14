# CodeQuest

CodeQuest e um jogo educacional em Pygame para ensinar logica de programacao e Python por meio de aulas curtas, exercicios, XP, niveis e progressao por mundos.

## Status

Versao atual: beta 0.9.

O projeto esta centralizado no Pygame. O fluxo principal roda em janela local, com persistencia em SQLite e conteudo versionado em JSON.

Fluxo implementado:

- menu inicial com Novo jogo, Continuar, Creditos e Sair;
- criacao de personagem;
- hub principal apos existir usuario;
- tela de perfil com nome, idade, XP e nivel;
- tela Arquipelago de Bythos com Mundo 1;
- Aula 1 no formato texto -> 5 exercicios -> texto -> 5 exercicios -> texto -> 5 exercicios;
- persistencia local em SQLite;
- bloqueio de XP duplicado para exercicios ja concluidos;
- XP dinamico: comeca em 10, perde 2 por erro e respeita piso minimo de 2;
- creditos atualizados para a versao Pygame.

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

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Execute o jogo:

```bash
python app.py
```

## Dados e Persistencia

Os conteudos versionados ficam em:

- `data/aulas.json`
- `data/exercicios.json`

O progresso local usa SQLite em `data/codequest.db`. Esse arquivo e gerado automaticamente durante a execucao.

Tabelas principais:

- `usuarios`: guarda o save ativo.
- `exercicios_concluidos`: impede XP duplicado em exercicios ja finalizados.
- `exercicio_erros`: registra erros para calcular o XP potencial.

## Testes

Execute a suite com:

```bash
python -m pytest tests
```

Os testes cobrem persistencia, regras de XP, validacao de respostas, carregamento de conteudo, creditos e componentes basicos de UI em modo headless.

## Documentacao Tecnica

A documentacao detalhada da arquitetura esta em:

- [docs/arquitetura.md](docs/arquitetura.md)

Ela explica o fluxo interno, as camadas do projeto, a chamada entre modulos, as tabelas SQLite e os pontos de extensao.

## Roadmap

- expandir o mapa do Arquipelago de Bythos;
- adicionar novos mundos e modulos de Python;
- criar novas cutscenes entre mundos;
- melhorar acessibilidade de leitura e contraste;
- adicionar conquistas e itens cosmeticos;
- revisar trilha sonora e efeitos de interface;
- empacotar o jogo para execucao local mais simples.
