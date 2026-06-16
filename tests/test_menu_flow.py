"""Testes unitários de transições do menu principal sem abrir janela Pygame."""

import pygame

from backend.usuario import Usuario
from pygame_client import menu_app, menu_events, menu_navigation
from pygame_client.ui import Button


def test_continuar_sem_save_abre_tela_de_criacao_sem_criar_usuario(monkeypatch):
    chamadas_criar = []

    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: None)

    def criar_usuario_indevido(nome, idade):
        chamadas_criar.append((nome, idade))

    monkeypatch.setattr(menu_navigation, "criar_usuario", criar_usuario_indevido)
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

    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(menu_navigation, "criar_usuario", lambda nome, idade: chamadas_criar.append((nome, idade)))
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


def test_botao_creditos_volta_para_inicio_mesmo_com_usuario():
    usuario = Usuario(nome="Ada", idade=12)

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = usuario
    app.screen_name = "credits"

    botoes = app._botoes_tela()

    assert len(botoes) == 1
    assert botoes[0].action.__name__ == "_voltar_inicio"


def test_voltar_contextual_creditos_vai_para_inicio_mesmo_com_usuario():
    usuario = Usuario(nome="Ada", idade=12)

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = usuario
    app.screen_name = "credits"
    app.status_message = ""
    app.status_kind = "normal"

    app._voltar_contextual()

    assert app.screen_name == "start"
    assert app.status_message == "Bem-vindo ao CodeQuest."


def test_cursor_muda_apenas_quando_estado_clicavel_muda(monkeypatch):
    chamadas = []
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.screen_name = "start"
    app.link_rect = None
    app.credit_link_rect = None
    app._cursor_atual = None
    botao = Button(pygame.Rect(10, 10, 100, 40), "Ok", lambda: None)

    monkeypatch.setattr(menu_app.pygame.mouse, "set_cursor", chamadas.append)

    app._atualizar_cursor((20, 20), [botao])
    app._atualizar_cursor((25, 25), [botao])
    app._atualizar_cursor((200, 200), [botao])

    assert chamadas == [pygame.SYSTEM_CURSOR_HAND, pygame.SYSTEM_CURSOR_ARROW]


def test_link_de_aula_abre_url_do_segmento(monkeypatch):
    chamadas = []
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.screen_name = "lesson"
    app.link_rect = pygame.Rect(10, 10, 120, 30)
    app.content_x = 150
    app.content_width = 980
    app.active_field = "nome"
    app._segmento_atual = lambda: {"tipo": "aula", "video_url": "https://www.youtube.com/watch?v=abc123"}
    app._botoes_tela = lambda: []

    monkeypatch.setattr(menu_events.webbrowser, "open", chamadas.append)

    evento = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (20, 20)})
    app._processar_clique(evento)

    assert chamadas == ["https://www.youtube.com/watch?v=abc123"]


def test_link_dos_creditos_abre_github(monkeypatch):
    chamadas = []
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.screen_name = "credits"
    app.credit_link_rect = pygame.Rect(10, 10, 260, 30)
    app._botoes_tela = lambda: []

    monkeypatch.setattr(menu_events.webbrowser, "open", chamadas.append)

    evento = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (20, 20)})
    app._processar_clique(evento)

    assert chamadas == ["https://github.com/netojoseluizferreira-sys/CodeQuest"]


def test_mundo_indisponivel_mostra_texto_em_breve_atualizado():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.status_message = ""
    app.status_kind = "normal"

    app._mostrar_mundo_em_breve()

    assert app.status_message == (
        "EM BREVE!\n"
        "Os segredos deste mundo ainda não estão prontos para serem revelados. "
        "Continue sua jornada pelos mundos disponíveis enquanto isso."
    )


def test_pula_exercicios_concluidos_ate_proximo_pendente(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)
    concluidos = {"1", "2"}

    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(
        menu_navigation,
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

    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(menu_navigation, "exercicio_foi_concluido", lambda *_args: True)

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


def test_mensagem_conquista_desbloqueada_usa_tres_linhas():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)

    mensagem = app._mensagem_conquistas_desbloqueadas([{"nome": "Melhor professor da UFAL"}])

    assert mensagem == (
        "Conquista desbloqueada!\n"
        "Melhor professor da UFAL\n"
        "Vá ao perfil para visualizar."
    )


def test_avancar_exercicio_nao_exibe_texto_generico_de_proximo_desafio(monkeypatch):
    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: Usuario(nome="Ada", idade=12))
    monkeypatch.setattr(menu_navigation, "exercicio_foi_concluido", lambda *_args: False)

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = Usuario(nome="Ada", idade=12)
    app.mundo_ativo = "mundo_1"
    app.aula = {"trilha": [{"tipo": "exercicios", "exercicios": ["1", "2"]}]}
    app.trilha_indice = 0
    app.exercicio_indice = 0
    app.resposta_texto = "ok"
    app.exercicio_respondido = True
    app.status_message = "mensagem antiga"
    app.status_kind = "success"
    app.screen_name = "lesson"

    app._avancar_exercicio()

    assert app.exercicio_indice == 1
    assert app.status_message == ""
    assert "Próximo desafio" not in app.status_message


def test_avancar_segmento_nao_exibe_texto_generico_de_jornada(monkeypatch):
    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: Usuario(nome="Ada", idade=12))

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = Usuario(nome="Ada", idade=12)
    app.mundo_ativo = "mundo_1"
    app.aula = {"trilha": [{"tipo": "aula"}, {"tipo": "aula"}]}
    app.trilha_indice = 0
    app.exercicio_indice = 0
    app.resposta_texto = "ok"
    app.exercicio_respondido = True
    app.status_message = "mensagem antiga"
    app.status_kind = "success"
    app.screen_name = "lesson"

    app._avancar_segmento()

    assert app.trilha_indice == 1
    assert app.status_message == ""
    assert "Continue sua jornada" not in app.status_message


def test_iniciar_mundo_2_define_estado_da_aula(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)
    aula = {"titulo": "Aula 2", "trilha": [{"tipo": "aula", "conteudo": ["Texto"]}]}

    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(menu_navigation, "obter_status_mundo", lambda *_args: {"estado": menu_navigation.STATUS_DISPONIVEL})
    monkeypatch.setattr(menu_navigation, "aula_inicial", lambda mundo: "aula_1")
    monkeypatch.setattr(menu_navigation, "carregar_aula_pygame", lambda mundo, aula_id: aula)
    monkeypatch.setattr(menu_navigation, "carregar_exercicios_pygame", lambda mundo: {"1": {"id": 1}})

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


def test_iniciar_mundo_2_bloqueia_quando_mundo_1_incompleto(monkeypatch):
    usuario = Usuario(nome="Ada", idade=12)
    chamadas_aula = []

    monkeypatch.setattr(menu_navigation, "carregar_usuario", lambda: usuario)
    monkeypatch.setattr(
        menu_navigation,
        "obter_status_mundo",
        lambda *_args: {
            "estado": menu_navigation.STATUS_BLOQUEADO,
            "mensagem": "Conclua Mundo 1 antes de abrir Mundo 2.",
        },
    )
    monkeypatch.setattr(menu_navigation, "carregar_aula_pygame", lambda mundo, aula_id: chamadas_aula.append((mundo, aula_id)))

    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.usuario = usuario
    app.status_message = ""
    app.status_kind = "normal"
    app.screen_name = "worlds"

    app._iniciar_mundo_2()

    assert chamadas_aula == []
    assert app.screen_name == "worlds"
    assert app.status_kind == "error"
    assert app.status_message == "Conclua Mundo 1 antes de abrir Mundo 2."


def test_conclusao_do_mundo_2_aponta_para_mundo_3():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_2"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 3"
    assert callable(acao)
    assert "Mundo 2" in app._texto_conclusao_mundo(label)
    assert "Mundo 3" in app._texto_conclusao_mundo(label)


def test_conclusao_do_mundo_3_aponta_para_mundo_4():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_3"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 4"
    assert callable(acao)
    assert "Mundo 3" in app._texto_conclusao_mundo(label)
    assert "Mundo 4" in app._texto_conclusao_mundo(label)


def test_conclusao_do_mundo_4_aponta_para_mundo_5():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_4"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 5"
    assert callable(acao)
    assert "Mundo 4" in app._texto_conclusao_mundo(label)
    assert "Mundo 5" in app._texto_conclusao_mundo(label)


def test_conclusao_do_mundo_5_aponta_para_mundo_6():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_5"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 6"
    assert callable(acao)
    assert "Mundo 5" in app._texto_conclusao_mundo(label)
    assert "Mundo 6" in app._texto_conclusao_mundo(label)


def test_conclusao_do_mundo_6_aponta_para_mundo_7():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_6"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 7"
    assert callable(acao)
    assert "Mundo 6" in app._texto_conclusao_mundo(label)
    assert "Mundo 7" in app._texto_conclusao_mundo(label)


def test_conclusao_do_mundo_7_aponta_para_mundo_8():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_7"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 8"
    assert callable(acao)
    assert "Mundo 7" in app._texto_conclusao_mundo(label)
    assert "Mundo 8" in app._texto_conclusao_mundo(label)


def test_conclusao_do_mundo_8_aponta_para_mundo_9():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.mundo_ativo = "mundo_8"
    app.status_message = ""
    app.status_kind = "normal"

    label, acao = app._proximo_mundo_conclusao()

    assert label == "Mundo 9"
    assert callable(acao)
    assert "Mundo 8" in app._texto_conclusao_mundo(label)
    assert "Mundo 9" in app._texto_conclusao_mundo(label)


def test_contexto_musical_diferencia_aula_e_exercicio():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.screen_name = "lesson"
    app.aula = {
        "trilha": [
            {"tipo": "aula"},
            {"tipo": "exercicios", "exercicios": ["1"]},
        ]
    }
    app.trilha_indice = 0

    assert app._contexto_musica_atual() == "lesson"

    app.trilha_indice = 1

    assert app._contexto_musica_atual() == "exercise"


def test_contexto_musical_create_usa_tela_inicial():
    app = menu_app.CodeQuestPygameMenu.__new__(menu_app.CodeQuestPygameMenu)
    app.screen_name = "create"

    assert app._contexto_musica_atual() == "start"
