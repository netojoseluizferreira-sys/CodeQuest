"""Aplicacao Pygame principal do CodeQuest e fluxo de telas do jogo."""

import glob
import math
import os

import pygame
import webbrowser

from backend.xp_system import xp_para_proximo_nivel
from pygame_client.audio import AudioController
from pygame_client.content import carregar_aula_pygame, carregar_exercicios_pygame, obter_exercicio
from pygame_client.learning_progress import registrar_resposta
from pygame_client.palette import PALETTE
from pygame_client.settings import WINDOW
from pygame_client.ui import Button, desenhar_texto_centralizado, quebrar_texto
from utils.database import carregar_usuario, criar_usuario, resetar_banco_de_dados


MUNDO_ATIVO = "mundo_1"
AULA_ATIVA = "aula_1"

MUNDOS_BYTHOS = [
    ("Mundo 1", "Introdução", "Cabana do Oráculo", True),
    ("Mundo 2", "Primeiros Passos", "Tenda do Iniciado", False),
    ("Mundo 3", "Operadores", "Forja das Runas", False),
    ("Mundo 4", "Estruturas de Decisão", "Torre dos Julgamentos", False),
    ("Mundo 5", "Estruturas de Repetição", "Moinho Eterno", False),
    ("Mundo 6", "Funções", "Santuário dos Invocadores", False),
    ("Mundo 7", "Vetores / Listas", "Biblioteca dos Pergaminhos", False),
    ("Mundo 8", "Dicionários", "Templo da Grade Sagrada", False),
    ("Mundo 9", "Recursividade", "Citadela do Espelho Infinito", False),
]

_VERDE = (30, 100, 50)
_BRANCO = (255, 255, 255)
_VERDE_CLARO = (100, 200, 120)
_KW_VERDE = dict(background=_VERDE, hover_background=_BRANCO, text_color=_BRANCO, hover_text_color=_VERDE, border_color=_VERDE_CLARO)

CUTSCENE_TEXTS = [
    "Em um dia comum, Faísca estava em seu quarto, mexendo no seu computador...",
    "Quando menos esperava, alguém bateu à sua porta. Curioso, ele foi até lá atender.",
    "Quando abriu, era Frederick, o entregador do bairro. Tinha uma encomenda em seu nome. Faísca ficou confuso, pois não estava esperando por nada. Mesmo assim, ele recebeu a caixa.",
    "Quando abriu, ficou surpreso com o que tinha dentro...",
    "Um pen-drive, aparentemente já usado. Colocou o pen-drive de volta na caixa e voltou para o seu quarto, sem dar muita importância.",
    "De volta ao quarto, deixou o pen-drive de lado e voltou ao que estava fazendo. Ainda tinha muito jogo pela frente.",
    "O cansaço começou a tomar conta e, pouco a pouco, Faísca sentia seus olhos ficarem mais pesados. Era hora de descansar.",
    "Ele desligou o monitor e se levantou da cadeira, pronto para ir dormir. Ao se levantar, tropeçou em algo no chão. Era o pen-drive. Olhou para ele por alguns segundos, intrigado e...",
    "CATAPLÓFITE!!! Assim que conectou o pen-drive, a tela acendeu sozinha. Letras vermelhas piscavam na tela: ERRO! Você está sendo transferido para o Arquipélago de Bythos...",
    "Antes que Faísca pudesse reagir, uma luz verde brilhante começou a engoli-lo. Ele sentiu seu corpo sendo puxado, sugado para dentro da tela do computador. Tudo ficou escuro. Ele estava sendo transferido para outra dimensão.",
]


class CodeQuestPygameMenu:
    """Loop Pygame principal do CodeQuest: gerencia telas, eventos, áudio e progresso."""

    def __init__(self):
        """Inicializa Pygame, carrega fontes/imagens/vídeos e restaura o save do usuário.

        Configura a janela 1280×800, o AudioController, as fontes PressStart2P,
        RammettoOne e WendyOne, os frames de vídeo de fundo (start, hub, créditos, perfil),
        as imagens da cutscene (data/cutscenes/1-10.jpeg) e os atributos de estado
        de tela, campo ativo, cutscene fade e fluxo de aprendizagem.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW.width, WINDOW.height))
        pygame.display.set_caption(WINDOW.title)
        self.clock = pygame.time.Clock()
        self.audio = AudioController()
        self.audio.inicializar()
        _data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        _wendyone = os.path.join(_data_dir, "WendyOne-Regular.ttf")
        _pressstart = os.path.join(_data_dir, "PressStart2P-Regular.ttf")
        _rammetto = os.path.join(_data_dir, "RammettoOne-Regular.ttf")
        self.font_title = pygame.font.Font(_pressstart, 52)
        self.font_title_large = pygame.font.Font(_pressstart, 64)
        self.font_hub_subtitle = pygame.font.Font(_rammetto, 28)
        self.font_subtitle = pygame.font.Font(_rammetto, 28)
        _titulo_w = sum(self.font_title_large.size(c)[0] for c in "CodeQuest") + 2 * 8
        _sub_size = 22
        _sub_texto = "Uma Jornada pelo Arquipélago de Bythos"
        _font_sub = pygame.font.Font(_rammetto, _sub_size)
        while _font_sub.size(_sub_texto)[0] > _titulo_w and _sub_size > 8:
            _sub_size -= 1
            _font_sub = pygame.font.Font(_rammetto, _sub_size)
        self.font_subtitle_small = _font_sub
        self.font_start_btn = pygame.font.Font(_wendyone, 21)
        self.font_welcome = pygame.font.Font(_wendyone, 20)
        self.font_body = pygame.font.Font(_wendyone, 21)
        self.font_small = pygame.font.Font(_wendyone, 17)
        self.font_tiny = pygame.font.Font(_wendyone, 15)
        self.font_block_title = pygame.font.Font(_rammetto, 16)
        self.font_block_body = pygame.font.Font(_wendyone, 20)
        self.font_credit_section = pygame.font.Font(_rammetto, 23)
        self.font_credit_body_bold = pygame.font.Font(_wendyone, 22)
        self.font_cutscene_text = pygame.font.Font(_wendyone, 26)
        self.font_credit_body = pygame.font.Font(_wendyone, 22)
        self.font_credit_small_bold = pygame.font.Font(_rammetto, 16)
        self.font_credit_small_reg = pygame.font.Font(_wendyone, 20)
        self.font_credit_quote = pygame.font.Font(_wendyone, 18)
        self.font_credit_footer_bold = pygame.font.Font(_wendyone, 16)
        self.font_status_success = pygame.font.Font(_wendyone, 24)
        self.font_profile_label = pygame.font.Font(_rammetto, 19)
        self.font_profile_value = pygame.font.Font(_wendyone, 38)
        self.content_x = 150
        self.content_width = WINDOW.width - (self.content_x * 2)
        self.running = True
        self.screen_name = "start"
        self.status_message = "Bem-vindo ao CodeQuest."
        self.status_kind = "normal"
        self.usuario = carregar_usuario()
        self.credit_scroll = 0
        self.nome_input = ""
        self.idade_input = ""
        self.active_field = "nome"
        self.aula = None
        self.exercicios = {}
        self.trilha_indice = 0
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self.link_rect = None
        self.btn_continuar_y = None
        self._frame_cache = {}
        _frames_dir = os.path.join(_data_dir, "video_frames")
        self.video_frame_paths = sorted(glob.glob(os.path.join(_frames_dir, "*.jpg")))
        self.video_frame_index = 0
        self.video_frame_timer = 0
        self.glow_timer = 0
        self.start_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.start_overlay.fill((0, 0, 0, 140))
        _hub_frames_dir = os.path.join(_data_dir, "hub_frames")
        self.hub_frame_paths = sorted(glob.glob(os.path.join(_hub_frames_dir, "*.jpg")))
        self.hub_frame_index = 0
        self.hub_frame_timer = 0
        self.hub_glow_timer = 0
        self.hub_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.hub_overlay.fill((0, 0, 0, 140))
        _creditos_frames_dir = os.path.join(_data_dir, "creditos_frames")
        self.creditos_frame_paths = sorted(glob.glob(os.path.join(_creditos_frames_dir, "*.jpg")))
        self.creditos_frame_index = 0
        self.creditos_frame_timer = 0
        _cutscenes_dir = os.path.join(_data_dir, "cutscenes")
        self.cutscene_images = []
        for _i in range(1, 11):
            _cpath = os.path.join(_cutscenes_dir, f"{_i}.jpeg")
            if os.path.exists(_cpath):
                _cimg = pygame.image.load(_cpath).convert()
                self.cutscene_images.append(pygame.transform.scale(_cimg, (900, 500)))
            else:
                self.cutscene_images.append(None)
        self.cutscene_index = 0
        self.cutscene_fade_alpha = 0
        self.cutscene_fade_state = "visible"
        self.cutscene_fade_next = None
        self._cutscene_prev_frame = None
        _cut_bg_path = None
        for _ext in ("jpeg", "jpg", "png"):
            _p = os.path.join(_data_dir, f"imagem_cut.{_ext}")
            if os.path.exists(_p):
                _cut_bg_path = _p
                break
        if _cut_bg_path:
            _cbg = pygame.image.load(_cut_bg_path).convert()
            self.cutscene_bg = pygame.transform.scale(_cbg, (WINDOW.width, WINDOW.height))
        else:
            self.cutscene_bg = None
        _perfil_frames_dir = os.path.join(_data_dir, "perfil_frames")
        self.perfil_frame_paths = sorted(glob.glob(os.path.join(_perfil_frames_dir, "*.jpg")))
        self.perfil_frame_index = 0
        self.perfil_frame_timer = 0
        self.perfil_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.perfil_overlay.fill((0, 0, 0, 120))
        _mundos_frames_dir = os.path.join(_data_dir, "mundos_frames")
        self.mundos_frame_paths = sorted(glob.glob(os.path.join(_mundos_frames_dir, "*.jpg")))
        self.mundos_frame_index = 0
        self.mundos_frame_timer = 0
        self.mundos_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.mundos_overlay.fill((0, 0, 0, 150))
        self.mundos_glow_timer = 0
        self.lesson_glow_timer = 0
        self.font_lesson_title = pygame.font.Font(_pressstart, 28)
        self.font_lesson_content = pygame.font.Font(_wendyone, 20)
        self.font_lesson_body = pygame.font.Font(_wendyone, 20)
        _less_ov = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        _less_ov.fill((0, 0, 0, 160))
        self.lesson_overlay = _less_ov

    def run(self):
        """Inicia a trilha sonora e executa o loop principal a 60 fps até self.running ser False."""
        self.audio.tocar_trilha()
        while self.running:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # Resetando cursor para seta no inicio do frame
            self._processar_eventos()
            self._renderizar()
            self.clock.tick(WINDOW.fps)

        self.audio.encerrar()
        pygame.quit()

    def _obter_frame_animado(self, frame_paths, frame_index):
        """Carrega e retorna um frame de fundo sob demanda.

        Recebe:
            frame_paths (list[str]): Caminhos dos frames da animacao.
            frame_index (int): Indice do frame desejado.

        Retorna:
            pygame.Surface | None: Frame escalado para a janela, ou None quando
            a lista de caminhos estiver vazia.
        """
        if not frame_paths:
            return None

        frame_path = frame_paths[frame_index % len(frame_paths)]
        if frame_path not in self._frame_cache:
            image = pygame.image.load(frame_path).convert()
            self._frame_cache[frame_path] = pygame.transform.scale(image, (WINDOW.width, WINDOW.height))
        return self._frame_cache[frame_path]

    def _botoes_tela(self):
        """Retorna a lista de botões da tela atualmente ativa.

        Retorna:
            list[Button]: Botões prontos para desenho e tratamento de evento;
            lista vazia para telas sem botões registrados.
        """
        if self.screen_name == "start":
            return self._botoes_inicio()
        if self.screen_name == "create":
            return self._botoes_criacao()
        if self.screen_name == "hub":
            return self._botoes_hub()
        if self.screen_name == "worlds":
            return self._botoes_mundos()
        if self.screen_name == "profile":
            return [Button(pygame.Rect(30, WINDOW.height - 75, 160, 45), "Voltar", self._abrir_hub, **_KW_VERDE)]
        if self.screen_name == "credits":
            return [self._botao_voltar_hub(**_KW_VERDE) if self.usuario else self._botao_voltar_inicio(**_KW_VERDE)]
        if self.screen_name == "cutscene":
            return []
        if self.screen_name == "lesson":
            return self._botoes_fluxo_aprendizado()
        if self.screen_name == "complete":
            return [self._botao_voltar_hub()]
        return []

    def _botoes_inicio(self):
        """Constrói os quatro botões da tela inicial (Novo jogo, Continuar, Sair, Créditos).

        Retorna:
            list[Button]: Botões posicionados verticalmente a partir de y=380
            com espaçamento de 65px entre si.
        """
        largura = 420
        altura = 58
        x = (WINDOW.width - largura) // 2
        y_inicial = 380
        _esp = 65
        return [
            Button(pygame.Rect(x, y_inicial, largura, altura), "Novo jogo", self._novo_jogo, **_KW_VERDE),
            Button(pygame.Rect(x, y_inicial + _esp, largura, altura), "Continuar", self._continuar, **_KW_VERDE),
            Button(pygame.Rect(x, y_inicial + _esp * 2, largura, altura), "Sair", self._sair, **_KW_VERDE),
            Button(pygame.Rect(WINDOW.width - 190, WINDOW.height - 75, 160, 45), "Creditos", self._abrir_creditos, **_KW_VERDE),
        ]

    def _botoes_criacao(self):
        """Constrói os botões da tela de criação de personagem (Criar e Voltar).

        Retorna:
            list[Button]: Dois botões lado a lado na linha y=505.
        """
        return [
            Button(pygame.Rect(410, 505, 220, 54), "Criar", self._criar_personagem, **_KW_VERDE),
            Button(pygame.Rect(670, 505, 220, 54), "Voltar", self._voltar_inicio, **_KW_VERDE),
        ]

    def _botoes_hub(self):
        """Constrói os botões do hub principal (Arquipélago, Tela inicial, Sair, Perfil).

        Retorna:
            list[Button]: Três botões centralizados a partir de y=385 e um botão
            de perfil no canto inferior esquerdo.
        """
        largura = 420
        altura = 58
        x = (WINDOW.width - largura) // 2
        y_inicial = 385
        _esp = 65
        return [
            Button(pygame.Rect(x, y_inicial, largura, altura), "Arquipelago de Bythos", self._abrir_cutscene, **_KW_VERDE),
            Button(pygame.Rect(x, y_inicial + _esp, largura, altura), "Tela inicial", self._voltar_inicio, **_KW_VERDE),
            Button(pygame.Rect(x, y_inicial + _esp * 2, largura, altura), "Sair", self._sair, **_KW_VERDE),
            Button(pygame.Rect(30, WINDOW.height - 75, 160, 45), "Perfil", self._abrir_perfil, **_KW_VERDE),
        ]

    def _botoes_mundos(self):
        """Constrói os botões da tela de seleção de mundos em grade.

        Retorna:
            list[Button]: Botões dos mundos organizados em 3 colunas e botão Voltar.
        """
        _bw = 330
        _bh = 58
        _gap_x = 28
        _gap_y = 16
        _grid_w = _bw * 3 + _gap_x * 2
        _start_x = (WINDOW.width - _grid_w) // 2
        _start_y = 300
        botoes = []
        for indice, (numero, _assunto, nome, disponivel) in enumerate(MUNDOS_BYTHOS):
            col = indice % 3
            row = indice // 3
            x = _start_x + col * (_bw + _gap_x)
            y = _start_y + row * (_bh + _gap_y)
            acao = self._iniciar_mundo_1 if disponivel else self._mostrar_mundo_em_breve
            botoes.append(Button(pygame.Rect(x, y, _bw, _bh), f"{numero} - {nome}", acao, **_KW_VERDE))
        botoes.append(Button(pygame.Rect(30, WINDOW.height - 75, 160, 45), "Voltar", self._abrir_hub, **_KW_VERDE))
        return botoes

    def _botoes_fluxo_aprendizado(self):
        """Constrói os botões do segmento de aula ou exercício atualmente exibido.

        Para aulas: botão Continuar com posição dinâmica dependendo de btn_continuar_y.
        Para múltipla escolha: um botão por alternativa (A–D) mais Voltar.
        Para texto livre: botão Responder ou Próximo (após acerto) mais Voltar.

        Retorna:
            list[Button]: Botões prontos para o segmento ativo; contém apenas
            o botão Voltar quando não houver segmento carregado.
        """
        segmento = self._segmento_atual()
        if segmento is None:
            return [self._botao_voltar_hub()]

        if segmento["tipo"] == "aula":
            return [
                Button(pygame.Rect(WINDOW.width - 310, WINDOW.height - 88, 250, 52), "Continuar", self._avancar_segmento, **_KW_VERDE),
                self._botao_voltar_mundos(**_KW_VERDE),
            ]

        if self.exercicio_respondido:
            return [
                Button(pygame.Rect(WINDOW.width - 340, WINDOW.height - 88, 250, 52), "Proximo", self._avancar_exercicio),
                self._botao_voltar_mundos(),
            ]

        exercicio = self._exercicio_atual()
        if exercicio and exercicio["tipo"] == "multipla_escolha":
            botoes = []
            for indice, opcao in enumerate(exercicio["opcoes"]):
                y = 285 + (indice * 86)
                botoes.append(
                    Button(
                        pygame.Rect(self.content_x, y, self.content_width, 72),
                        f"{chr(65 + indice)}) {opcao}",
                        lambda escolha=indice: self._responder_exercicio(escolha),
                        background=PALETTE.surface,
                        hover_background=PALETTE.surface_hover,
                        text_color=PALETTE.text,
                    )
                )
            botoes.append(self._botao_voltar_mundos())
            return botoes

        return [
            Button(pygame.Rect(WINDOW.width - 340, WINDOW.height - 88, 250, 52), "Responder", self._responder_texto_livre),
            self._botao_voltar_mundos(),
        ]

    def _botao_voltar_inicio(self, **kw):
        """Cria o botão Voltar que navega para a tela inicial.

        Recebe:
            **kw: Kwargs de estilo repassados ao Button (background, hover_background, etc.).

        Retorna:
            Button: Botão posicionado no canto inferior esquerdo (x=60, y=height-88).
        """
        return Button(pygame.Rect(60, WINDOW.height - 88, 190, 52), "Voltar", self._voltar_inicio, **kw)

    def _botao_voltar_hub(self, **kw):
        """Cria o botão Voltar que navega para o hub.

        Recebe:
            **kw: Kwargs de estilo repassados ao Button.

        Retorna:
            Button: Botão posicionado no canto inferior esquerdo (x=60, y=height-88).
        """
        return Button(pygame.Rect(60, WINDOW.height - 88, 190, 52), "Voltar", self._abrir_hub, **kw)

    def _botao_voltar_mundos(self, **kw):
        """Cria o botão Mundos que navega para a seleção de mundos.

        Recebe:
            **kw: Kwargs de estilo repassados ao Button.

        Retorna:
            Button: Botão posicionado no canto inferior esquerdo (x=60, y=height-88).
        """
        return Button(pygame.Rect(60, WINDOW.height - 88, 190, 52), "Mundos", self._abrir_mundos, **kw)

    def _processar_eventos(self):
        """Drena a fila de eventos do Pygame e despacha para os handlers de tecla e clique."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._sair()
            elif event.type == pygame.KEYDOWN:
                self._processar_tecla(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._processar_clique(event)

    def _processar_clique(self, event):
        """Trata cliques de mouse conforme a tela ativa.

        Na tela "create", ativa o campo nome ou idade pelo rect clicado.
        Na tela "cutscene", detecta clique no botão Avançar manual.
        Na tela "lesson", detecta clique no link do YouTube e no campo de resposta.
        Em seguida repassa o evento a todos os botões da tela via handle_event.

        Recebe:
            event (pygame.event.Event): Evento MOUSEBUTTONDOWN com atributo pos.
        """
        if self.screen_name == "create":
            if pygame.Rect(390, 285, 500, 50).collidepoint(event.pos):
                self.active_field = "nome"
            elif pygame.Rect(390, 385, 220, 50).collidepoint(event.pos):
                self.active_field = "idade"

        if self.screen_name == "cutscene":
            _cs_bw, _cs_bh = 190, 45
            _cs_by = WINDOW.height - 65
            _cs_bx2 = WINDOW.width - 20 - _cs_bw
            _cs_bx1 = _cs_bx2 - 10 - _cs_bw
            if pygame.Rect(_cs_bx2, _cs_by, _cs_bw, _cs_bh).collidepoint(event.pos):
                self._avancar_cutscene()
            elif pygame.Rect(_cs_bx1, _cs_by, _cs_bw, _cs_bh).collidepoint(event.pos):
                self._abrir_mundos()

        if self.screen_name == "lesson":
            segmento = self._segmento_atual()

            if self.link_rect and self.link_rect.collidepoint(event.pos):
                webbrowser.open("https://www.youtube.com/watch?v=8mei6uVttho")

            exercicio = self._exercicio_atual() if segmento and segmento["tipo"] == "exercicios" else None
            if exercicio and exercicio["tipo"] == "completar":
                if pygame.Rect(self.content_x, 455, self.content_width, 52).collidepoint(event.pos):
                    self.active_field = "resposta"

        for button in self._botoes_tela():
            if button.handle_event(event):
                self.audio.tocar_botao()
                break

    def _processar_tecla(self, event):
        """Trata teclas conforme a tela ativa.

        ESC chama _voltar_contextual em qualquer tela. Na tela "credits",
        W/S e setas controlam a rolagem. Na tela "cutscene", qualquer tecla
        avança a cena. Nas telas "create" e "lesson", encaminha para os
        handlers de digitação específicos.

        Recebe:
            event (pygame.event.Event): Evento KEYDOWN com atributos key e unicode.
        """
        if event.key == pygame.K_ESCAPE:
            self._voltar_contextual()
            return

        if self.screen_name == "credits":
            if event.key in (pygame.K_UP, pygame.K_w):
                self.credit_scroll = max(0, self.credit_scroll - 32)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.credit_scroll += 32
            return

        if self.screen_name == "cutscene":
            self._avancar_cutscene()
            return

        if self.screen_name == "create":
            self._digitar_criacao(event)
        elif self.screen_name == "lesson" and self.active_field == "resposta":
            self._digitar_resposta(event)

    def _digitar_criacao(self, event):
        """Processa teclas no formulário de criação de personagem.

        Enter submete o formulário, Tab alterna entre nome e idade,
        Backspace apaga o último caractere do campo ativo. Letras vão para
        nome (máx 24 chars) e dígitos vão para idade (máx 3 chars).

        Recebe:
            event (pygame.event.Event): Evento KEYDOWN com atributos key e unicode.
        """
        if event.key == pygame.K_RETURN:
            self._criar_personagem()
            return
        if event.key == pygame.K_TAB:
            self.active_field = "idade" if self.active_field == "nome" else "nome"
            return
        if event.key == pygame.K_BACKSPACE:
            if self.active_field == "nome":
                self.nome_input = self.nome_input[:-1]
            else:
                self.idade_input = self.idade_input[:-1]
            return

        if self.active_field == "nome" and event.unicode and len(self.nome_input) < 24:
            if event.unicode.isprintable():
                self.nome_input += event.unicode
        elif self.active_field == "idade" and event.unicode.isdigit() and len(self.idade_input) < 3:
            self.idade_input += event.unicode

    def _digitar_resposta(self, event):
        """Processa teclas no campo de resposta textual livre.

        Enter submete a resposta, Backspace apaga o último caractere.
        Caracteres imprimíveis são acumulados até o limite de 80.

        Recebe:
            event (pygame.event.Event): Evento KEYDOWN com atributos key e unicode.
        """
        if event.key == pygame.K_RETURN:
            self._responder_texto_livre()
            return
        if event.key == pygame.K_BACKSPACE:
            self.resposta_texto = self.resposta_texto[:-1]
            return
        if event.unicode and event.unicode.isprintable() and len(self.resposta_texto) < 80:
            self.resposta_texto += event.unicode

    def _renderizar(self):
        """Renderiza a tela ativa e todos os botões por cima, depois chama display.flip."""
        if self.screen_name == "start":
            self._renderizar_fundo_video()
            self._renderizar_inicio()
        elif self.screen_name == "hub":
            self._renderizar_fundo_hub()
            self._renderizar_hub()
        elif self.screen_name == "profile":
            self._renderizar_fundo_perfil()
            self._renderizar_perfil()
        elif self.screen_name == "worlds":
            self._renderizar_fundo_mundos()
            self._renderizar_mundos()
        elif self.screen_name == "cutscene":
            self._renderizar_cutscene()
        else:
            if self.screen_name == "create":
                self._renderizar_fundo_perfil()
                self.screen.blit(self.lesson_overlay, (0, 0))
            elif self.screen_name == "credits":
                self.screen.fill((11, 25, 11))
            else:
                self.screen.fill(PALETTE.background)
            if self.screen_name == "create":
                self._renderizar_criacao()
            elif self.screen_name == "credits":
                self._renderizar_creditos()
            elif self.screen_name == "lesson":
                self._renderizar_fluxo_aprendizado()
            elif self.screen_name == "complete":
                self._renderizar_conclusao()

        mouse_pos = pygame.mouse.get_pos()
        _btn_font = self.font_start_btn if self.screen_name in {"start", "hub", "profile", "worlds"} else self.font_body
        for button in self._botoes_tela():
            button.draw(self.screen, _btn_font, mouse_pos)
        pygame.display.flip()

    def _renderizar_fundo_video(self):
        """Blita o frame atual da animação de fundo da tela inicial e avança o timer."""
        if not self.video_frame_paths:
            self.screen.fill(PALETTE.background)
            return
        self.video_frame_timer += 1
        if self.video_frame_timer >= 2:
            self.video_frame_timer = 0
            self.video_frame_index = (self.video_frame_index + 1) % len(self.video_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.video_frame_paths, self.video_frame_index), (0, 0))

    def _renderizar_fundo_hub(self):
        """Blita o frame atual da animação de fundo do hub e avança o timer."""
        if not self.hub_frame_paths:
            self.screen.fill((20, 40, 20))
            return
        self.hub_frame_timer += 1
        if self.hub_frame_timer >= 2:
            self.hub_frame_timer = 0
            self.hub_frame_index = (self.hub_frame_index + 1) % len(self.hub_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.hub_frame_paths, self.hub_frame_index), (0, 0))

    def _renderizar_fundo_perfil(self):
        """Blita o frame atual da animação de fundo do perfil e avança o timer."""
        if not self.perfil_frame_paths:
            self.screen.fill((11, 25, 11))
            return
        self.perfil_frame_timer += 1
        if self.perfil_frame_timer >= 2:
            self.perfil_frame_timer = 0
            self.perfil_frame_index = (self.perfil_frame_index + 1) % len(self.perfil_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.perfil_frame_paths, self.perfil_frame_index), (0, 0))

    def _renderizar_fundo_mundos(self):
        """Blita o frame atual da animação de fundo da tela de mundos e avança o timer."""
        if not self.mundos_frame_paths:
            self.screen.fill((20, 40, 20))
            return
        self.mundos_frame_timer += 1
        if self.mundos_frame_timer >= 2:
            self.mundos_frame_timer = 0
            self.mundos_frame_index = (self.mundos_frame_index + 1) % len(self.mundos_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.mundos_frame_paths, self.mundos_frame_index), (0, 0))

    def _renderizar_inicio(self):
        """Renderiza o overlay, título "CodeQuest" com glow pulsante e subtítulo da tela inicial."""
        self.screen.blit(self.start_overlay, (0, 0))

        # Titulo renderizado letra por letra com espaçamento manual uniforme
        _TITULO = "CodeQuest"
        _GAP = 2  # pixels extras entre caracteres alem da largura individual
        _char_w = [self.font_title_large.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title_large.get_height()
        _tcy = 270  # centro vertical do titulo

        # Glow verde pulsante por tras do titulo
        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title_large.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        # Sombra do titulo (offset +3px)
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title_large.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        # Titulo principal branco
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title_large.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        # Subtitulo com sombra nas letras deslocada 2px
        _subtitulo = "Uma Jornada pelo Arquipélago de Bythos"
        _sub_som = self.font_subtitle_small.render(_subtitulo, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 327)))
        _sub_surf = self.font_subtitle_small.render(_subtitulo, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 325)))

        if self.status_kind in {"success", "error"}:
            self._desenhar_status(600)

    def _renderizar_criacao(self):
        """Renderiza o título "Criar personagem" com glow e os campos nome/idade."""
        _TITULO = "Criar personagem"
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 120

        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "Defina quem vai explorar Bythos"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 187)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 185)))

        _lbl = self.font_credit_body_bold.render("Nome do aventureiro", True, _BRANCO)
        self.screen.blit(_lbl, (390, 252))
        self._desenhar_input_verde(pygame.Rect(390, 285, 500, 50), self.nome_input, "nome", "Digite seu nome")

        _lbl = self.font_credit_body_bold.render("Idade", True, _BRANCO)
        self.screen.blit(_lbl, (390, 352))
        self._desenhar_input_verde(pygame.Rect(390, 385, 220, 50), self.idade_input, "idade", "18")

        if self.status_kind in {"success", "error"}:
            self._desenhar_status_hub(610)

    def _renderizar_hub(self):
        """Renderiza o hub com overlay, título "Menu de Jornada", saudação ao jogador e status."""
        self.screen.blit(self.hub_overlay, (0, 0))

        nome = self.usuario.nome if self.usuario else "Aventureiro"

        _TITULO = "Menu de Jornada"
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 255

        self.hub_glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.hub_glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = f"Bem-vindo, {nome}"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 327)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 325)))

        if self.status_kind in {"success", "error"}:
            self._desenhar_status_hub(665)

    def _desenhar_status_hub(self, y):
        """Desenha feedback centralizado para telas de hub e criacao.

        Usa banner verde para sucesso e texto vermelho com sombra para erro,
        mantendo o aviso de erro visualmente separado dos botoes.

        Recebe:
            y (int): Coordenada vertical do centro do feedback.
        """
        color = PALETTE.success if self.status_kind == "success" else PALETTE.error
        font = self.font_hub_subtitle if self.status_kind == "error" else self.font_status_success
        linhas = quebrar_texto(self.status_message, font, WINDOW.width - 200)
        linha_altura = font.get_linesize()
        if self.status_kind == "error":
            texto_y = y - (len(linhas) * linha_altura) // 2
            for linha in linhas:
                sombra = font.render(linha, True, (0, 0, 0))
                self.screen.blit(sombra, sombra.get_rect(center=(WINDOW.width // 2 + 2, texto_y + linha_altura // 2 + 2)))
                surface = font.render(linha, True, color)
                self.screen.blit(surface, surface.get_rect(center=(WINDOW.width // 2, texto_y + linha_altura // 2)))
                texto_y += linha_altura
            return

        max_w = max(font.size(l)[0] for l in linhas)
        box_w = min(max_w + 56, WINDOW.width - 170)
        altura = max(48, len(linhas) * linha_altura + 16)
        rect = pygame.Rect(WINDOW.width // 2 - box_w // 2, y - altura // 2, box_w, altura)
        pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, width=2, border_radius=10)
        texto_y = rect.y + 8
        for linha in linhas:
            sombra = font.render(linha, True, (0, 0, 0))
            self.screen.blit(sombra, sombra.get_rect(center=(rect.centerx + 2, texto_y + linha_altura // 2 + 2)))
            surface = font.render(linha, True, _BRANCO)
            self.screen.blit(surface, surface.get_rect(center=(rect.centerx, texto_y + linha_altura // 2)))
            texto_y += linha_altura

    def _renderizar_mundos(self):
        """Renderiza a tela de seleção de mundos com fundo animado, título com glow e caixa de aviso."""
        self.screen.blit(self.mundos_overlay, (0, 0))

        _TITULO = "Arquipelago de Bythos"
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 175

        self.mundos_glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.mundos_glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "Escolha o próximo destino"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 242)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 240)))

        # Caixa de aviso com a mensagem de status
        _aviso_font = self.font_status_success
        _aviso_linhas = []
        for _parte in self.status_message.splitlines():
            _aviso_linhas.extend(quebrar_texto(_parte, _aviso_font, WINDOW.width - 340))
        _lh = _aviso_font.get_linesize()
        _pad = 12
        _aviso_h = len(_aviso_linhas) * _lh + _pad * 2
        _aviso_w = min(max(_aviso_font.size(l)[0] for l in _aviso_linhas) + 56, WINDOW.width - 300)
        _aviso_rect = pygame.Rect(WINDOW.width // 2 - _aviso_w // 2, 548, _aviso_w, _aviso_h)
        _cor_borda_aviso = _VERDE_CLARO
        if self.status_kind == "success":
            _cor_borda_aviso = PALETTE.success
        elif self.status_kind == "error":
            _cor_borda_aviso = PALETTE.error
        pygame.draw.rect(self.screen, (20, 55, 30), _aviso_rect, border_radius=10)
        pygame.draw.rect(self.screen, _cor_borda_aviso, _aviso_rect, width=2, border_radius=10)
        _ty = _aviso_rect.y + _pad
        for _l in _aviso_linhas:
            _ss = _aviso_font.render(_l, True, (0, 0, 0))
            self.screen.blit(_ss, _ss.get_rect(center=(_aviso_rect.centerx + 1, _ty + _lh // 2 + 1)))
            _ss = _aviso_font.render(_l, True, _BRANCO)
            self.screen.blit(_ss, _ss.get_rect(center=(_aviso_rect.centerx, _ty + _lh // 2)))
            _ty += _lh

    def _renderizar_perfil(self):
        """Renderiza o perfil do usuário com quatro cards de estatísticas e seção de conquistas."""
        self.screen.blit(self.perfil_overlay, (0, 0))

        self.usuario = carregar_usuario()
        if self.usuario is None:
            self._desenhar_paragrafo("Nenhum personagem criado ainda.", 360, 300, 560, self.font_body, PALETTE.text)
            return

        _TITULO = self.usuario.nome
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 120

        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "Seu progresso em Bythos"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 187)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 185)))

        _CW, _CH = 280, 140
        _HGAP, _VGAP = 40, 25
        _GX = WINDOW.width // 2 - (_CW * 2 + _HGAP) // 2
        _GY = 230
        _COR_FUNDO = (30, 80, 50)
        _COR_BORDA = (100, 200, 120)

        cards = [
            ("Nível", str(self.usuario.nivel)),
            ("XP Total", str(self.usuario.xp)),
            ("Prox. Nível", str(xp_para_proximo_nivel(self.usuario.xp))),
            ("Idade", str(self.usuario.idade)),
        ]
        for idx, (label, valor) in enumerate(cards):
            col = idx % 2
            row = idx // 2
            cx = _GX + col * (_CW + _HGAP)
            cy = _GY + row * (_CH + _VGAP)
            rect = pygame.Rect(cx, cy, _CW, _CH)
            pygame.draw.rect(self.screen, _COR_FUNDO, rect, border_radius=12)
            pygame.draw.rect(self.screen, _COR_BORDA, rect, width=2, border_radius=12)
            _lbl_surf = self.font_profile_label.render(label, True, _COR_BORDA)
            self.screen.blit(_lbl_surf, _lbl_surf.get_rect(center=(cx + _CW // 2, cy + 36)))
            _val_surf = self.font_profile_value.render(valor, True, _BRANCO)
            self.screen.blit(_val_surf, _val_surf.get_rect(center=(cx + _CW // 2, cy + 96)))

        _sect_y = _GY + 2 * (_CH + _VGAP)
        _sect_rect = pygame.Rect(_GX, _sect_y, _CW * 2 + _HGAP, 100)
        pygame.draw.rect(self.screen, _COR_FUNDO, _sect_rect, border_radius=12)
        pygame.draw.rect(self.screen, _COR_BORDA, _sect_rect, width=2, border_radius=12)
        _conq_lbl = self.font_profile_label.render("Conquistas", True, _COR_BORDA)
        self.screen.blit(_conq_lbl, _conq_lbl.get_rect(center=(_sect_rect.centerx, _sect_rect.y + 28)))
        _em_breve = self.font_profile_value.render("EM BREVE", True, _COR_BORDA)
        self.screen.blit(_em_breve, _em_breve.get_rect(center=(_sect_rect.centerx, _sect_rect.y + 68)))

    def _renderizar_cutscene(self):
        """Renderiza a cena atual da cutscene com três estados de fade.

        Estados:
        - "fade_out_entry": hub escurece para preto (único fade — ocorre só na entrada).
        - "fade_in": primeira cena aparece saindo do preto.
        - "visible": cena visível, transições entre cenas são instantâneas.

        Renderiza: fundo imagem_cut.jpeg com overlay escuro; imagem principal 960×400
        centralizada com glow pulsante e borda arredondada; caixa de texto estilo
        alerta abaixo da imagem; caixa-contador no canto inferior esquerdo; botões
        "Pular história" e "Avançar →" lado a lado no canto inferior direito.
        """
        _FADE_SPEED = 8
        _IMG_W, _IMG_H = 900, 500
        _IMG_X = (WINDOW.width - _IMG_W) // 2
        _IMG_Y = 50
        _BTN_W, _BTN_H = 190, 45
        _BTN_Y = WINDOW.height - 65
        _BTN2_X = WINDOW.width - 20 - _BTN_W
        _BTN1_X = _BTN2_X - 10 - _BTN_W
        _ARROW_RECT = pygame.Rect(_BTN2_X, _BTN_Y, _BTN_W, _BTN_H)
        _PULAR_RECT = pygame.Rect(_BTN1_X, _BTN_Y, _BTN_W, _BTN_H)

        # Fase de entrada: hub escurecendo para preto — único fade do modo cutscene
        if self.cutscene_fade_state == "fade_out_entry":
            if self._cutscene_prev_frame:
                self.screen.blit(self._cutscene_prev_frame, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            self.cutscene_fade_alpha = min(255, self.cutscene_fade_alpha + _FADE_SPEED)
            _ov = pygame.Surface((WINDOW.width, WINDOW.height))
            _ov.fill((0, 0, 0))
            _ov.set_alpha(self.cutscene_fade_alpha)
            self.screen.blit(_ov, (0, 0))
            if self.cutscene_fade_alpha >= 255:
                self.cutscene_fade_state = "fade_in"
                self.cutscene_fade_alpha = 255
            return

        # Fundo: imagem_cut.jpeg escalada + overlay escuro semitransparente
        if self.cutscene_bg:
            self.screen.blit(self.cutscene_bg, (0, 0))
            _bg_ov = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
            _bg_ov.fill((0, 0, 0, 150))
            self.screen.blit(_bg_ov, (0, 0))
        else:
            self.screen.fill((11, 25, 11))

        # Glow pulsante ao redor da imagem principal
        _gt = pygame.time.get_ticks()
        _g_a = int(40 + 60 * abs(math.sin(_gt * 0.0015)))
        _glow_surf = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        for _sp, _fa in ((16, max(0, _g_a // 5)), (10, max(0, _g_a // 3)), (5, max(0, _g_a // 2))):
            pygame.draw.rect(
                _glow_surf, (*_VERDE_CLARO, _fa),
                pygame.Rect(_IMG_X - _sp, _IMG_Y - _sp, _IMG_W + _sp * 2, _IMG_H + _sp * 2),
                border_radius=12 + _sp,
            )
        self.screen.blit(_glow_surf, (0, 0))

        # Imagem principal com máscara e borda arredondadas para esconder quinas.
        _img = self.cutscene_images[self.cutscene_index] if self.cutscene_index < len(self.cutscene_images) else None
        if _img:
            _img_round = pygame.Surface((_IMG_W, _IMG_H), pygame.SRCALPHA)
            _img_round.blit(_img, (0, 0))
            _mask = pygame.Surface((_IMG_W, _IMG_H), pygame.SRCALPHA)
            pygame.draw.rect(_mask, _BRANCO, _mask.get_rect(), border_radius=16)
            _img_round.blit(_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(_img_round, (_IMG_X, _IMG_Y))
        else:
            pygame.draw.rect(self.screen, (20, 50, 30), pygame.Rect(_IMG_X, _IMG_Y, _IMG_W, _IMG_H), border_radius=16)
        pygame.draw.rect(
            self.screen, _VERDE_CLARO,
            pygame.Rect(_IMG_X, _IMG_Y, _IMG_W, _IMG_H),
            width=6, border_radius=16,
        )

        # Caixa de texto estilo alerta abaixo da imagem
        _font = self.font_cutscene_text
        _text_max_w = _IMG_W - 56
        _linhas = quebrar_texto(CUTSCENE_TEXTS[self.cutscene_index], _font, _text_max_w)
        _lh = _font.get_linesize() + 2
        _pad = 14
        _box_h = len(_linhas) * _lh + _pad * 2
        _box_top = _IMG_Y + _IMG_H + 14
        _box_rect = pygame.Rect(_IMG_X, _box_top, _IMG_W, _box_h)
        pygame.draw.rect(self.screen, (20, 55, 30), _box_rect, border_radius=10)
        pygame.draw.rect(self.screen, _VERDE_CLARO, _box_rect, width=2, border_radius=10)
        _ty = _box_top + _pad
        _text_x = _box_rect.x + 28
        for _l in _linhas:
            _sombra = _font.render(_l, True, (0, 0, 0))
            self.screen.blit(_sombra, (_text_x + 1, _ty + 1))
            _surf = _font.render(_l, True, _BRANCO)
            self.screen.blit(_surf, (_text_x, _ty))
            _ty += _lh

        # Caixa-contador estilo alerta no canto inferior esquerdo
        _cnt_text = f"{self.cutscene_index + 1} / {len(CUTSCENE_TEXTS)}"
        _cnt_font = self.font_credit_section
        _cnt_w = _cnt_font.size(_cnt_text)[0] + 40
        _cnt_rect = pygame.Rect(20, _BTN_Y, _cnt_w, _BTN_H)
        pygame.draw.rect(self.screen, (20, 55, 30), _cnt_rect, border_radius=8)
        pygame.draw.rect(self.screen, _VERDE_CLARO, _cnt_rect, width=2, border_radius=8)
        _cnt_surf = _cnt_font.render(_cnt_text, True, _BRANCO)
        self.screen.blit(_cnt_surf, _cnt_surf.get_rect(center=_cnt_rect.center))

        # Botões "Pular história" e "Avançar →" lado a lado no canto inferior direito
        _mouse = pygame.mouse.get_pos()
        for _rect, _label in ((_PULAR_RECT, "Pular história"), (_ARROW_RECT, "Avançar →")):
            _hov = _rect.collidepoint(_mouse) and self.cutscene_fade_state == "visible"
            pygame.draw.rect(self.screen, _BRANCO if _hov else _VERDE, _rect, border_radius=8)
            pygame.draw.rect(self.screen, _VERDE_CLARO, _rect, width=2, border_radius=8)
            _b_surf = self.font_start_btn.render(_label, True, _VERDE if _hov else _BRANCO)
            self.screen.blit(_b_surf, _b_surf.get_rect(center=_rect.center))

        # Fade de entrada saindo do preto
        if self.cutscene_fade_state == "fade_in":
            self.cutscene_fade_alpha = max(0, self.cutscene_fade_alpha - _FADE_SPEED)
            if self.cutscene_fade_alpha == 0:
                self.cutscene_fade_state = "visible"

        if self.cutscene_fade_alpha > 0:
            _ov = pygame.Surface((WINDOW.width, WINDOW.height))
            _ov.fill((0, 0, 0))
            _ov.set_alpha(self.cutscene_fade_alpha)
            self.screen.blit(_ov, (0, 0))

    def _renderizar_creditos(self):
        """Renderiza os créditos com seções estilizadas, título CodeQuest com glow e fundo animado."""
        if self.creditos_frame_paths:
            self.creditos_frame_timer += 1
            if self.creditos_frame_timer >= 6:
                self.creditos_frame_timer = 0
                self.creditos_frame_index = (self.creditos_frame_index + 1) % len(self.creditos_frame_paths)
            self.screen.blit(self._obter_frame_animado(self.creditos_frame_paths, self.creditos_frame_index), (0, 0))
            _cred_ov = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
            _cred_ov.fill((0, 0, 0, 120))
            self.screen.blit(_cred_ov, (0, 0))

        _COR_BORDA = (100, 200, 120)
        _COR_PLACA = (0, 0, 0, 178)
        _MARG = 100
        _CW = WINDOW.width - _MARG * 2
        _ft_titulo = self.font_lesson_title
        _ft_sub = self.font_hub_subtitle
        _ft_body = self.font_lesson_content
        _LH_SUB = _ft_sub.get_linesize() + 2
        _LH_BODY = _ft_body.get_linesize() + 4
        _ESPACO_SECAO = 40

        _secoes = [
            ("EQUIPE DE DESENVOLVIMENTO", [
                ("sub",   "Neto  —  Backend e Persistência"),
                ("body",  "Sistema de XP, SQLite, organização de dados e arquitetura."),
                ("space", ""),
                ("sub",   "Anthony  —  Interface e Experiência"),
                ("body",  "Telas Pygame, navegação, estilo visual e polimento de interação."),
                ("space", ""),
                ("sub",   "Mayanderson  —  Conteúdo e Pedagogia"),
                ("body",  "Aulas, exercícios, progressão pedagógica, narrativa e revisão."),
            ]),
            ("INSTITUIÇÃO E DISCIPLINA", [
                ("sub",  "Universidade Federal de Alagoas (UFAL)"),
                ("body", "Curso: Ciência da Computação — 1° Período"),
                ("body", "Disciplina: Algoritmos e Programação de Computadores"),
                ("body", "Professor: Alexandre Barbosa"),
            ]),
            ("TECNOLOGIAS UTILIZADAS", [
                ("body", "Python  |  Pygame  |  SQLite  |  Pytest  |  Git e GitHub"),
            ]),
            ("AGRADECIMENTOS", [
                ("body", "Ao Professor Alexandre Barbosa pela orientação ao longo da disciplina."),
                ("body", "Aos colegas que testaram o jogo e ajudaram com feedback."),
            ]),
            ("MENSAGEM FINAL", [
                ("body",  "Este projeto foi desenvolvido por Mayanderson, Neto e Anthony, alunos do primeiro período da UFAL."),
                ("space", ""),
                ("body",  "Obrigado por embarcar nessa jornada pelo Arquipélago de Bythos."),
                ("space", ""),
                ("body",  "Que o CodeQuest ajude a acender sua curiosidade por programação."),
            ]),
            ("DATA", [
                ("body", "Maio — Junho de 2025"),
            ]),
            ("LINKS", [
                ("body", "github.com/netojoseluizferreira-sys/CodeQuest"),
            ]),
        ]

        def _plate_h(titulo):
            return _ft_titulo.get_height() + 16

        def _secao_h(linhas, titulo):
            h = _plate_h(titulo) + 14
            for style, text in linhas:
                if style == "sub":
                    h += len(quebrar_texto(text, _ft_sub, _CW)) * _LH_SUB
                elif style == "body":
                    h += len(quebrar_texto(text, _ft_body, _CW)) * _LH_BODY
                elif style == "space":
                    h += 14
            return h

        def _desenhar_secao_titulo(ty, titulo):
            _ts = _ft_titulo.render(titulo, True, _BRANCO)
            _ph = _ft_titulo.get_height() + 16
            _pw = _ts.get_width() + 48
            _pr = pygame.Rect(0, 0, _pw, _ph)
            _pr.center = (WINDOW.width // 2, ty + _ph // 2)
            _pbg = pygame.Surface((_pw, _ph), pygame.SRCALPHA)
            _pbg.fill(_COR_PLACA)
            self.screen.blit(_pbg, _pr.topleft)
            pygame.draw.rect(self.screen, _COR_BORDA, _pr, width=2, border_radius=8)
            _shadow = _ft_titulo.render(titulo, True, (0, 0, 0))
            self.screen.blit(_shadow, _shadow.get_rect(center=(_pr.centerx + 2, _pr.centery + 2)))
            self.screen.blit(_ts, _ts.get_rect(center=_pr.center))
            return _ph

        _AREA_TOP = 112
        _AREA_BOTTOM = WINDOW.height - 90
        self.screen.set_clip(pygame.Rect(0, _AREA_TOP, WINDOW.width, _AREA_BOTTOM - _AREA_TOP))

        y = _AREA_TOP + 12 - self.credit_scroll
        for _titulo_sec, _linhas in _secoes:
            _sh = _secao_h(_linhas, _titulo_sec)
            if y + _sh >= _AREA_TOP and y <= _AREA_BOTTOM:
                _ph = _desenhar_secao_titulo(y, _titulo_sec)
                _ty = y + _ph + 14
                for style, text in _linhas:
                    if style == "sub":
                        for _sub in quebrar_texto(text, _ft_sub, _CW):
                            _ss = _ft_sub.render(_sub, True, (0, 0, 0))
                            self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2 + 2, _ty + _LH_SUB // 2 + 2)))
                            _ss = _ft_sub.render(_sub, True, _BRANCO)
                            self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2, _ty + _LH_SUB // 2)))
                            _ty += _LH_SUB
                    elif style == "body":
                        for _sub in quebrar_texto(text, _ft_body, _CW):
                            self.screen.blit(_ft_body.render(_sub, True, _BRANCO), (_MARG, _ty))
                            _ty += _LH_BODY
                    elif style == "space":
                        _ty += 14
            y += _sh + _ESPACO_SECAO

        self.screen.set_clip(None)

        # Título "CodeQuest" com glow verde pulsante e nameplate — desenhado por cima das seções
        _TITULO = "CodeQuest"
        _GAP = 2
        _char_w = [self.font_title_large.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title_large.get_height()
        _tcy = 52

        _title_rect = pygame.Rect(0, 0, _total_w + 72, _char_h + 28)
        _title_rect.center = (WINDOW.width // 2, _tcy)
        _title_bg = pygame.Surface(_title_rect.size, pygame.SRCALPHA)
        _title_bg.fill(_COR_PLACA)
        self.screen.blit(_title_bg, _title_rect.topleft)
        pygame.draw.rect(self.screen, _COR_BORDA, _title_rect, width=2, border_radius=10)

        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title_large.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(self.font_title_large.render(_c, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(self.font_title_large.render(_c, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP


    def _renderizar_fluxo_aprendizado(self):
        """Despacha para _renderizar_segmento_aula ou _renderizar_segmento_exercicio conforme o segmento atual."""
        segmento = self._segmento_atual()
        if segmento is None:
            self.screen_name = "complete"
            return
        if segmento["tipo"] == "aula":
            self._renderizar_segmento_aula(segmento)
        else:
            self._renderizar_segmento_exercicio(segmento)

    def _renderizar_segmento_aula(self, segmento):
        """Renderiza um segmento de aula sobre fundo imagem_cut com título glow, conteúdo e link YouTube."""
        # Fundo: imagem_cut redimensionada + camada escura alpha 160
        if self.cutscene_bg:
            self.screen.blit(self.cutscene_bg, (0, 0))
        else:
            self.screen.fill((11, 25, 11))
        self.screen.blit(self.lesson_overlay, (0, 0))

        # Título PressStart2P com glow verde pulsante (igual à tela inicial)
        _TITULO = segmento["titulo"]
        _GAP = 2
        _ft = self.font_lesson_title
        _char_w = [_ft.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = _ft.get_height()
        _tcy = 52

        self.lesson_glow_timer += 1
        _ga = int(40 + 80 * abs(math.sin(self.lesson_glow_timer * 0.04)))
        _gs = [_ft.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _gs:
            _s.set_alpha(_ga)
        for _sp in (8, 5, 2):
            for _dx in (-_sp, 0, _sp):
                for _dy in (-_sp, 0, _sp):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_gs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft.render(_c, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft.render(_c, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        # Subtítulo "Aula X: [nome da aula]" em RammettoOne branco com sombra preta
        _sub = self.aula["titulo"]
        _sub_y = _tcy + _char_h // 2 + 42
        _fes = self.font_hub_subtitle
        _ss = _fes.render(_sub, True, (0, 0, 0))
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2 + 2, _sub_y + 2)))
        _ss = _fes.render(_sub, True, _BRANCO)
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2, _sub_y)))

        # Corpo WendyOne em painel de leitura, com respiro e divisao em colunas quando necessario.
        _MARG = 118
        _cw = WINDOW.width - _MARG * 2
        _fc = self.font_lesson_body
        _lh = _fc.get_linesize() + 2
        _body_top = _sub_y + _fes.get_height() // 2 + 32
        _has_cta = MUNDO_ATIVO == "mundo_1" and segmento.get("id") == "texto_1"
        _conteudo = segmento["conteudo"]
        if len(_conteudo) > 4:
            _meio = math.ceil(len(_conteudo) / 2)
            _colunas = [_conteudo[:_meio], _conteudo[_meio:]]
        else:
            _colunas = [_conteudo]

        _gap_col = 38 if len(_colunas) > 1 else 0
        _col_w = (_cw - _gap_col) // len(_colunas)
        _col_heights = []
        for _paragrafos in _colunas:
            _altura_coluna = 0
            for _para in _paragrafos:
                _altura_coluna += len(quebrar_texto(_para, _fc, _col_w - 18)) * _lh + 12
            _col_heights.append(max(0, _altura_coluna - 12))

        _panel_max_bottom = WINDOW.height - (250 if _has_cta else 118)
        _panel_h = min(max(max(_col_heights, default=0) + 36, 300), _panel_max_bottom - (_body_top - 18))
        _panel_rect = pygame.Rect(_MARG - 18, _body_top - 18, _cw + 36, _panel_h)
        _panel = pygame.Surface(_panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(_panel, (0, 0, 0, 118), _panel.get_rect(), border_radius=8)
        pygame.draw.rect(_panel, (*_VERDE_CLARO, 130), _panel.get_rect(), width=2, border_radius=8)
        self.screen.blit(_panel, _panel_rect.topleft)

        _max_y = _panel_rect.bottom - 18
        for _col_idx, _paragrafos in enumerate(_colunas):
            _x = _MARG + _col_idx * (_col_w + _gap_col)
            _y = _body_top
            for _para in _paragrafos:
                _linhas = quebrar_texto(_para, _fc, _col_w - 18)
                _accent_h = min(len(_linhas) * _lh - 4, _max_y - _y)
                if _accent_h > 0:
                    pygame.draw.rect(self.screen, _VERDE_CLARO, pygame.Rect(_x, _y + 4, 4, _accent_h), border_radius=2)
                for _linha in _linhas:
                    if _y + _lh > _max_y:
                        break
                    _shadow = _fc.render(_linha, True, (0, 0, 0))
                    self.screen.blit(_shadow, (_x + 16 + 2, _y + 2))
                    self.screen.blit(_fc.render(_linha, True, _BRANCO), (_x + 16, _y))
                    _y += _lh
                _y += 12
                if _y >= _max_y:
                    break

        # Mensagem CTA e link YouTube (apenas mundo_1 / texto_1)
        if _has_cta:
            _cta_font = self.font_status_success
            _cta_lines = [
                "Quer se aprofundar um pouco mais no tema?",
                "Clica no link abaixo e assista a uma aula completa!",
            ]
            _cta_lh = _cta_font.get_linesize() + 2
            _ltxt = "Assistir Aula Completa (YouTube)"
            _lsurf = self.font_lesson_content.render(_ltxt, True, _VERDE_CLARO)
            _cta_h = len(_cta_lines) * _cta_lh + _lsurf.get_height() + 44
            _cta_content_w = max([_cta_font.size(_linha)[0] for _linha in _cta_lines] + [_lsurf.get_width()])
            _cta_w = min(_cw + 36, _cta_content_w + 92)
            _cta_rect = pygame.Rect(WINDOW.width // 2 - _cta_w // 2, _panel_rect.bottom + 18, _cta_w, _cta_h)
            _cta = pygame.Surface(_cta_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(_cta, (0, 0, 0, 112), _cta.get_rect(), border_radius=8)
            pygame.draw.rect(_cta, (*_VERDE_CLARO, 150), _cta.get_rect(), width=2, border_radius=8)
            self.screen.blit(_cta, _cta_rect.topleft)

            _cy = _cta_rect.y + 14
            for _cl in _cta_lines:
                _txt_shadow = _cta_font.render(_cl, True, (0, 0, 0))
                _txt_surf = _cta_font.render(_cl, True, _VERDE_CLARO)
                self.screen.blit(_txt_shadow, _txt_shadow.get_rect(center=(WINDOW.width // 2 + 2, _cy + _cta_lh // 2 + 2)))
                self.screen.blit(_txt_surf, _txt_surf.get_rect(center=(WINDOW.width // 2, _cy + _cta_lh // 2)))
                _cy += _cta_lh

            self.link_rect = _lsurf.get_rect(center=(WINDOW.width // 2, _cy + _lsurf.get_height() // 2 + 4))
            self.screen.blit(_lsurf, self.link_rect)
            pygame.draw.line(
                self.screen, _VERDE_CLARO,
                (self.link_rect.left, self.link_rect.bottom),
                (self.link_rect.right, self.link_rect.bottom),
                2,
            )
        else:
            self.link_rect = None

        self.btn_continuar_y = None

    def _renderizar_segmento_exercicio(self, segmento):
        """Renderiza o exercício atual dentro de um bloco de prática.

        Exibe cabeçalho com contador "X de Y", pergunta do exercício, campo de
        resposta ou alternativas (via botões em _botoes_fluxo_aprendizado) e
        banner de status.

        Recebe:
            segmento (dict): Segmento de tipo "exercicios" com chaves "titulo"
            e "exercicios" (list[str] de IDs).
        """
        self.link_rect = None  # Evita clique fantasma em botoes de link que sumiram
        exercicio = self._exercicio_atual()
        numero = self.exercicio_indice + 1
        total = len(segmento["exercicios"])
        self._desenhar_cabecalho(segmento["titulo"], f"Exercicio {numero} de {total}")
        if exercicio is None:
            self._desenhar_paragrafo("Exercicio nao encontrado.", self.content_x, 250, self.content_width, self.font_body, PALETTE.text)
            return

        self._desenhar_paragrafo(exercicio["pergunta"], self.content_x, 205, self.content_width, self.font_body, PALETTE.text)
        if exercicio["tipo"] != "multipla_escolha":
            placeholder = exercicio.get("placeholder", "Digite sua resposta")
            self._desenhar_input(pygame.Rect(self.content_x, 455, self.content_width, 52), self.resposta_texto, "resposta", placeholder)

        self._desenhar_status(WINDOW.height - 118)

    def _renderizar_conclusao(self):
        """Renderiza a tela de conclusão exibida ao final de todos os segmentos da aula."""
        self._desenhar_cabecalho("Aula concluida", "A primeira rota de Bythos foi vencida")
        self._desenhar_paragrafo(
            "Voce completou o fluxo de texto, pratica e revisao. Volte ao menu para ver seu perfil.",
            300,
            300,
            680,
            self.font_body,
            PALETTE.text,
        )

    def _desenhar_cabecalho(self, titulo, subtitulo):
        """Desenha o cabeçalho padrão de 170px com título e subtítulo centralizados.

        Recebe:
            titulo (str): Texto principal renderizado com font_title.
            subtitulo (str): Texto secundário renderizado com font_subtitle em cor accent.
        """
        pygame.draw.rect(self.screen, PALETTE.surface, pygame.Rect(0, 0, WINDOW.width, 170))
        pygame.draw.line(self.screen, PALETTE.border, (0, 170), (WINDOW.width, 170), 2)
        desenhar_texto_centralizado(self.screen, titulo, self.font_title, PALETTE.text, 68)
        desenhar_texto_centralizado(self.screen, subtitulo, self.font_subtitle, PALETTE.accent, 120)

    def _desenhar_label(self, texto, x, y):
        """Renderiza um rótulo de formulário com font_small na cor muted.

        Recebe:
            texto (str): Texto do rótulo.
            x (int): Coordenada horizontal do canto superior esquerdo.
            y (int): Coordenada vertical do canto superior esquerdo.
        """
        self.screen.blit(self.font_small.render(texto, True, PALETTE.muted), (x, y))

    def _desenhar_input(self, rect, valor, campo, placeholder):
        """Renderiza um campo de texto com estilo escuro padrão.

        Destaca a borda em accent quando o campo estiver ativo; mostra
        placeholder em cor muted quando valor for vazio.

        Recebe:
            rect (pygame.Rect): Posição e tamanho do campo.
            valor (str): Texto digitado atualmente.
            campo (str): Nome interno do campo para comparação com self.active_field.
            placeholder (str): Texto exibido quando valor for vazio.
        """
        ativo = self.active_field == campo
        cor_borda = PALETTE.accent if ativo else PALETTE.border
        pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=8)
        pygame.draw.rect(self.screen, cor_borda, rect, width=2, border_radius=8)
        texto = valor or placeholder
        cor = PALETTE.text if valor else PALETTE.muted
        self.screen.blit(self.font_body.render(texto, True, cor), (rect.x + 14, rect.y + 10))

    def _desenhar_input_verde(self, rect, valor, campo, placeholder):
        """Renderiza um campo de texto com estilo verde escuro para telas de fundo verde.

        Análogo a _desenhar_input mas com paleta _VERDE/_VERDE_CLARO em vez de PALETTE.

        Recebe:
            rect (pygame.Rect): Posição e tamanho do campo.
            valor (str): Texto digitado atualmente.
            campo (str): Nome interno do campo para comparação com self.active_field.
            placeholder (str): Texto exibido quando valor for vazio.
        """
        ativo = self.active_field == campo
        cor_borda = _VERDE_CLARO if ativo else _VERDE
        pygame.draw.rect(self.screen, (15, 35, 15), rect, border_radius=8)
        pygame.draw.rect(self.screen, cor_borda, rect, width=2, border_radius=8)
        texto = valor or placeholder
        cor = _BRANCO if valor else (100, 150, 100)
        self.screen.blit(self.font_body.render(texto, True, cor), (rect.x + 14, rect.y + 10))

    def _desenhar_paragrafo(self, texto, x, y, largura, font, color):
        """Renderiza um bloco de texto quebrado em múltiplas linhas.

        Recebe:
            texto (str): Conteúdo textual a renderizar.
            x (int): Margem esquerda em pixels.
            y (int): Coordenada vertical inicial.
            largura (int): Largura máxima disponível em pixels.
            font (pygame.font.Font): Fonte usada na renderização.
            color (tuple[int, int, int]): Cor RGB do texto.

        Retorna:
            int: Coordenada y imediatamente após o último pixel do bloco de texto.
        """
        linha_altura = font.get_linesize() + 4
        for linha in quebrar_texto(texto, font, largura):
            self.screen.blit(font.render(linha, True, color), (x, y))
            y += linha_altura
        return y

    def _desenhar_status(self, y):
        """Renderiza o banner de status quando status_kind for "success" ou "error".

        Para "normal", exibe apenas o texto em cor muted. Para "success", desenha
        um retangulo com borda verde. Para "error", usa apenas texto vermelho com
        sombra, evitando que o aviso pareca um botao clicavel.

        Recebe:
            y (int): Coordenada vertical central do banner.
        """
        if self.status_kind in {"success", "error"}:
            color = PALETTE.success if self.status_kind == "success" else PALETTE.error
            font = self.font_hub_subtitle if self.status_kind == "error" else self.font_body
            linhas = quebrar_texto(self.status_message, font, self.content_width - 80)
            linha_altura = font.get_linesize()
            if self.status_kind == "error":
                texto_y = y - (len(linhas) * linha_altura) // 2
                for linha in linhas:
                    sombra = font.render(linha, True, (0, 0, 0))
                    self.screen.blit(sombra, sombra.get_rect(center=(WINDOW.width // 2 + 2, texto_y + linha_altura // 2 + 2)))
                    surface = font.render(linha, True, color)
                    self.screen.blit(surface, surface.get_rect(center=(WINDOW.width // 2, texto_y + linha_altura // 2)))
                    texto_y += linha_altura
                return

            altura = max(58, (len(linhas) * linha_altura) + 24)
            rect = pygame.Rect(self.content_x, y - altura // 2, self.content_width, altura)
            pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=10)
            pygame.draw.rect(self.screen, color, rect, width=2, border_radius=10)
            texto_y = rect.y + 12
            for linha in linhas:
                surface = font.render(linha, True, color)
                surface_rect = surface.get_rect(center=(rect.centerx, texto_y + linha_altura // 2))
                self.screen.blit(surface, surface_rect)
                texto_y += linha_altura
            return

        desenhar_texto_centralizado(self.screen, self.status_message, self.font_tiny, PALETTE.muted, y)

    def _definir_status(self, mensagem, kind="normal"):
        """Atualiza a mensagem de status e seu estilo visual exibido por _desenhar_status.

        Recebe:
            mensagem (str): Texto a exibir.
            kind (str): "normal" (texto muted), "success" (borda verde) ou "error" (borda vermelha).
        """
        self.status_message = mensagem
        self.status_kind = kind

    def _novo_jogo(self):
        """Reseta o banco de dados, limpa o estado do usuário e navega para a criação de personagem."""
        resetar_banco_de_dados()
        self.usuario = None
        self.nome_input = ""
        self.idade_input = ""
        self.active_field = "nome"
        self._definir_status("Crie seu personagem para comecar uma nova jornada.")
        self.screen_name = "create"

    def _continuar(self):
        """Carrega o save existente ou direciona o jogador para criar perfil.

        Recebe:
            Nenhum parametro.

        Retorna:
            None: Atualiza self.usuario, status_message e screen_name como efeito colateral.
        """
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self.nome_input = ""
            self.idade_input = ""
            self.active_field = "nome"
            self._definir_status("Crie seu perfil para continuar.", "normal")
            self.screen_name = "create"
            return

        self._definir_status("Save carregado. Continue sua jornada.", "success")
        self._abrir_hub()

    def _criar_personagem(self):
        """Valida os campos do formulário de criação, persiste o usuário e vai para o hub.

        Exibe erros de status quando nome estiver vazio, idade não for numérica
        ou estiver fora do intervalo [1, 120].
        """
        nome = self.nome_input.strip()
        if not nome:
            self._definir_status("Informe um nome para o personagem.", "error")
            return
        try:
            idade = int(self.idade_input)
        except ValueError:
            self._definir_status("Informe uma idade numerica.", "error")
            return
        if idade < 1 or idade > 120:
            self._definir_status("A idade precisa estar entre 1 e 120.", "error")
            return

        self.usuario = criar_usuario(nome, idade)
        self._definir_status("Personagem criado. Escolha seu proximo destino.", "success")
        self._abrir_hub()

    def _abrir_hub(self):
        """Navega para o hub; redireciona para criação de personagem se não houver save."""
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self.screen_name = "create"
            return
        self.screen_name = "hub"
        self.active_field = "nome"

    def _abrir_mundos(self):
        """Navega para a seleção de mundos; bloqueia com erro se não houver personagem criado."""
        if carregar_usuario() is None:
            self._definir_status("Crie um personagem antes de viajar.", "error")
            self.screen_name = "create"
            return
        self.screen_name = "worlds"
        self._definir_status("Escolha um destino para estudar.")

    def _mostrar_mundo_em_breve(self):
        """Mostra o aviso de mundo indisponível mantendo o jogador na seleção de mundos.

        Recebe:
            Nenhum parametro.

        Retorna:
            None: Atualiza apenas a mensagem de status exibida na tela de mundos.
        """
        self._definir_status(
            "EM BREVE!\nOs segredos deste lugar ainda não estão prontos para ser revelados. "
            "Continue sua jornada pelo Módulo 1 enquanto isso.",
            "normal",
        )

    def _abrir_perfil(self):
        """Navega para a tela de perfil do jogador."""
        self.screen_name = "profile"

    def _abrir_creditos(self):
        """Toca o som de créditos, zera o scroll e navega para a tela de créditos."""
        self.audio.tocar_creditos()
        self.screen_name = "credits"
        self.credit_scroll = 0

    def _abrir_cutscene(self):
        """Captura o frame atual do hub para o fade de entrada e inicia a cutscene do início.

        Armazena o frame capturado em _cutscene_prev_frame para uso em _renderizar_cutscene
        durante o estado "fade_out_entry". Reseta índice, alpha e estado de fade.
        """
        self._cutscene_prev_frame = self.screen.copy()
        self.cutscene_index = 0
        self.cutscene_fade_alpha = 0
        self.cutscene_fade_state = "fade_out_entry"
        self.cutscene_fade_next = None
        self.screen_name = "cutscene"

    def _avancar_cutscene(self):
        """Avança diretamente para a próxima cena (sem fade) ou abre mundos na última.

        Ignorado enquanto o fade de entrada estiver em andamento (estado != "visible").
        """
        if self.cutscene_fade_state != "visible":
            return
        if self.cutscene_index >= len(CUTSCENE_TEXTS) - 1:
            self._abrir_mundos()
        else:
            self.cutscene_index += 1

    def _iniciar_mundo_1(self):
        """Carrega a aula e exercícios do Mundo 1 e inicia o fluxo de aprendizagem.

        Redireciona para criação de personagem se não houver save, ou exibe erro
        de status quando o arquivo de aula não puder ser carregado.
        """
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self._definir_status("Crie um personagem antes de estudar.", "error")
            self.screen_name = "create"
            return

        self.aula = carregar_aula_pygame(MUNDO_ATIVO, AULA_ATIVA)
        self.exercicios = carregar_exercicios_pygame(MUNDO_ATIVO)
        if not self.aula:
            self._definir_status("Nao foi possivel carregar a aula.", "error")
            return
        self.trilha_indice = 0
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self._definir_status("Leia com calma e avance no seu ritmo.")
        self.screen_name = "lesson"

    def _segmento_atual(self):
        """Retorna o segmento na posição trilha_indice da trilha da aula carregada.

        Retorna:
            dict | None: Dicionário do segmento atual, ou None quando não houver
            aula carregada ou trilha_indice ultrapassar o total de segmentos.
        """
        if not self.aula:
            return None
        trilha = self.aula.get("trilha", [])
        if self.trilha_indice >= len(trilha):
            return None
        return trilha[self.trilha_indice]

    def _exercicio_atual(self):
        """Retorna o exercício na posição exercicio_indice do segmento de prática atual.

        Retorna:
            dict | None: Dicionário do exercício, ou None quando o segmento não
            for do tipo "exercicios" ou o ID não for encontrado em self.exercicios.
        """
        segmento = self._segmento_atual()
        if not segmento or segmento["tipo"] != "exercicios":
            return None
        exercicio_id = segmento["exercicios"][self.exercicio_indice]
        return obter_exercicio(self.exercicios, exercicio_id)

    def _avancar_segmento(self):
        """Incrementa trilha_indice, reseta o estado de exercício e navega para "complete" ao final."""
        self.trilha_indice += 1
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self._definir_status("Continue sua jornada.")
        if self._segmento_atual() is None:
            self.screen_name = "complete"

    def _avancar_exercicio(self):
        """Vai para o próximo exercício do bloco ou avança para o próximo segmento ao esgotar a lista."""
        segmento = self._segmento_atual()
        if not segmento:
            self.screen_name = "complete"
            return
        self.exercicio_indice += 1
        if self.exercicio_indice >= len(segmento["exercicios"]):
            self._avancar_segmento()
        else:
            self.resposta_texto = ""
            self.exercicio_respondido = False
            self._definir_status("Proximo desafio.")

    def _responder_texto_livre(self):
        """Valida que o campo de resposta não está vazio e encaminha para _responder_exercicio."""
        if not self.resposta_texto.strip():
            self._definir_status("Digite uma resposta antes de enviar.", "error")
            return
        self._responder_exercicio(self.resposta_texto)

    def _responder_exercicio(self, resposta):
        """Valida a resposta via registrar_resposta, atualiza XP e define o feedback de status.

        Recebe:
            resposta (int | str): Índice da alternativa escolhida (múltipla escolha)
            ou texto digitado (texto livre).
        """
        exercicio = self._exercicio_atual()
        self.usuario = carregar_usuario()
        if exercicio is None or self.usuario is None:
            self._definir_status("Nao foi possivel responder agora.", "error")
            return

        resultado = registrar_resposta(MUNDO_ATIVO, exercicio, resposta, self.usuario)
        self._definir_status(resultado["mensagem"], "success" if resultado["acertou"] else "error")
        if resultado["acertou"]:
            self.usuario = carregar_usuario()
            self.exercicio_respondido = True
            self.active_field = "nome"

    def _voltar_contextual(self):
        """Navega para a tela anterior mais lógica com base em screen_name atual.

        "hub"/"create" → tela inicial; "worlds"/"profile"/"complete"/"cutscene" → hub;
        "lesson" → mundos; "credits" → hub (logado) ou início (sem usuário); outros → sair.
        """
        if self.screen_name in {"hub", "create"}:
            self._voltar_inicio()
        elif self.screen_name in {"worlds", "profile", "complete", "cutscene"}:
            self._abrir_hub()
        elif self.screen_name == "lesson":
            self._abrir_mundos()
        elif self.screen_name == "credits":
            self._abrir_hub() if self.usuario else self._voltar_inicio()
        else:
            self._sair()

    def _voltar_inicio(self):
        """Navega para a tela inicial e reseta a mensagem de status."""
        self.screen_name = "start"
        self._definir_status("Bem-vindo ao CodeQuest.")

    def _sair(self):
        """Define self.running como False, encerrando o loop principal no próximo ciclo."""
        self.running = False


def main():
    """Instancia CodeQuestPygameMenu e inicia o loop principal do jogo."""
    CodeQuestPygameMenu().run()


if __name__ == "__main__":
    main()
