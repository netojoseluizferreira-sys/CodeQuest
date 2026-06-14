"""Constantes de caminho usadas pela camada de banco de dados."""

import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "codequest.db")
LEGACY_USUARIO_JSON_PATH = os.path.join(DATA_DIR, "usuarios.json")
LEGACY_PROGRESSO_JSON_PATH = os.path.join(DATA_DIR, "progresso.json")
USUARIO_ATIVO_ID = 1
