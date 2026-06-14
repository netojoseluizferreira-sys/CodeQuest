"""Fixtures compartilhadas pelos testes automatizados do CodeQuest."""

import pytest

from utils import database_config


@pytest.fixture()
def banco_temporario(tmp_path, monkeypatch):
    """Isola o banco SQLite e os arquivos legados em uma pasta temporaria."""
    monkeypatch.setattr(database_config, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(database_config, "DB_PATH", str(tmp_path / "codequest.db"))
    monkeypatch.setattr(
        database_config,
        "LEGACY_USUARIO_JSON_PATH",
        str(tmp_path / "usuario.json"),
    )
    monkeypatch.setattr(
        database_config,
        "LEGACY_PROGRESSO_JSON_PATH",
        str(tmp_path / "progresso.json"),
    )
    return tmp_path
