# Pytest e Testes Unitarios

Este projeto usa `pytest` para validar regras de negocio, persistencia, conteudo e partes do fluxo Pygame sem precisar abrir a janela do jogo durante a maior parte da suite.

## Como Rodar

Na raiz do projeto:

```bash
python -m pytest tests
```

Para rodar um arquivo especifico:

```bash
python -m pytest tests/test_xp_system.py
```

Para rodar um teste especifico:

```bash
python -m pytest tests/test_menu_flow.py::test_conclusao_do_mundo_9_aponta_para_mundos
```

## Organizacao da Suite

- `tests/test_database.py`: persistencia SQLite, usuario ativo, progresso de exercicios e mundos.
- `tests/test_xp_system.py`: niveis, teto de XP e soma de XP.
- `tests/test_learning_progress.py`: validacao de resposta, XP potencial e conclusao de mundo.
- `tests/test_achievements.py`: regras e persistencia de conquistas.
- `tests/test_content_and_credits.py`: integridade dos JSONs de aulas, exercicios, mundos, assets e creditos.
- `tests/test_menu_flow.py`: navegacao entre telas, conclusoes de mundo, mensagens e comportamento de cutscene.
- `tests/test_ui_components.py`: helpers de UI, quebra de texto e botoes.
- `tests/test_audio.py`: mapeamento de trilhas por contexto.

## Fixture de Banco Temporario

`tests/conftest.py` define a fixture `banco_temporario`. Ela redireciona o banco SQLite e arquivos legados para uma pasta temporaria do pytest, evitando alterar o save real em `data/codequest.db`.

Use essa fixture em testes que criam usuario, concluem exercicios, alteram XP ou desbloqueiam conquistas:

```python
def test_exemplo_com_banco(banco_temporario):
    usuario = database.criar_usuario("Ada", 12)

    assert usuario.nome == "Ada"
```

## Boas Praticas

- Teste regra de negocio em `backend/` ou `utils/` antes de testar tela.
- Para fluxo de menu, instancie `CodeQuestPygameMenu.__new__(CodeQuestPygameMenu)` quando nao precisar abrir Pygame.
- Prefira asserts pequenos e diretos: um teste deve explicar uma regra.
- Quando adicionar mundo, aula, exercicios ou asset obrigatorio, acrescente uma verificacao em `test_content_and_credits.py`.
- Quando mudar progressao, XP ou conquistas, rode a suite completa.

## O Que Evitar

- Nao use o banco real do jogador nos testes.
- Nao dependa de ordem aleatoria de dicionarios quando o comportamento exige uma ordem clara.
- Nao abra janelas ou toque audio real em testes unitarios; isole o comportamento com objetos simples ou monkeypatch.

## Checklist Para Novas Features

1. A feature tem regra de dominio? Crie teste em `tests/test_learning_progress.py`, `tests/test_xp_system.py`, `tests/test_achievements.py` ou `tests/test_database.py`.
2. A feature muda conteudo JSON? Atualize `tests/test_content_and_credits.py`.
3. A feature muda navegacao? Atualize `tests/test_menu_flow.py`.
4. A feature muda UI pura? Atualize `tests/test_ui_components.py`.
5. Rode `python -m pytest tests` antes de commitar.
