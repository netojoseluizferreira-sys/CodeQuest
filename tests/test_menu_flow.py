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
