# CodeQuest

CodeQuest e um jogo educacional em Pygame para ensinar logica de programacao e Python por meio de aulas curtas, exercicios, XP, niveis e progressao por mundos.

## Status Atual

O projeto esta em transicao para uma experiencia centralizada em Pygame. A interface web/Streamlit saiu do escopo versionado, e o fluxo principal agora acontece dentro da janela Pygame.

Fluxo implementado:

- tela inicial com Novo jogo, Continuar, Creditos e Sair;
- criacao de personagem quando nao houver usuario salvo;
- menu principal apos login;
- tela de perfil com XP, nivel e dados do usuario;
- tela Arquipelago de Bythos com Mundo 1;
- Aula 1 no formato texto -> 5 exercicios -> texto -> 5 exercicios -> texto -> 5 exercicios;
- persistencia local em SQLite;
- bloqueio de XP duplicado para exercicios ja concluidos;
- XP dinamico: comeca em 10, perde 2 por erro e respeita piso minimo de 2.

## Estrutura

```text
CodeQuest/
├── backend/
│   ├── exercicio.py
│   ├── usuario.py
│   └── xp_system.py
├── data/
│   ├── aulas.json
│   └── exercicios.json
├── pygame_client/
│   ├── audio.py
│   ├── content.py
│   ├── credits.py
│   ├── learning_progress.py
│   ├── menu_app.py
│   ├── palette.py
│   ├── settings.py
│   └── ui.py
├── utils/
│   ├── database.py
│   ├── database_config.py
│   ├── database_connection.py
│   ├── exercise_progress_repository.py
│   ├── user_mapper.py
│   └── user_repository.py
├── requirements.txt
└── README.md
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

O progresso local usa SQLite em `data/codequest.db`.

## Testes

Se `pytest` estiver instalado, rode:

```bash
python -m pytest tests
```

A pasta `tests/` e local e nao faz parte dos commits do repositorio.

## Roadmap

- expandir o mapa do Arquipelago de Bythos;
- adicionar novos mundos e modulos de Python;
- criar telas de cutscene entre mundos;
- melhorar acessibilidade de leitura e contraste;
- adicionar conquistas e itens cosmeticos;
- revisar a trilha sonora e efeitos de interface;
- empacotar o jogo para execucao local mais simples.
