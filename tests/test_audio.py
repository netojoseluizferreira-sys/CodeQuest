"""Testes de configuração das trilhas musicais."""

from pygame_client.audio import TRACK_FILES


def test_track_files_mapeia_contextos_principais():
    assert TRACK_FILES["start"] == "terran_1.mp3"
    assert TRACK_FILES["hub"] == "terran_2.mp3"
    assert TRACK_FILES["cutscene"] == "zerg_1.mp3"
    assert TRACK_FILES["worlds"] == "protoss_1.mp3"
    assert TRACK_FILES["lesson"] == "terran_3.mp3"
    assert TRACK_FILES["exercise"] == "terran_1.mp3"
    assert TRACK_FILES["profile"] == "protoss_2.mp3"
    assert TRACK_FILES["credits"] == "terran_victory.mp3"
