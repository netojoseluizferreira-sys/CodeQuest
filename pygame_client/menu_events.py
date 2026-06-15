"""Processamento de eventos de mouse e teclado do menu Pygame."""

import pygame
import webbrowser

from pygame_client.settings import WINDOW


class EventMixin:
    """Centraliza a leitura de eventos de mouse e teclado do Pygame.

    Os métodos não retornam valores; eles atualizam o estado da tela principal,
    disparam ações dos botões e encaminham digitação para formulários ou
    respostas de exercícios.
    """

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
                url = segmento.get("video_url") if segmento else None
                webbrowser.open(url or "https://www.youtube.com/watch?v=8mei6uVttho")

            exercicio = self._exercicio_atual() if segmento and segmento["tipo"] == "exercicios" else None
            if exercicio and exercicio["tipo"] == "completar":
                if pygame.Rect(self.content_x, 350, self.content_width, 58).collidepoint(event.pos):
                    self.active_field = "resposta"

        if self.screen_name == "credits":
            if self.credit_link_rect and self.credit_link_rect.collidepoint(event.pos):
                webbrowser.open("https://github.com/netojoseluizferreira-sys/CodeQuest")

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
        elif self.screen_name == "lesson":
            exercicio = self._exercicio_atual()
            if exercicio and exercicio.get("tipo") != "multipla_escolha" and not self.exercicio_respondido:
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
