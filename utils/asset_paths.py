"""Caminhos centralizados para conteudo e assets versionados do CodeQuest."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CONTENT_DIR = DATA_DIR / "content"
FONTS_DIR = DATA_DIR / "fonts"
IMAGES_DIR = DATA_DIR / "images"
BACKGROUNDS_DIR = IMAGES_DIR / "backgrounds"
CUTSCENE_IMAGES_DIR = IMAGES_DIR / "cutscenes"
ACHIEVEMENT_IMAGES_DIR = IMAGES_DIR / "achievements"
MAPS_DIR = IMAGES_DIR / "maps"
VIDEO_DIR = DATA_DIR / "video"
AUDIO_DIR = DATA_DIR / "audio"
MUSIC_DIR = AUDIO_DIR / "music"


def content_path(filename):
    """Retorna o caminho absoluto de um JSON de conteudo versionado."""
    return CONTENT_DIR / filename


def font_path(filename):
    """Retorna o caminho absoluto de uma fonte em `data/fonts`."""
    return FONTS_DIR / filename


def background_path(filename):
    """Retorna o caminho absoluto de uma imagem de fundo em `data/images/backgrounds`."""
    return BACKGROUNDS_DIR / filename


def map_path(filename):
    """Retorna o caminho absoluto de uma imagem de mapa em `data/images/maps`."""
    return MAPS_DIR / filename


def video_frames_dir(name):
    """Retorna o diretorio de frames de video identificado pelo nome logico."""
    return VIDEO_DIR / name


def data_path(relative_path):
    """Resolve um caminho relativo a partir de `data/`."""
    return DATA_DIR / relative_path
