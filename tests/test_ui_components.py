"""Testes de componentes reutilizaveis de UI em modo Pygame headless."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from pygame_client.ui import Button, quebrar_texto, quebrar_texto_multilinha
from pygame_client.menu_learning_rendering import LearningRenderMixin


class _DummyLearningRenderer(LearningRenderMixin):
    pass


def setup_module():
    pygame.init()
    pygame.font.init()


def teardown_module():
    pygame.quit()


def test_quebrar_texto_mantem_linhas_dentro_da_largura():
    fonte = pygame.font.Font(None, 24)
    linhas = quebrar_texto("um texto grande para quebrar corretamente", fonte, 120)

    assert len(linhas) > 1
    assert all(fonte.size(linha)[0] <= 120 for linha in linhas)


def test_quebrar_texto_retorna_texto_original_quando_sem_palavras():
    fonte = pygame.font.Font(None, 24)

    assert quebrar_texto("", fonte, 120) == [""]


def test_quebrar_texto_multilinha_preserva_quebras_explicitas():
    fonte = pygame.font.Font(None, 24)

    linhas = quebrar_texto_multilinha("Conquista desbloqueada\nNome\nVá ao perfil", fonte, 300)

    assert linhas == ["Conquista desbloqueada", "Nome", "Vá ao perfil"]


def test_button_handle_event_executa_acao_ao_clicar_dentro():
    chamado = {"valor": False}
    botao = Button(pygame.Rect(10, 10, 100, 40), "Ok", lambda: chamado.update(valor=True))
    evento = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (20, 20)})

    assert botao.handle_event(evento) is True
    assert chamado["valor"] is True


def test_button_handle_event_ignora_clique_fora():
    chamado = {"valor": False}
    botao = Button(pygame.Rect(10, 10, 100, 40), "Ok", lambda: chamado.update(valor=True))
    evento = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (200, 200)})

    assert botao.handle_event(evento) is False
    assert chamado["valor"] is False


def test_button_draw_nao_altera_o_rect():
    tela = pygame.Surface((220, 120))
    fonte = pygame.font.Font(None, 24)
    rect = pygame.Rect(10, 10, 180, 70)
    botao = Button(rect.copy(), "Opcao com texto maior", lambda: None)

    botao.draw(tela, fonte, (0, 0))

    assert botao.rect == rect


def test_desenhar_input_verde_renderiza_campo_inativo_sem_name_error():
    renderer = _DummyLearningRenderer()
    renderer.screen = pygame.Surface((260, 90))
    renderer.font_body = pygame.font.Font(None, 24)
    renderer.active_field = "nome"

    renderer._desenhar_input_verde(pygame.Rect(10, 10, 180, 42), "", "idade", "18")

    assert renderer.screen.get_bounding_rect().width > 0
