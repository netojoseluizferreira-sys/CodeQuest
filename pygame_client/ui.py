from dataclasses import dataclass
from typing import Callable

import pygame

from pygame_client.palette import PALETTE


def _quebrar_texto_botao(texto, font, largura_maxima):
    """Divide o texto do botao em linhas que cabem dentro do retangulo.

    Recebe:
        texto: Texto exibido no botao.
        font: Fonte usada para medir cada linha.
        largura_maxima: Largura maxima disponivel em pixels.

    Retorna:
        Lista de linhas prontas para renderizacao.
    """
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        candidata = f"{linha_atual} {palavra}".strip()
        if font.size(candidata)[0] <= largura_maxima:
            linha_atual = candidata
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas or [texto]


@dataclass
class Button:
    """Botao retangular usado pelas telas do menu Pygame."""

    rect: pygame.Rect
    text: str
    action: Callable[[], None]
    background: tuple[int, int, int] | None = None
    hover_background: tuple[int, int, int] | None = None
    text_color: tuple[int, int, int] = PALETTE.text

    def draw(self, screen, font, mouse_pos):
        """Desenha o botao na tela.

        Recebe:
            screen: Superficie principal do Pygame.
            font: Fonte usada para renderizar o texto.
            mouse_pos: Posicao atual do mouse.

        Retorna:
            None.
        """
        hovered = self.rect.collidepoint(mouse_pos)
        if hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Mudando cursor para mãozinha

        background = self.background or PALETTE.primary
        hover_background = self.hover_background or PALETTE.primary_hover
        color = hover_background if hovered else background
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, PALETTE.border, self.rect, width=2, border_radius=8)

        linhas = _quebrar_texto_botao(self.text, font, self.rect.width - 24)
        linha_altura = font.get_linesize()
        y = self.rect.centery - ((len(linhas) * linha_altura) // 2)

        for linha in linhas:
            label = font.render(linha, True, self.text_color)
            label_rect = label.get_rect(center=(self.rect.centerx, y + linha_altura // 2))
            screen.blit(label, label_rect)
            y += linha_altura

    def handle_event(self, event):
        """Executa a acao do botao quando houver clique.

        Recebe:
            event: Evento do Pygame recebido no loop principal.

        Retorna:
            True quando o botao foi clicado; caso contrario, False.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False


def desenhar_texto_centralizado(screen, text, font, color, y):
    """Desenha uma linha de texto centralizada horizontalmente.

    Recebe:
        screen: Superficie principal do Pygame.
        text: Texto renderizado.
        font: Fonte usada para renderizar o texto.
        color: Cor RGB do texto.
        y: Coordenada vertical do centro do texto.

    Retorna:
        None.
    """
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(screen.get_width() // 2, y))
    screen.blit(surface, rect)


def quebrar_texto(texto, font, largura_maxima):
    """Divide um texto em linhas que cabem na largura informada.

    Recebe:
        texto: Texto que sera quebrado.
        font: Fonte usada para medir a largura.
        largura_maxima: Largura maxima em pixels.

    Retorna:
        Lista de linhas ajustadas para renderizacao.
    """
    palavras = texto.split()
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        candidata = f"{linha_atual} {palavra}".strip()
        if font.size(candidata)[0] <= largura_maxima:
            linha_atual = candidata
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra

    if linha_atual:
        linhas.append(linha_atual)

    return linhas or [texto]
