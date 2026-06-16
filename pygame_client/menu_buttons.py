"""Fábricas de botões das telas do menu Pygame."""

import pygame

from backend.worlds import listar_mundos, titulo_botao_mundo
from pygame_client.menu_config import _KW_VERDE
from pygame_client.settings import WINDOW
from pygame_client.ui import Button


class ButtonMixin:
    """Agrupa a montagem dos botões clicáveis usados por cada tela.

    Espera que a classe principal exponha `screen_name`, dimensões de conteúdo
    e métodos de navegação. Retorna objetos `Button` já posicionados para serem
    desenhados e acionados pelo loop principal.
    """

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
            return [self._botao_voltar_inicio(**_KW_VERDE)]
        if self.screen_name == "cutscene":
            return []
        if self.screen_name == "lesson":
            return self._botoes_fluxo_aprendizado()
        if self.screen_name == "complete":
            proximo_label, proximo_acao = self._proximo_mundo_conclusao()
            return [
                Button(pygame.Rect(WINDOW.width // 2 - 125, WINDOW.height - 88, 250, 52), proximo_label, proximo_acao, **_KW_VERDE),
                Button(pygame.Rect(WINDOW.width - 310, WINDOW.height - 88, 250, 52), "Perfil", self._abrir_perfil, **_KW_VERDE),
                self._botao_voltar_hub(**_KW_VERDE),
            ]
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
            Button(pygame.Rect(WINDOW.width - 190, WINDOW.height - 75, 160, 45), "Créditos", self._abrir_creditos, **_KW_VERDE),
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
            Button(pygame.Rect(x, y_inicial, largura, altura), "Arquipélago de Bythos", self._abrir_cutscene, **_KW_VERDE),
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
        for indice, mundo in enumerate(listar_mundos()):
            col = indice % 3
            row = indice // 3
            x = _start_x + col * (_bw + _gap_x)
            y = _start_y + row * (_bh + _gap_y)
            botoes.append(
                Button(
                    pygame.Rect(x, y, _bw, _bh),
                    titulo_botao_mundo(mundo),
                    lambda mundo_id=mundo["id"]: self._selecionar_mundo(mundo_id),
                    **_KW_VERDE,
                )
            )
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

        if segmento["tipo"] == "final_text":
            return [
                Button(pygame.Rect(WINDOW.width - 310, WINDOW.height - 88, 250, 52), "Continuar", self._avancar_segmento, **_KW_VERDE),
                self._botao_voltar_mundos(**_KW_VERDE),
            ]

        if segmento["tipo"] == "cutscene_video":
            return []

        if self.exercicio_respondido:
            return [
                Button(pygame.Rect(WINDOW.width - 340, WINDOW.height - 88, 250, 52), "Próximo", self._avancar_exercicio, **_KW_VERDE),
                self._botao_voltar_mundos(**_KW_VERDE),
            ]

        exercicio = self._exercicio_atual()
        if exercicio and exercicio["tipo"] == "multipla_escolha":
            botoes = []
            for indice, opcao in enumerate(exercicio["opcoes"]):
                y = 330 + (indice * 82)
                botoes.append(
                    Button(
                        pygame.Rect(self.content_x, y, self.content_width, 72),
                        f"{chr(65 + indice)}) {opcao}",
                        lambda escolha=indice: self._responder_exercicio(escolha),
                        **_KW_VERDE,
                    )
                )
            botoes.append(self._botao_voltar_mundos(**_KW_VERDE))
            return botoes

        return [
            Button(pygame.Rect(WINDOW.width - 340, WINDOW.height - 88, 250, 52), "Responder", self._responder_texto_livre, **_KW_VERDE),
            self._botao_voltar_mundos(**_KW_VERDE),
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
