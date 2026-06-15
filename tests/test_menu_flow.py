"""Testes unitarios de transicoes do menu principal sem abrir janela Pygame."""

from backend.usuario import Usuario
from pygame_client import menu_app


def test_continuar_sem_save_abre_tela_de_criacao_sem_criar_usuario(monkeypatch):
    chamadas_criar = []

    monkeypatch.setattr(menu_app, "carregar_usuario", lambda: None)

    def criar_usuario_indevido(nome, idade):
        chamadas_criar.append((nome, idade))

    monkeypatch.setattr(menu_app, "criar_usuario", criar_usuario_indevido)
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.status_message = ""
    app.status_kind = "normal"
    app.screen_name = "start"
    app.active_field = ""
    app.nome_input = "Nome antigo"
    app.idade_input = "99"

    app._continuar()

    assert chamadas_criar == []
    assert app.usuario is None
    assert app.nome_input == ""
    assert app.idade_input == ""
    assert app.active_field == "nome"
    assert app.status_kind == "normal"
    assert app.screen_name == "create"


def test_continuar_carrega_save_existente_sem_criar_usuario(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)
    chamadas_criar = []

    monkeypatch.setattr(menu_app, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(menu_app, "criar_usuario", lambda nome, idade: chamadas_criar.append((nome, idade)))
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.status_message = ""
    app.status_kind = "normal"
    app.screen_name = "start"
    app.active_field = ""

    app._continuar()

    assert chamadas_criar == []
    assert app.usuario == usuario
    assert app.status_kind == "success"
    assert app.screen_name == "hub"


def test_pula_exercicios_concluidos_ate_proximo_pendente(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)
    concluidos = {"1", "2"}

    monkeypatch.setattr(menu_app, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(
        menu_app,
        "exercicio_foi_concluido",
        lambda mundo, exercicio_id, usuario: str(exercicio_id) in concluidos,
    )

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = usuario
    app.mundo_ativo = "mundo_1"
    app.aula = {"trilha": [{"tipo": "exercicios", "exercicios": ["1", "2", "3"]}]}
    app.trilha_indice = 0
    app.exercicio_indice = 0
    app.resposta_texto = "resposta antiga"
    app.exercicio_respondido = True
    app.screen_name = "lesson"

    app._pular_exercicios_concluidos()

    assert app.trilha_indice == 0
    assert app.exercicio_indice == 2
    assert app.screen_name == "lesson"


def test_pula_bloco_concluido_mas_preserva_texto_de_aula(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)

    monkeypatch.setattr(menu_app, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(menu_app, "exercicio_foi_concluido", lambda *_args: True)

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = usuario
    app.mundo_ativo = "mundo_1"
    app.aula = {
        "trilha": [
            {"tipo": "exercicios", "exercicios": ["1", "2"]},
            {"tipo": "aula", "conteudo": ["Texto seguinte"]},
        ]
    }
    app.trilha_indice = 0
    app.exercicio_indice = 0
    app.resposta_texto = "resposta antiga"
    app.exercicio_respondido = True
    app.screen_name = "lesson"

    app._pular_exercicios_concluidos()

    assert app.trilha_indice == 1
    assert app.exercicio_indice == 0
    assert app.resposta_texto == ""
    assert app.exercicio_respondido is False
    assert app.screen_name == "lesson"


def test_iniciar_mundo_2_define_estado_da_aula(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)
    aula = {"titulo": "Aula 2", "trilha": [{"tipo": "aula", "conteudo": ["Texto"]}]}

    monkeypatch.setattr(menu_app, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(menu_app, "carregar_aula_pygame", lambda mundo, aula_id: aula)
    monkeypatch.setattr(menu_app, "carregar_exercicios_pygame", lambda mundo: {"1": {"id": 1}})

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.status_message = ""
    app.status_kind = "normal"
    app.screen_name = "worlds"

    app._iniciar_mundo_2()

    assert app.mundo_ativo == "mundo_2"
    assert app.aula_ativa == "aula_1"
    assert app.aula == aula
    assert app.exercicios == {"1": {"id": 1}}
    assert app.trilha_indice == 0
    assert app.exercicio_indice == 0
    assert app.screen_name == "lesson"
