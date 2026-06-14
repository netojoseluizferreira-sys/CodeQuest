from dataclasses import dataclass


@dataclass(frozen=True)
class WindowSettings:
    """Configurações imutáveis da janela Pygame do CodeQuest.

    Acesse via a instância global WINDOW. Alterar valores exige reinicializar
    o display manualmente; o dataclass frozen=True impede atribuições acidentais.
    """

    width: int = 1280
    height: int = 800
    title: str = "CodeQuest - Menu Pygame"
    fps: int = 60


WINDOW = WindowSettings()
