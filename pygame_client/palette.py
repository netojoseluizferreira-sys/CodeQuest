"""Paleta visual compartilhada pelas telas Pygame do CodeQuest."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CodeQuestPalette:
    """Paleta de cores imutável usada pelas telas Pygame do CodeQuest.

    Todos os campos são tuplas RGB (int, int, int) e não devem ser modificados
    em tempo de execução (frozen=True). Acesse via a instância global PALETTE.
    """

    background: tuple[int, int, int] = (11, 18, 32)
    surface: tuple[int, int, int] = (22, 31, 49)
    surface_hover: tuple[int, int, int] = (32, 45, 68)
    text: tuple[int, int, int] = (232, 238, 247)
    muted: tuple[int, int, int] = (150, 162, 181)
    primary: tuple[int, int, int] = (55, 92, 145)
    primary_hover: tuple[int, int, int] = (71, 116, 181)
    accent: tuple[int, int, int] = (105, 179, 255)
    success: tuple[int, int, int] = (67, 199, 128)
    error: tuple[int, int, int] = (255, 99, 99)
    gold: tuple[int, int, int] = (245, 190, 92)
    border: tuple[int, int, int] = (67, 82, 107)


PALETTE = CodeQuestPalette()
