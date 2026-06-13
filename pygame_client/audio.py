import math
from array import array

import pygame


class AudioController:
    """Controla trilha sonora e efeitos simples gerados em memoria."""

    def __init__(self, sample_rate=44100):
        """Inicializa o controlador de audio.

        Recebe:
            sample_rate: Taxa de amostragem usada para gerar os sons.

        Retorna:
            None.
        """
        self.sample_rate = sample_rate
        self.enabled = False
        self.music_channel = None
        self.button_sound = None
        self.credit_sound = None

    def inicializar(self):
        """Inicializa o mixer e prepara os sons do menu.

        Recebe:
            Nenhum parametro.

        Retorna:
            True quando o audio foi inicializado; caso contrario, False.
        """
        try:
            pygame.mixer.pre_init(self.sample_rate, -16, 1, 512)
            pygame.mixer.init()
            self.music_channel = pygame.mixer.Channel(0)
            self.button_sound = self._criar_tom(660, 0.08, 0.18)
            self.credit_sound = self._criar_tom(880, 0.14, 0.14)
            self.enabled = True
        except pygame.error:
            self.enabled = False
        return self.enabled

    def tocar_trilha(self):
        """Toca uma trilha sonora simples em loop.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if not self.enabled or self.music_channel is None:
            return
        trilha = self._criar_trilha()
        self.music_channel.set_volume(0.28)
        self.music_channel.play(trilha, loops=-1)

    def tocar_botao(self):
        """Toca o efeito sonoro padrao dos botoes.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if self.enabled and self.button_sound:
            self.button_sound.play()

    def tocar_creditos(self):
        """Toca o efeito sonoro de abertura dos creditos.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if self.enabled and self.credit_sound:
            self.credit_sound.play()

    def encerrar(self):
        """Finaliza o mixer quando ele estiver ativo.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if self.enabled:
            pygame.mixer.quit()

    def _criar_tom(self, frequencia, duracao, volume):
        """Gera um efeito sonoro senoidal curto.

        Recebe:
            frequencia: Frequencia do tom em Hertz.
            duracao: Duracao do som em segundos.
            volume: Volume entre 0.0 e 1.0.

        Retorna:
            pygame.mixer.Sound com o tom gerado.
        """
        total = int(self.sample_rate * duracao)
        samples = array("h")
        for indice in range(total):
            envelope = 1 - (indice / total)
            onda = math.sin(2 * math.pi * frequencia * indice / self.sample_rate)
            samples.append(int(32767 * volume * envelope * onda))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _criar_trilha(self):
        """Gera uma trilha curta em loop com arpejos simples.

        Recebe:
            Nenhum parametro.

        Retorna:
            pygame.mixer.Sound com a trilha gerada.
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
