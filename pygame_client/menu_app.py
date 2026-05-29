import argparse

import pygame

from pygame_client.audio import AudioController
from pygame_client.api_client import CodeQuestApiClient
from pygame_client.credits import obter_linhas_creditos
from pygame_client.menu_actions import solicitar_continuar_jogo, solicitar_novo_jogo
from pygame_client.palette import PALETTE
from pygame_client.settings import WINDOW
from pygame_client.ui import Button, desenhar_texto_centralizado, quebrar_texto


class CodeQuestPygameMenu:
    """Aplicacao Pygame inicial para o menu do CodeQuest."""

    def __init__(self, api_url="http://127.0.0.1:8000"):
        """Inicializa o estado visual do menu.

        Recebe:
            api_url: URL base da API REST do CodeQuest.

        Retorna:
            None.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW.width, WINDOW.height))
        pygame.display.set_caption(WINDOW.title)
        self.clock = pygame.time.Clock()
        self.api_client = CodeQuestApiClient(api_url)
        self.audio = AudioController()
        self.audio.inicializar()
        self.font_title = pygame.font.SysFont("segoeui", 52, bold=True)
        self.font_subtitle = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 22)
        self.font_small = pygame.font.SysFont("segoeui", 18)
        self.running = True
        self.screen_name = "menu"
        self.status_message = f"Menu conectado em {api_url}. Escolha uma opcao."
        self.credit_scroll = 0
        self.buttons = self._criar_botoes_menu()

    def run(self):
        """Executa o loop principal da aplicacao.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.audio.tocar_trilha()
        while self.running:
            self._processar_eventos()
            self._renderizar()
            self.clock.tick(WINDOW.fps)

        self.audio.encerrar()
        pygame.quit()

    def _criar_botoes_menu(self):
        """Cria os botoes da tela inicial.

        Recebe:
            Nenhum parametro.

        Retorna:
            Lista de instancias Button configuradas.
        """
        largura = 320
        altura = 56
        x = (WINDOW.width - largura) // 2
        return [
            Button(pygame.Rect(x, 245, largura, altura), "Novo jogo", self._novo_jogo),
            Button(pygame.Rect(x, 315, largura, altura), "Continuar", self._continuar),
            Button(pygame.Rect(x, 385, largura, altura), "Creditos", self._abrir_creditos),
            Button(pygame.Rect(x, 455, largura, altura), "Sair", self._sair),
        ]

    def _processar_eventos(self):
        """Processa eventos de teclado, mouse e janela.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._sair()
            elif event.type == pygame.KEYDOWN:
                self._processar_tecla(event)
            elif self.screen_name == "menu":
                for button in self.buttons:
                    if button.handle_event(event):
                        self.audio.tocar_botao()
                        break

    def _processar_tecla(self, event):
        """Processa atalhos de teclado do menu.

        Recebe:
            event: Evento KEYDOWN recebido pelo Pygame.

        Retorna:
            None.
        """
        if event.key == pygame.K_ESCAPE:
            if self.screen_name == "credits":
                self.screen_name = "menu"
                self.credit_scroll = 0
            else:
                self._sair()
        elif self.screen_name == "credits" and event.key in (pygame.K_UP, pygame.K_w):
            self.credit_scroll = max(0, self.credit_scroll - 32)
        elif self.screen_name == "credits" and event.key in (pygame.K_DOWN, pygame.K_s):
            self.credit_scroll += 32

    def _renderizar(self):
        """Renderiza a tela ativa.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        if self.screen_name == "credits":
            self._renderizar_creditos()
        else:
            self._renderizar_menu()
        pygame.display.flip()

    def _renderizar_menu(self):
        """Renderiza a tela de menu principal.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.screen.fill(PALETTE.background)
        self._desenhar_cabecalho()

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.draw(self.screen, self.font_body, mouse_pos)

        desenhar_texto_centralizado(self.screen, self.status_message, self.font_small, PALETTE.muted, 555)
        desenhar_texto_centralizado(
            self.screen,
            "Apenas a tela de creditos esta funcional nesta etapa.",
            self.font_small,
            PALETTE.muted,
            585,
        )

    def _desenhar_cabecalho(self):
        """Desenha titulo e subtitulo do menu.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        pygame.draw.rect(self.screen, PALETTE.surface, pygame.Rect(0, 0, WINDOW.width, 180))
        pygame.draw.line(self.screen, PALETTE.border, (0, 180), (WINDOW.width, 180), 2)
        desenhar_texto_centralizado(self.screen, "CodeQuest", self.font_title, PALETTE.text, 72)
        desenhar_texto_centralizado(
            self.screen,
            "Uma Jornada pelo Arquipelago de Bythos",
            self.font_subtitle,
            PALETTE.accent,
            124,
        )

    def _renderizar_creditos(self):
        """Renderiza a tela de creditos com rolagem.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.screen.fill(PALETTE.background)
        y = 58 - self.credit_scroll
        largura_texto = WINDOW.width - 160

        for style, text in obter_linhas_creditos():
            font, color, spacing = self._estilo_credito(style)
            for line in quebrar_texto(text, font, largura_texto):
                desenhar_texto_centralizado(self.screen, line, font, color, y)
                y += spacing
            y += 8

        rodape = pygame.Rect(0, WINDOW.height - 54, WINDOW.width, 54)
        pygame.draw.rect(self.screen, PALETTE.surface, rodape)
        pygame.draw.line(self.screen, PALETTE.border, (0, WINDOW.height - 54), (WINDOW.width, WINDOW.height - 54), 2)
        desenhar_texto_centralizado(
            self.screen,
            "Use W/S ou setas para rolar. ESC volta ao menu.",
            self.font_small,
            PALETTE.muted,
            WINDOW.height - 27,
        )

    def _estilo_credito(self, style):
        """Resolve fonte, cor e espacamento de uma linha de creditos.

        Recebe:
            style: Nome do estilo da linha de creditos.

        Retorna:
            Tupla com fonte, cor RGB e espacamento vertical.
        """
        if style == "title":
            return self.font_title, PALETTE.primary, 58
        if style == "subtitle":
            return self.font_subtitle, PALETTE.accent, 36
        if style == "section":
            return self.font_subtitle, PALETTE.text, 38
        if style == "body":
            return self.font_body, PALETTE.text, 30
        if style == "quote":
            return self.font_small, PALETTE.accent, 26
        if style == "footer":
            return self.font_small, PALETTE.gold, 30
        return self.font_small, PALETTE.muted, 24

    def _novo_jogo(self):
        """Solicita novo jogo pela API e fecha o menu quando der certo.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        action = solicitar_novo_jogo(self.api_client)
        self.status_message = f"Preparado: {action.description}"
        if action.success:
            self._sair()

    def _continuar(self):
        """Solicita continuar jogo pela API e fecha o menu quando der certo.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        action = solicitar_continuar_jogo(self.api_client)
        self.status_message = f"Preparado: {action.description}"
        if action.success:
            self._sair()

    def _abrir_creditos(self):
        """Abre a tela de creditos.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.audio.tocar_creditos()
        self.screen_name = "credits"
        self.credit_scroll = 0

    def _sair(self):
        """Encerra o loop principal.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self.running = False


def main():
    """Executa o menu Pygame inicial do CodeQuest.

    Recebe:
        Nenhum parametro.

    Retorna:
        None.
    """
    parser = argparse.ArgumentParser(description="Menu Pygame inicial do CodeQuest.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000", help="URL base da API FastAPI.")
    args = parser.parse_args()
    CodeQuestPygameMenu(api_url=args.api_url).run()


if __name__ == "__main__":
    main()
