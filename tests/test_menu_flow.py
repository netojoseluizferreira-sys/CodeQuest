"""Testes unitarios de transicoes do menu principal sem abrir janela Pygame."""

from backend.usuario import Usuario
from pygame_client import menu_app


def test_continuar_cria_usuario_padrao_quando_nao_existe_save(monkeypatch):
    criado = Usuario(nome="Aventureiro", idade=18)
    chamadas_criar = []
    carregamentos = iter([None, criado])

    monkeypatch.setattr(menu_app, "carregar_usuario", lambda: next(carregamentos))

    def criar_usuario_padrao(nome, idade):
        chamadas_criar.append((nome, idade))
        return criado

    monkeypatch.setattr(menu_app, "criar_usuario", criar_usuario_padrao)
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.status_message = ""
    app.status_kind = "normal"
    app.screen_name = "start"
    app.active_field = ""

    app._continuar()

    assert chamadas_criar == [("Aventureiro", 18)]
    assert app.usuario == criado
    assert app.status_kind == "success"
    assert app.screen_name == "hub"


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
