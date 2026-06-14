from dataclasses import dataclass
from typing import Callable

import pygame

from pygame_client.palette import PALETTE


def _quebrar_texto_botao(texto, font, largura_maxima):
    """Divide um texto em linhas que caibam dentro da largura do botão.

    Recebe:
        texto (str): Texto completo do botão.
        font (pygame.font.Font): Fonte usada para medir a largura de cada token.
        largura_maxima (int): Largura disponível em pixels, já descontado o padding.

    Retorna:
        list[str]: Lista de linhas prontas para renderização; contém ao menos
        um elemento (o texto original) quando nenhuma quebra for possível.
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
    """Botão retangular interativo usado pelas telas do menu Pygame."""

    rect: pygame.Rect
    text: str
    action: Callable[[], None]
    background: tuple[int, int, int] | None = None
    hover_background: tuple[int, int, int] | None = None
    text_color: tuple[int, int, int] = PALETTE.text
    hover_text_color: tuple[int, int, int] | None = None
    border_color: tuple[int, int, int] | None = None

    def draw(self, screen, font, mouse_pos):
        """Renderiza o botão na surface, aplicando cor de hover quando o mouse está sobre ele.

        Recebe:
            screen (pygame.Surface): Surface principal onde o botão é desenhado.
            font (pygame.font.Font): Fonte usada para renderizar o rótulo.
            mouse_pos (tuple[int, int]): Posição atual do cursor em pixels.
        """
        hovered = self.rect.collidepoint(mouse_pos)
        background = self.background or PALETTE.primary
        hover_background = self.hover_background or PALETTE.primary_hover
        color = hover_background if hovered else background
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.border_color or PALETTE.border, self.rect, width=2, border_radius=8)

        linhas = _quebrar_texto_botao(self.text, font, self.rect.width - 24)
        linha_altura = font.get_linesize()
        y = self.rect.centery - ((len(linhas) * linha_altura) // 2)

        cur_text_color = (self.hover_text_color if hovered and self.hover_text_color is not None else self.text_color)
        for linha in linhas:
            label = font.render(linha, True, cur_text_color)
            label_rect = label.get_rect(center=(self.rect.centerx, y + linha_altura // 2))
            screen.blit(label, label_rect)
            y += linha_altura

    def handle_event(self, event):
        """Executa a ação do botão quando há clique esquerdo dentro do seu rect.

        Recebe:
            event (pygame.event.Event): Evento do Pygame recebido no loop principal.

        Retorna:
            bool: True quando o clique coincidiu com o rect e a ação foi chamada;
            False em qualquer outro caso.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.action()
                return True
        return False


def desenhar_texto_centralizado(screen, text, font, color, y):
    """Renderiza uma linha de texto centralizada horizontalmente na surface.

    Recebe:
        screen (pygame.Surface): Surface onde o texto é desenhado.
        text (str): Texto a renderizar.
        font (pygame.font.Font): Fonte usada na renderização.
        color (tuple[int, int, int]): Cor RGB do texto.
        y (int): Coordenada vertical do centro do texto.
    """
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(screen.get_width() // 2, y))
    screen.blit(surface, rect)


def quebrar_texto(texto, font, largura_maxima):
    """Divide um texto em linhas que caibam na largura informada.

    Recebe:
        texto (str): Texto a quebrar.
        font (pygame.font.Font): Fonte usada para medir a largura de cada token.
        largura_maxima (int): Largura máxima disponível em pixels.

    Retorna:
        list[str]: Lista de linhas ajustadas; contém ao menos um elemento
        (o texto original) quando nenhuma quebra for possível.
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
