from dataclasses import dataclass


@dataclass(frozen=True)
class WindowSettings:
    """Configuracoes visuais da janela Pygame."""

    width: int = 960
    height: int = 640
    title: str = "CodeQuest - Menu Pygame"
    fps: int = 60


WINDOW = WindowSettings()
