from dataclasses import dataclass


@dataclass(frozen=True)
class CodeQuestPalette:
    """Paleta inspirada no tema padrao do Streamlit usado pelo projeto."""

    background: tuple[int, int, int] = (255, 255, 255)
    surface: tuple[int, int, int] = (240, 242, 246)
    surface_hover: tuple[int, int, int] = (225, 229, 236)
    text: tuple[int, int, int] = (49, 51, 63)
    muted: tuple[int, int, int] = (109, 116, 128)
    primary: tuple[int, int, int] = (255, 75, 75)
    primary_hover: tuple[int, int, int] = (226, 55, 55)
    accent: tuple[int, int, int] = (0, 104, 201)
    success: tuple[int, int, int] = (33, 195, 84)
    gold: tuple[int, int, int] = (245, 166, 35)
    border: tuple[int, int, int] = (210, 214, 222)


PALETTE = CodeQuestPalette()
