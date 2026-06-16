"""Trilhas de fundo e efeitos sonoros usados pela interface Pygame."""

import math
import os
from array import array

import pygame


TRACK_FILES = {
    "start": "terran_1.mp3",
    "hub": "terran_2.mp3",
    "cutscene": "zerg_1.mp3",
    "worlds": "protoss_1.mp3",
    "lesson": "terran_3.mp3",
    "exercise": "terran_1.mp3",
    "profile": "protoss_2.mp3",
    "credits": "terran_victory.mp3",
    "complete": "terran_victory.mp3",
}


class AudioController:
    """Controla trilhas MP3 de fundo e efeitos sonoros gerados em memória."""

    def __init__(self, sample_rate=44100, music_dir=None):
        """Configura os atributos iniciais sem inicializar o mixer.

        Recebe:
            sample_rate (int): Taxa de amostragem em Hz usada na geração de áudio.
            O mixer só é aberto quando inicializar() for chamado.
            music_dir (str | None): Diretório com os arquivos MP3. Quando None,
            usa data/music na raiz do projeto.
        """
        self.sample_rate = sample_rate
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.music_dir = music_dir or os.path.join(base_dir, "data", "music")
        self.enabled = False
        self.music_channel = None
        self.button_sound = None
        self.credit_sound = None
        self.current_track = None
        self.fallback_track = None

    def inicializar(self):
        """Inicializa o mixer do Pygame e pré-gera os efeitos sonoros.

        Abre o mixer com formato PCM de 16 bits mono a sample_rate Hz, reserva
        o canal 0 para a trilha e gera os sons de botão e créditos via _criar_tom.
        Em caso de erro do mixer, desativa o áudio silenciosamente.

        Retorna:
            bool: True quando o mixer foi inicializado com sucesso; False caso contrário.
        """
        try:
            pygame.mixer.pre_init(self.sample_rate, -16, 1, 512)
            pygame.mixer.init()
            self.music_channel = pygame.mixer.Channel(0)
            self.button_sound = self._criar_tom(660, 0.08, 0.18)
            self.credit_sound = self._criar_tom(880, 0.14, 0.14)
            self.fallback_track = self._criar_trilha()
            self.enabled = True
        except pygame.error:
            self.enabled = False
        return self.enabled

    def tocar_trilha(self, contexto="start"):
        """Toca em loop a trilha associada ao contexto informado.

        Recebe:
            contexto (str): Chave de TRACK_FILES, como "start", "hub",
            "lesson" ou "exercise". Contextos desconhecidos usam "start".
        """
        if not self.enabled:
            return

        track_key = contexto if contexto in TRACK_FILES else "start"
        if self.current_track == track_key and pygame.mixer.music.get_busy():
            return

        caminho = os.path.join(self.music_dir, TRACK_FILES[track_key])
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(0.28)
            pygame.mixer.music.play(loops=-1)
            if self.music_channel:
                self.music_channel.stop()
            self.current_track = track_key
        except pygame.error:
            self._tocar_trilha_fallback(track_key)

    def _tocar_trilha_fallback(self, track_key):
        """Toca a trilha procedural quando um MP3 não está disponível.

        Recebe:
            track_key (str): Contexto que deveria tocar; salvo em current_track
            para evitar reiniciar o fallback a cada frame.
        """
        if not self.music_channel or not self.fallback_track:
            return
        if self.current_track == track_key and self.music_channel.get_busy():
            return
        pygame.mixer.music.stop()
        self.music_channel.set_volume(0.28)
        self.music_channel.play(self.fallback_track, loops=-1)
        self.current_track = track_key

    def tocar_botao(self):
        """Reproduz o efeito sonoro padrão de clique em botão.

        Só executa quando o áudio estiver habilitado e o som gerado.
        """
        if self.enabled and self.button_sound:
            self.button_sound.play()

    def tocar_creditos(self):
        """Reproduz o efeito sonoro de abertura da tela de créditos.

        Só executa quando o áudio estiver habilitado e o som gerado.
        """
        if self.enabled and self.credit_sound:
            self.credit_sound.play()

    def tocar_arquivo_uma_vez(self, nome_arquivo, chave=None, volume=0.34):
        """Toca um arquivo de musica uma unica vez, sem loop."""
        if not self.enabled:
            return

        track_key = chave or nome_arquivo
        if self.current_track == track_key and pygame.mixer.music.get_busy():
            return

        caminho = os.path.join(self.music_dir, nome_arquivo)
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops=0)
            if self.music_channel:
                self.music_channel.stop()
            self.current_track = track_key
        except pygame.error:
            return

    def encerrar(self):
        """Finaliza o mixer do Pygame quando o áudio estiver ativo."""
        if self.enabled:
            pygame.mixer.music.stop()
            pygame.mixer.quit()

    def _criar_tom(self, frequencia, duracao, volume):
        """Gera um tom senoidal com envelope de decaimento linear.

        Recebe:
            frequencia (float): Frequência do tom em Hz.
            duracao (float): Duração do som em segundos.
            volume (float): Amplitude máxima entre 0.0 e 1.0.

        Retorna:
            pygame.mixer.Sound: Objeto de som pronto para reprodução.
        """
        total = int(self.sample_rate * duracao)
        samples = array("h")
        for indice in range(total):
            envelope = 1 - (indice / total)
            onda = math.sin(2 * math.pi * frequencia * indice / self.sample_rate)
            samples.append(int(32767 * volume * envelope * onda))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _criar_trilha(self):
        """Gera uma sequência de notas em arpejo para uso como trilha de fundo.

        Sintetiza seis notas (C4-E4-G4-C5-G4-E4) com harmônico de segunda oitava,
        usando um envelope de ataque rápido (40 ms) e decaimento proporcional.

        Retorna:
            pygame.mixer.Sound: Objeto de som com a trilha gerada, adequado para loop.
        """
        notas = (261.63, 329.63, 392.00, 523.25, 392.00, 329.63)
        duracao_nota = 0.32
        samples = array("h")

        for nota in notas:
            total = int(self.sample_rate * duracao_nota)
            for indice in range(total):
                fase = indice / self.sample_rate
                envelope = min(1.0, indice / (self.sample_rate * 0.04))
                envelope *= max(0.0, 1 - indice / total)
                onda = math.sin(2 * math.pi * nota * fase)
                harmonia = 0.35 * math.sin(2 * math.pi * nota * 2 * fase)
                samples.append(int(32767 * 0.09 * envelope * (onda + harmonia)))

        return pygame.mixer.Sound(buffer=samples.tobytes())
