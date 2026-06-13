import pygame
import webbrowser  # Adicionei a importacao do webbrowser para abrir links no navegador

from backend.xp_system import xp_para_proximo_nivel
from pygame_client.audio import AudioController
from pygame_client.content import carregar_aula_pygame, carregar_exercicios_pygame, obter_exercicio
from pygame_client.credits import obter_linhas_creditos
from pygame_client.learning_progress import registrar_resposta
from pygame_client.palette import PALETTE
from pygame_client.settings import WINDOW
from pygame_client.ui import Button, desenhar_texto_centralizado, quebrar_texto
from utils.database import carregar_usuario, criar_usuario, resetar_banco_de_dados


MUNDO_ATIVO = "mundo_1"
AULA_ATIVA = "aula_1"


class CodeQuestPygameMenu:
    """Aplicacao Pygame principal do CodeQuest."""

    def __init__(self):
        """Inicializa estado visual, audio, usuario e conteudo.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW.width, WINDOW.height))
        pygame.display.set_caption(WINDOW.title)
        self.clock = pygame.time.Clock()
        self.audio = AudioController()
        self.audio.inicializar()
        self.font_title = pygame.font.SysFont("segoeui", 52, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 21)
        self.font_small = pygame.font.SysFont("segoeui", 17)
        self.font_tiny = pygame.font.SysFont("segoeui", 15)
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
        self.link_rect = None  # Adicionei a variavel para armazenar o retangulo do link
        self.btn_continuar_y = None  # Adicionei a variavel para armazenar o Y do botao continuar

    def run(self):
        """Executa o loop principal da aplicacao.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.audio.tocar_trilha()
        while self.running:
            self._processar_eventos()
            self._renderizar()
            self.clock.tick(WINDOW.fps)

        self.audio.encerrar()
        pygame.quit()

    def _botoes_tela(self):
        """Cria os botoes da tela ativa.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de instancias Button da tela atual.
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
            return [self._botao_voltar_hub()]
        if self.screen_name == "credits":
            return [self._botao_voltar_hub() if self.usuario else self._botao_voltar_inicio()]
        if self.screen_name == "lesson":
            return self._botoes_fluxo_aprendizado()
        if self.screen_name == "complete":
            return [self._botao_voltar_hub()]
        return []

    def _botoes_inicio(self):
        """Monta botoes da tela inicial.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de botoes de inicio.
        """
        return self._botoes_centralizados(
            [
                ("Novo jogo", self._novo_jogo),
                ("Continuar", self._continuar),
                ("Creditos", self._abrir_creditos),
                ("Sair", self._sair),
            ],
            y_inicial=245,
        )

    def _botoes_criacao(self):
        """Monta botoes da criacao de personagem.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de botoes da tela de criacao.
        """
        return [
            Button(pygame.Rect(410, 505, 220, 54), "Criar", self._criar_personagem),
            Button(pygame.Rect(670, 505, 220, 54), "Voltar", self._voltar_inicio),
        ]

    def _botoes_hub(self):
        """Monta botoes do menu principal apos login.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de botoes do hub.
        """
        return self._botoes_centralizados(
            [
                ("Arquipelago de Bythos", self._abrir_mundos),
                ("Perfil", self._abrir_perfil),
                ("Creditos", self._abrir_creditos),
                ("Tela inicial", self._voltar_inicio),
                ("Sair", self._sair),
            ],
            y_inicial=225,
        )

    def _botoes_mundos(self):
        """Monta botoes da tela de selecao de mundos.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de botoes da tela de mundos.
        """
        return [
            Button(pygame.Rect(390, 285, 500, 62), "Mundo 1 - Cabana do Oraculo", self._iniciar_mundo_1),
            self._botao_voltar_hub(),
        ]

    def _botoes_fluxo_aprendizado(self):
        """Monta botoes do segmento atual de aula ou exercicio.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de botoes de navegacao ou resposta.
        """
        segmento = self._segmento_atual()
        if segmento is None:
            return [self._botao_voltar_hub()]

        if segmento["tipo"] == "aula":
            # Mudei a posicao do botao 'Continuar' para acompanhar o y dinamico calculado ao exibir o link, se aplicavel (apenas para modulo 1 aula 1)
            x_btn = self.content_x if self.btn_continuar_y is not None else WINDOW.width - 340
            y_btn = self.btn_continuar_y if self.btn_continuar_y is not None else WINDOW.height - 88
            return [
                Button(pygame.Rect(x_btn, y_btn, 250, 52), "Continuar", self._avancar_segmento),
                self._botao_voltar_mundos(),
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

    def _botoes_centralizados(self, itens, y_inicial):
        """Cria botoes centralizados com espacamento uniforme.

        Recebe:
            itens: Lista de tuplas com texto e acao.
            y_inicial: Coordenada vertical inicial.

        Retorna:
            Lista de botoes configurados.
        """
        largura = 420
        altura = 58
        x = (WINDOW.width - largura) // 2
        return [
            Button(pygame.Rect(x, y_inicial + (indice * 72), largura, altura), texto, acao)
            for indice, (texto, acao) in enumerate(itens)
        ]

    def _botao_voltar_inicio(self):
        """Cria botao de retorno para a tela inicial.

        Recebe:
            Nenhum parametro.

        Retorna:
            Botao Voltar.
        """
        return Button(pygame.Rect(60, WINDOW.height - 88, 190, 52), "Voltar", self._voltar_inicio)

    def _botao_voltar_hub(self):
        """Cria botao de retorno para o hub.

        Recebe:
            Nenhum parametro.

        Retorna:
            Botao Voltar.
        """
        return Button(pygame.Rect(60, WINDOW.height - 88, 190, 52), "Voltar", self._abrir_hub)

    def _botao_voltar_mundos(self):
        """Cria botao de retorno para a tela de mundos.

        Recebe:
            Nenhum parametro.

        Retorna:
            Botao Voltar.
        """
        return Button(pygame.Rect(60, WINDOW.height - 88, 190, 52), "Mundos", self._abrir_mundos)

    def _processar_eventos(self):
        """Processa eventos de teclado, mouse e janela.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._sair()
            elif event.type == pygame.KEYDOWN:
                self._processar_tecla(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._processar_clique(event)

    def _processar_clique(self, event):
        """Processa cliques de mouse da tela atual.

        Recebe:
            event: Evento de clique recebido pelo Pygame.

        Retorna:
            None.
        """
        if self.screen_name == "create":
            if pygame.Rect(390, 285, 500, 50).collidepoint(event.pos):
                self.active_field = "nome"
            elif pygame.Rect(390, 385, 220, 50).collidepoint(event.pos):
                self.active_field = "idade"

        if self.screen_name == "lesson":
            segmento = self._segmento_atual()

            # Adicionei a verificacao de clique no link do Youtube
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
        """Processa teclado de navegacao e campos de texto.

        Recebe:
            event: Evento KEYDOWN recebido pelo Pygame.

        Retorna:
            None.
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

        if self.screen_name == "create":
            self._digitar_criacao(event)
        elif self.screen_name == "lesson" and self.active_field == "resposta":
            self._digitar_resposta(event)

    def _digitar_criacao(self, event):
        """Atualiza campos da tela de criacao de personagem.

        Recebe:
            event: Evento KEYDOWN recebido pelo Pygame.

        Retorna:
            None.
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
        """Atualiza campo de resposta textual.

        Recebe:
            event: Evento KEYDOWN recebido pelo Pygame.

        Retorna:
            None.
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
        """Renderiza a tela ativa.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.screen.fill(PALETTE.background)
        if self.screen_name == "start":
            self._renderizar_inicio()
        elif self.screen_name == "create":
            self._renderizar_criacao()
        elif self.screen_name == "hub":
            self._renderizar_hub()
        elif self.screen_name == "worlds":
            self._renderizar_mundos()
        elif self.screen_name == "profile":
            self._renderizar_perfil()
        elif self.screen_name == "credits":
            self._renderizar_creditos()
        elif self.screen_name == "lesson":
            self._renderizar_fluxo_aprendizado()
        elif self.screen_name == "complete":
            self._renderizar_conclusao()

        mouse_pos = pygame.mouse.get_pos()
        for button in self._botoes_tela():
            button.draw(self.screen, self.font_body, mouse_pos)
        pygame.display.flip()

    def _renderizar_inicio(self):
        """Renderiza a tela inicial.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self._desenhar_cabecalho("CodeQuest", "Uma Jornada pelo Arquipelago de Bythos")
        self._desenhar_status(570)

    def _renderizar_criacao(self):
        """Renderiza a tela de criacao de personagem.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self._desenhar_cabecalho("Criar personagem", "Defina quem vai explorar Bythos")
        self._desenhar_label("Nome do aventureiro", 390, 252)
        self._desenhar_input(pygame.Rect(390, 285, 500, 50), self.nome_input, "nome", "Digite seu nome")
        self._desenhar_label("Idade", 390, 352)
        self._desenhar_input(pygame.Rect(390, 385, 220, 50), self.idade_input, "idade", "18")
        self._desenhar_status(610)

    def _renderizar_hub(self):
        """Renderiza o menu principal do jogador.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        nome = self.usuario.nome if self.usuario else "Aventureiro"
        self._desenhar_cabecalho("Menu de Jornada", f"Bem-vindo, {nome}")
        self._desenhar_status(585)

    def _renderizar_mundos(self):
        """Renderiza a selecao de mundos.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self._desenhar_cabecalho("Arquipelago de Bythos", "Escolha o proximo destino")
        self._desenhar_paragrafo(
            "A Cabana do Oraculo guarda a primeira aula: programacao, algoritmos e linguagens.",
            280,
            390,
            720,
            self.font_body,
            PALETTE.text,
        )
        self._desenhar_status(650)

    def _renderizar_perfil(self):
        """Renderiza a tela de perfil do usuario.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.usuario = carregar_usuario()
        self._desenhar_cabecalho("Perfil", "Seu progresso em Bythos")
        if self.usuario is None:
            self._desenhar_paragrafo("Nenhum personagem criado ainda.", 360, 300, 560, self.font_body, PALETTE.text)
            return

        dados = [
            f"Nome: {self.usuario.nome}",
            f"Idade: {self.usuario.idade}",
            f"Nivel: {self.usuario.nivel}",
            f"XP total: {self.usuario.xp}",
            f"XP para o proximo nivel: {xp_para_proximo_nivel(self.usuario.xp)}",
        ]
        y = 250
        for linha in dados:
            self._desenhar_paragrafo(linha, 430, y, 520, self.font_body, PALETTE.text)
            y += 48

    def _renderizar_creditos(self):
        """Renderiza a tela de creditos com rolagem.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        y = 58 - self.credit_scroll
        largura_texto = WINDOW.width - 160
        for style, text in obter_linhas_creditos():
            font, color, spacing = self._estilo_credito(style)
            for line in quebrar_texto(text, font, largura_texto):
                desenhar_texto_centralizado(self.screen, line, font, color, y)
                y += spacing
            y += 8
        self._desenhar_rodape("Use W/S ou setas para rolar. ESC volta.")

    def _renderizar_fluxo_aprendizado(self):
        """Renderiza aula ou exercicio atual.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        segmento = self._segmento_atual()
        if segmento is None:
            self.screen_name = "complete"
            return
        if segmento["tipo"] == "aula":
            self._renderizar_segmento_aula(segmento)
        else:
            self._renderizar_segmento_exercicio(segmento)

    def _renderizar_segmento_aula(self, segmento):
        """Renderiza um texto de aula.

        Recebe:
            segmento: Dicionario do segmento de aula atual.

        Retorna:
            None.
        """
        self._desenhar_cabecalho(segmento["titulo"], self.aula["titulo"])
        y = 205
        for paragrafo in segmento["conteudo"]:
            y = self._desenhar_paragrafo(paragrafo, self.content_x, y, self.content_width, self.font_small, PALETTE.text) + 12

        # Adicionei checagem para Módulo 1 (MUNDO_ATIVO) e primeira aula (texto_1)
        if MUNDO_ATIVO == "mundo_1" and segmento.get("id") == "texto_1":
            chamada = "Quer se aprofundar um pouco mais no tema? Clica no link abaixo e assista a uma aula completa!"
            y = self._desenhar_paragrafo(chamada, self.content_x, y + 10, self.content_width, self.font_body, PALETTE.accent) + 10

            link_texto = "Assistir Aula Completa (YouTube)"
            link_surface = self.font_body.render(link_texto, True, (0, 150, 255))
            self.link_rect = link_surface.get_rect(topleft=(self.content_x, y))
            self.screen.blit(link_surface, self.link_rect)

            y = self.link_rect.bottom + 20
            self.btn_continuar_y = y  # Salva para posicionar o botão continuar
        else:
            self.link_rect = None
            self.btn_continuar_y = None

    def _renderizar_segmento_exercicio(self, segmento):
        """Renderiza o exercicio atual dentro de uma lista de pratica.

        Recebe:
            segmento: Dicionario do bloco de exercicios atual.

        Retorna:
            None.
        """
        exercicio = self._exercicio_atual()
        numero = self.exercicio_indice + 1
        total = len(segmento["exercicios"])
        self._desenhar_cabecalho(segmento["titulo"], f"Exercicio {numero} de {total}")
        if exercicio is None:
            self._desenhar_paragrafo("Exercicio nao encontrado.", self.content_x, 250, self.content_width, self.font_body, PALETTE.text)
            return

        self._desenhar_paragrafo(exercicio["pergunta"], self.content_x, 205, self.content_width, self.font_body, PALETTE.text)
        if exercicio["tipo"] == "multipla_escolha":
            self._renderizar_opcoes(exercicio)
        else:
            placeholder = exercicio.get("placeholder", "Digite sua resposta")
            self._desenhar_input(pygame.Rect(self.content_x, 455, self.content_width, 52), self.resposta_texto, "resposta", placeholder)

        self._desenhar_status(WINDOW.height - 118)

    def _renderizar_opcoes(self, exercicio):
        """Mantem o espaco das alternativas, renderizadas pelos botoes.

        Recebe:
            exercicio: Dicionario do exercicio atual.

        Retorna:
            None.
        """
        return None

    def _renderizar_conclusao(self):
        """Renderiza a tela de conclusao da aula.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
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
        """Desenha cabecalho padrao da tela.

        Recebe:
            titulo: Titulo principal.
            subtitulo: Texto secundario.

        Retorna:
            None.
        """
        pygame.draw.rect(self.screen, PALETTE.surface, pygame.Rect(0, 0, WINDOW.width, 170))
        pygame.draw.line(self.screen, PALETTE.border, (0, 170), (WINDOW.width, 170), 2)
        desenhar_texto_centralizado(self.screen, titulo, self.font_title, PALETTE.text, 68)
        desenhar_texto_centralizado(self.screen, subtitulo, self.font_subtitle, PALETTE.accent, 120)

    def _desenhar_label(self, texto, x, y):
        """Desenha um label de formulario.

        Recebe:
            texto: Texto do label.
            x: Coordenada horizontal.
            y: Coordenada vertical.

        Retorna:
            None.
        """
        self.screen.blit(self.font_small.render(texto, True, PALETTE.muted), (x, y))

    def _desenhar_input(self, rect, valor, campo, placeholder):
        """Desenha campo de entrada de texto.

        Recebe:
            rect: Retangulo do campo.
            valor: Texto atual.
            campo: Nome interno do campo.
            placeholder: Texto exibido quando vazio.

        Retorna:
            None.
        """
        ativo = self.active_field == campo
        cor_borda = PALETTE.accent if ativo else PALETTE.border
        pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=8)
        pygame.draw.rect(self.screen, cor_borda, rect, width=2, border_radius=8)
        texto = valor or placeholder
        cor = PALETTE.text if valor else PALETTE.muted
        self.screen.blit(self.font_body.render(texto, True, cor), (rect.x + 14, rect.y + 10))

    def _desenhar_paragrafo(self, texto, x, y, largura, font, color):
        """Desenha texto quebrado em varias linhas.

        Recebe:
            texto: Conteudo textual.
            x: Coordenada horizontal.
            y: Coordenada vertical.
            largura: Largura maxima.
            font: Fonte usada no texto.
            color: Cor RGB.

        Retorna:
            Proxima coordenada y apos o bloco.
        """
        linha_altura = font.get_linesize() + 4
        for linha in quebrar_texto(texto, font, largura):
            self.screen.blit(font.render(linha, True, color), (x, y))
            y += linha_altura
        return y

    def _desenhar_status(self, y):
        """Desenha mensagem de status atual.

        Recebe:
            y: Coordenada vertical central da mensagem.

        Retorna:
            None.
        """
        if self.status_kind in {"success", "error"}:
            color = PALETTE.success if self.status_kind == "success" else PALETTE.error
            font = self.font_body
            linhas = quebrar_texto(self.status_message, font, self.content_width - 80)
            linha_altura = font.get_linesize()
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
        """Atualiza a mensagem de status e seu estilo visual.

        Recebe:
            mensagem: Texto que sera exibido no rodape ou banner.
            kind: Tipo visual da mensagem: normal, success ou error.

        Retorna:
            None.
        """
        self.status_message = mensagem
        self.status_kind = kind

    def _desenhar_rodape(self, texto):
        """Desenha rodape fixo na base da tela.

        Recebe:
            texto: Mensagem exibida no rodape.

        Retorna:
            None.
        """
        rodape = pygame.Rect(0, WINDOW.height - 54, WINDOW.width, 54)
        pygame.draw.rect(self.screen, PALETTE.surface, rodape)
        pygame.draw.line(self.screen, PALETTE.border, (0, WINDOW.height - 54), (WINDOW.width, WINDOW.height - 54), 2)
        desenhar_texto_centralizado(self.screen, texto, self.font_small, PALETTE.muted, WINDOW.height - 27)

    def _estilo_credito(self, style):
        """Resolve fonte, cor e espacamento de uma linha de creditos.

        Recebe:
            style: Nome do estilo da linha de creditos.

        Retorna:
            Tupla com fonte, cor RGB e espacamento vertical.
        """
        if style == "title":
            return self.font_title, PALETTE.primary, 58
        if style == "subtitle":
            return self.font_subtitle, PALETTE.accent, 36
        if style == "section":
            return self.font_subtitle, PALETTE.text, 38
        if style == "body":
            return self.font_body, PALETTE.text, 30
        if style == "quote":
            return self.font_small, PALETTE.accent, 26
        if style == "footer":
            return self.font_small, PALETTE.gold, 30
        return self.font_small, PALETTE.muted, 24

    def _novo_jogo(self):
        """Inicia novo jogo e abre criacao de personagem.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        resetar_banco_de_dados()
        self.usuario = None
        self.nome_input = ""
        self.idade_input = ""
        self.active_field = "nome"
        self._definir_status("Crie seu personagem para comecar uma nova jornada.")
        self.screen_name = "create"

    def _continuar(self):
        """Continua save existente ou abre criacao quando nao houver usuario.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self._definir_status("Nenhum save encontrado. Crie seu personagem.", "error")
            self.screen_name = "create"
            return
        self._abrir_hub()

    def _criar_personagem(self):
        """Valida formulario e cria usuario ativo.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
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
        """Abre o menu principal do jogador.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self.screen_name = "create"
            return
        self.screen_name = "hub"
        self.active_field = "nome"

    def _abrir_mundos(self):
        """Abre a tela de mundos.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if carregar_usuario() is None:
            self._definir_status("Crie um personagem antes de viajar.", "error")
            self.screen_name = "create"
            return
        self.screen_name = "worlds"
        self._definir_status("Escolha um mundo para estudar.")

    def _abrir_perfil(self):
        """Abre a tela de perfil.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.screen_name = "profile"

    def _abrir_creditos(self):
        """Abre a tela de creditos.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.audio.tocar_creditos()
        self.screen_name = "credits"
        self.credit_scroll = 0

    def _iniciar_mundo_1(self):
        """Carrega a primeira aula e inicia o fluxo de aprendizagem.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
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
        """Retorna o segmento atual da trilha.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario do segmento atual ou None quando terminou.
        """
        if not self.aula:
            return None
        trilha = self.aula.get("trilha", [])
        if self.trilha_indice >= len(trilha):
            return None
        return trilha[self.trilha_indice]

    def _exercicio_atual(self):
        """Retorna o exercicio atual dentro do bloco de pratica.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario do exercicio atual ou None.
        """
        segmento = self._segmento_atual()
        if not segmento or segmento["tipo"] != "exercicios":
            return None
        exercicio_id = segmento["exercicios"][self.exercicio_indice]
        return obter_exercicio(self.exercicios, exercicio_id)

    def _avancar_segmento(self):
        """Avanca para o proximo segmento da trilha.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.trilha_indice += 1
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self._definir_status("Continue sua jornada.")
        if self._segmento_atual() is None:
            self.screen_name = "complete"

    def _avancar_exercicio(self):
        """Avanca para o proximo exercicio ou segmento.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
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
        """Envia resposta textual do exercicio atual.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if not self.resposta_texto.strip():
            self._definir_status("Digite uma resposta antes de enviar.", "error")
            return
        self._responder_exercicio(self.resposta_texto)

    def _responder_exercicio(self, resposta):
        """Valida resposta, persiste erros/conclusao e atualiza XP.

        Recebe:
            resposta: Indice de alternativa ou texto digitado.

        Retorna:
            None.
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
        """Volta para a tela mais adequada ao contexto atual.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if self.screen_name in {"hub", "create"}:
            self._voltar_inicio()
        elif self.screen_name in {"worlds", "profile", "complete"}:
            self._abrir_hub()
        elif self.screen_name == "lesson":
            self._abrir_mundos()
        elif self.screen_name == "credits":
            self._abrir_hub() if self.usuario else self._voltar_inicio()
        else:
            self._sair()

    def _voltar_inicio(self):
        """Retorna para a tela inicial.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.screen_name = "start"
        self._definir_status("Bem-vindo ao CodeQuest.")

    def _sair(self):
        """Encerra o loop principal.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.running = False


def main():
    """Executa o CodeQuest em Pygame.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    CodeQuestPygameMenu().run()


if __name__ == "__main__":
    main()
