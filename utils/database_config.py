"""Constantes de caminho usadas pela camada de banco de dados."""

import os

from utils.asset_paths import DATA_DIR as PROJECT_DATA_DIR, PROJECT_ROOT

BASE_DIR = str(PROJECT_ROOT)
DATA_DIR = str(PROJECT_DATA_DIR)
DB_PATH = os.path.join(DATA_DIR, "codequest.db")
LEGACY_USUARIO_JSON_PATH = os.path.join(DATA_DIR, "usuarios.json")
LEGACY_PROGRESSO_JSON_PATH = os.path.join(DATA_DIR, "progresso.json")
USUARIO_ATIVO_ID = 1
