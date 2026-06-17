# CodeQuest

**Versao 2.0**

CodeQuest e um jogo educacional em Pygame para ensinar logica de programacao e Python por meio de aulas curtas, exercicios, XP, niveis, conquistas, persistencia local e progressao por mundos no Arquipelago de Bythos.

## Status

O projeto esta em versao jogavel local. O fluxo principal roda por `app.py`, usa SQLite para salvar progresso e mantem conteudo pedagogico em JSON versionado. A abordagem antiga com Streamlit/API nao faz parte do fluxo atual.

## Ja Implementado

- Menu inicial com Novo jogo, Continuar, Creditos e Sair.
- Criacao de personagem, hub de jornada, perfil e selecao de mundos.
- Cutscene inicial, telas de aula, exercicios e encerramento do Mundo 9.
- Mundos 1 a 9 implementados, incluindo recursividade e cutscene final.
- Bloqueio/desbloqueio de mundos por metadados em JSON.
- Exercicios concluidos sao pulados ao reiniciar o app, preservando textos de aula para revisao.
- XP dinamico: 10 XP por acerto perfeito, perda de 2 XP por erro e piso de 2 XP.
- Niveis de 1 a 5 alinhados ao teto atual de 1200 XP.
- Bloqueio de XP duplicado por exercicio concluido.
- Conquistas persistidas em SQLite e configuradas por `data/content/conquistas.json`.
- Trilhas sonoras por contexto e cutscene final com audio proprio.
- Testes unitarios em `tests/` cobrindo banco, XP, conteudo, conquistas, audio, UI e fluxo de menu.
- Documentacao tecnica em `docs/`.

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

## Estrutura

```text
CodeQuest/
|-- app.py
|-- backend/
|   |-- achievements.py
|   |-- exercicio.py
|   |-- usuario.py
|   |-- worlds.py
|   `-- xp_system.py
|-- data/
|   |-- audio/
|   |   `-- music/
|   |-- content/
|   |   |-- aulas.json
|   |   |-- conquistas.json
|   |   |-- exercicios.json
|   |   `-- mundos.json
|   |-- fonts/
|   |-- images/
|   |   |-- achievements/
|   |   |-- backgrounds/
|   |   `-- cutscenes/
|   `-- video/
|       |-- credits/
|       |-- hub/
|       |-- mundo_9_cutscene/
|       |-- profile/
|       |-- start/
|       `-- worlds/
|-- docs/
|   |-- arquitetura.md
|   `-- testes_pytest.md
|-- pygame_client/
|-- tests/
|-- utils/
|   |-- asset_paths.py
|   `-- ...
|-- requirements.txt
`-- README.md
```

## Dados e Persistencia

Conteudo versionado:

- `data/content/aulas.json`
- `data/content/conquistas.json`
- `data/content/exercicios.json`
- `data/content/mundos.json`

Assets versionados:

- Fontes em `data/fonts/`.
- Fundos e imagens em `data/images/`.
- Frames de video em `data/video/`.
- Musicas em `data/audio/music/`.

Progresso local:

- `data/codequest.db`, gerado automaticamente e ignorado pelo Git.

Tabelas principais:

- `usuarios`: save ativo do jogador.
- `exercicios_concluidos`: impede XP duplicado e permite pular exercicios ja feitos.
- `exercicio_erros`: registra erros por usuario, mundo e exercicio para calcular XP potencial.
- `mundos_concluidos`: registra conclusao de mundos por usuario e desbloqueia novos mundos.
- `usuario_conquistas`: registra conquistas desbloqueadas por usuario sem duplicidade.

## Conquistas

As conquistas iniciais sao:

- `melhor_professor_ufal`: desbloqueada ao criar usuario com variacoes normalizadas de Alexandre Barbosa.
- `fenomeno`: desbloqueada ao atingir o XP maximo do conteudo implementado.
- `quase_hexa`: desbloqueada ao concluir todo o conteudo implementado com o XP minimo possivel.

No perfil, conquistas bloqueadas usam `data/images/achievements/locked_question.png`; conquistas desbloqueadas mostram seu icone real.

## Testes

```bash
python -m pytest tests
```

Leia [docs/testes_pytest.md](docs/testes_pytest.md) para entender a organizacao dos testes e como criar novos casos.

## Documentacao Tecnica

Veja [docs/arquitetura.md](docs/arquitetura.md) para detalhes sobre modulos, fluxo de telas, persistencia, regras de XP e pontos de extensao.

## Roadmap

- Polir acessibilidade visual e feedbacks de progresso.
- Revisar licenciamento/autoria de assets externos.
- Empacotar uma versao executavel para distribuicao local.
