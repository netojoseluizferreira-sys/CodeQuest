import math
from array import array

import pygame


class AudioController:
    """Controla trilha sonora e efeitos sonoros gerados proceduralmente em memória."""

    def __init__(self, sample_rate=44100):
        """Configura os atributos iniciais sem inicializar o mixer.

        Recebe:
            sample_rate (int): Taxa de amostragem em Hz usada na geração de áudio.
            O mixer só é aberto quando inicializar() for chamado.
        """
        self.sample_rate = sample_rate
        self.enabled = False
        self.music_channel = None
        self.button_sound = None
        self.credit_sound = None

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
            self.enabled = True
        except pygame.error:
            self.enabled = False
        return self.enabled

    def tocar_trilha(self):
        """Gera e toca a trilha de fundo em loop infinito no canal 0.

        Só executa quando o áudio estiver habilitado e o canal disponível.
        O volume do canal é fixado em 0.28 para não cobrir os efeitos.
        """
        if not self.enabled or self.music_channel is None:
            return
        trilha = self._criar_trilha()
        self.music_channel.set_volume(0.28)
        self.music_channel.play(trilha, loops=-1)

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

    def encerrar(self):
        """Finaliza o mixer do Pygame quando o áudio estiver ativo."""
        if self.enabled:
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
