from dataclasses import dataclass
from typing import Callable

import pygame

from pygame_client.palette import PALETTE


@dataclass
class Button:
    """Botao retangular usado pelas telas do menu Pygame."""

    rect: pygame.Rect
    text: str
    action: Callable[[], None]

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
        color = PALETTE.primary_hover if hovered else PALETTE.primary
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, PALETTE.border, self.rect, width=2, border_radius=8)

        label = font.render(self.text, True, (255, 255, 255))
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

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
