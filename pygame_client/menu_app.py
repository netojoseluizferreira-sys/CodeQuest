"""Aplicação Pygame principal do CodeQuest e composição do menu."""

import glob
import os

import pygame

from backend.worlds import listar_mundos
from pygame_client.audio import AudioController
from pygame_client.menu_buttons import ButtonMixin
from pygame_client.menu_config import AULA_ATIVA, MUNDO_ATIVO
from pygame_client.menu_events import EventMixin
from pygame_client.menu_learning_rendering import LearningRenderMixin
from pygame_client.menu_navigation import NavigationMixin
from pygame_client.menu_rendering import RenderMixin
from pygame_client.settings import WINDOW
from utils.database import carregar_usuario


class CodeQuestPygameMenu(ButtonMixin, EventMixin, RenderMixin, LearningRenderMixin, NavigationMixin):
    """Controla o loop principal e reúne os mixins de botões, eventos, render e navegação."""

    def __init__(self):
        """Inicializa Pygame, carrega fontes/imagens/vídeos e restaura o save do usuário.

        Configura a janela 1280×800, o AudioController, as fontes PressStart2P,
        RammettoOne e WendyOne, os frames de vídeo de fundo (start, hub, créditos, perfil),
        as imagens da cutscene (data/cutscenes/1-10.jpeg) e os atributos de estado
        de tela, campo ativo, cutscene fade e fluxo de aprendizagem.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW.width, WINDOW.height))
        pygame.display.set_caption(WINDOW.title)
        self.clock = pygame.time.Clock()
        self.audio = AudioController()
        self.audio.inicializar()
        _data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        _wendyone = os.path.join(_data_dir, "WendyOne-Regular.ttf")
        _pressstart = os.path.join(_data_dir, "PressStart2P-Regular.ttf")
        _rammetto = os.path.join(_data_dir, "RammettoOne-Regular.ttf")
        self.font_title = pygame.font.Font(_pressstart, 52)
        self.font_title_large = pygame.font.Font(_pressstart, 64)
        self.font_hub_subtitle = pygame.font.Font(_rammetto, 28)
        self.font_subtitle = pygame.font.Font(_rammetto, 28)
        _titulo_w = sum(self.font_title_large.size(c)[0] for c in "CodeQuest") + 2 * 8
        _sub_size = 22
        _sub_texto = "Uma Jornada pelo Arquipélago de Bythos"
        _font_sub = pygame.font.Font(_rammetto, _sub_size)
        while _font_sub.size(_sub_texto)[0] > _titulo_w and _sub_size > 8:
            _sub_size -= 1
            _font_sub = pygame.font.Font(_rammetto, _sub_size)
        self.font_subtitle_small = _font_sub
        self.font_start_btn = pygame.font.Font(_wendyone, 21)
        self.font_welcome = pygame.font.Font(_wendyone, 20)
        self.font_body = pygame.font.Font(_wendyone, 21)
        self.font_small = pygame.font.Font(_wendyone, 17)
        self.font_tiny = pygame.font.Font(_wendyone, 15)
        self.font_block_title = pygame.font.Font(_rammetto, 16)
        self.font_block_body = pygame.font.Font(_wendyone, 20)
        self.font_credit_section = pygame.font.Font(_rammetto, 23)
        self.font_credit_body_bold = pygame.font.Font(_wendyone, 22)
        self.font_cutscene_text = pygame.font.Font(_wendyone, 26)
        self.font_credit_body = pygame.font.Font(_wendyone, 22)
        self.font_credit_small_bold = pygame.font.Font(_rammetto, 16)
        self.font_credit_small_reg = pygame.font.Font(_wendyone, 20)
        self.font_credit_quote = pygame.font.Font(_wendyone, 18)
        self.font_credit_footer_bold = pygame.font.Font(_wendyone, 16)
        self.font_status_success = pygame.font.Font(_wendyone, 24)
        self.font_profile_label = pygame.font.Font(_rammetto, 19)
        self.font_profile_value = pygame.font.Font(_wendyone, 38)
        self.content_x = 150
        self.content_width = WINDOW.width - (self.content_x * 2)
        self.running = True
        self.screen_name = "start"
        self.status_message = "Bem-vindo ao CodeQuest."
        self.status_kind = "normal"
        self.usuario = carregar_usuario()
        self.credit_scroll = 0
        self.nome_input = ""
        self.idade_input = ""
        self.active_field = "nome"
        self.aula = None
        self.exercicios = {}
        self.mundo_ativo = MUNDO_ATIVO
        self.aula_ativa = AULA_ATIVA
        self.trilha_indice = 0
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self.link_rect = None
        self.credit_link_rect = None
        self._cursor_atual = None
        self.btn_continuar_y = None
        self._frame_cache = {}
        self._achievement_image_cache = {}
        self.achievement_slot_rects = []
        _frames_dir = os.path.join(_data_dir, "video_frames")
        self.video_frame_paths = sorted(glob.glob(os.path.join(_frames_dir, "*.jpg")))
        self.video_frame_index = 0
        self.video_frame_timer = 0
        self.glow_timer = 0
        self.start_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.start_overlay.fill((0, 0, 0, 140))
        _hub_frames_dir = os.path.join(_data_dir, "hub_frames")
        self.hub_frame_paths = sorted(glob.glob(os.path.join(_hub_frames_dir, "*.jpg")))
        self.hub_frame_index = 0
        self.hub_frame_timer = 0
        self.hub_glow_timer = 0
        self.hub_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.hub_overlay.fill((0, 0, 0, 140))
        _creditos_frames_dir = os.path.join(_data_dir, "creditos_frames")
        self.creditos_frame_paths = sorted(glob.glob(os.path.join(_creditos_frames_dir, "*.jpg")))
        self.creditos_frame_index = 0
        self.creditos_frame_timer = 0
        _cutscenes_dir = os.path.join(_data_dir, "cutscenes")
        self.cutscene_images = []
        for _i in range(1, 11):
            _cpath = os.path.join(_cutscenes_dir, f"{_i}.jpeg")
            if os.path.exists(_cpath):
                _cimg = pygame.image.load(_cpath).convert()
                self.cutscene_images.append(pygame.transform.scale(_cimg, (900, 500)))
            else:
                self.cutscene_images.append(None)
        self.cutscene_index = 0
        self.cutscene_fade_alpha = 0
        self.cutscene_fade_state = "visible"
        self.cutscene_fade_next = None
        self._cutscene_prev_frame = None
        _cut_bg_path = None
        for _ext in ("jpeg", "jpg", "png"):
            _p = os.path.join(_data_dir, f"imagem_cut.{_ext}")
            if os.path.exists(_p):
                _cut_bg_path = _p
                break
        if _cut_bg_path:
            _cbg = pygame.image.load(_cut_bg_path).convert()
            self.cutscene_bg = pygame.transform.scale(_cbg, (WINDOW.width, WINDOW.height))
        else:
            self.cutscene_bg = None
        self.world_backgrounds = {}
        self.world_overlays = {}
        for _mundo in listar_mundos():
            _background = _mundo.get("background")
            if not _background:
                continue
            _bg_path = os.path.join(_data_dir, _background)
            if os.path.exists(_bg_path):
                _bg = pygame.image.load(_bg_path).convert()
                self.world_backgrounds[_mundo["id"]] = pygame.transform.scale(_bg, (WINDOW.width, WINDOW.height))
                _overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
                _overlay.fill((0, 0, 0, int(_mundo.get("overlay_alpha", 185))))
                self.world_overlays[_mundo["id"]] = _overlay
        _perfil_frames_dir = os.path.join(_data_dir, "perfil_frames")
        self.perfil_frame_paths = sorted(glob.glob(os.path.join(_perfil_frames_dir, "*.jpg")))
        self.perfil_frame_index = 0
        self.perfil_frame_timer = 0
        self.perfil_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.perfil_overlay.fill((0, 0, 0, 120))
        _mundos_frames_dir = os.path.join(_data_dir, "mundos_frames")
        self.mundos_frame_paths = sorted(glob.glob(os.path.join(_mundos_frames_dir, "*.jpg")))
        self.mundos_frame_index = 0
        self.mundos_frame_timer = 0
        _mundo9_cutscene_dir = os.path.join(_data_dir, "mundo_9_cutscene_frames")
        self.mundo9_cutscene_frame_paths = sorted(glob.glob(os.path.join(_mundo9_cutscene_dir, "*.jpg")))
        self.mundo9_cutscene_frame_index = 0
        self.mundo9_cutscene_frame_acc = 0.0
        self.mundo9_cutscene_audio_started = False
        self.mundos_overlay = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        self.mundos_overlay.fill((0, 0, 0, 150))
        self.mundos_glow_timer = 0
        self.lesson_glow_timer = 0
        self.font_lesson_title = pygame.font.Font(_pressstart, 28)
        self.font_lesson_practice_title = pygame.font.Font(_pressstart, 24)
        self.font_lesson_content = pygame.font.Font(_wendyone, 20)
        self.font_lesson_body = pygame.font.Font(_wendyone, 20)
        _less_ov = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        _less_ov.fill((0, 0, 0, 160))
        self.lesson_overlay = _less_ov

    def run(self):
        """Inicia a trilha sonora e executa o loop principal a 60 fps até self.running ser False."""
        while self.running:
            contexto_musica = self._contexto_musica_atual()
            if contexto_musica is not None:
                self.audio.tocar_trilha(contexto_musica)
            self._processar_eventos()
            self._renderizar()
            self.clock.tick(WINDOW.fps)

        self.audio.encerrar()
        pygame.quit()

    def _contexto_musica_atual(self):
        """Retorna o contexto musical correspondente à tela atual.

        Retorna:
            str: Chave usada por AudioController.tocar_trilha para selecionar
            a faixa MP3 adequada ao momento do jogo.
        """
        if self.screen_name == "lesson":
            segmento = self._segmento_atual()
            if segmento and segmento["tipo"] == "cutscene_video":
                return None
            if segmento and segmento["tipo"] == "exercicios":
                return "exercise"
            return "lesson"
        if self.screen_name in {"start", "hub", "cutscene", "worlds", "profile", "credits", "complete"}:
            return self.screen_name
        if self.screen_name == "create":
            return "start"
        return "start"

    def _obter_frame_animado(self, frame_paths, frame_index):
        """Carrega e retorna um frame de fundo sob demanda.

        Recebe:
            frame_paths (list[str]): Caminhos dos frames da animacao.
            frame_index (int): Indice do frame desejado.

        Retorna:
            pygame.Surface | None: Frame escalado para a janela, ou None quando
            a lista de caminhos estiver vazia.
        """
        if not frame_paths:
            return None

        frame_path = frame_paths[frame_index % len(frame_paths)]
        if frame_path not in self._frame_cache:
            image = pygame.image.load(frame_path).convert()
            self._frame_cache[frame_path] = pygame.transform.scale(image, (WINDOW.width, WINDOW.height))
        return self._frame_cache[frame_path]

    def _atualizar_cursor(self, mouse_pos, botoes):
        """Troca o cursor apenas quando muda entre seta e mão de clique."""
        cursor = pygame.SYSTEM_CURSOR_HAND if self._deve_mostrar_cursor_mao(mouse_pos, botoes) else pygame.SYSTEM_CURSOR_ARROW
        if cursor == self._cursor_atual:
            return
        try:
            pygame.mouse.set_cursor(cursor)
        except pygame.error:
            return
        self._cursor_atual = cursor

    def _deve_mostrar_cursor_mao(self, mouse_pos, botoes):
        """Retorna True quando o mouse está sobre algo clicável."""
        if any(button.rect.collidepoint(mouse_pos) for button in botoes):
            return True
        if self.screen_name == "lesson" and self.link_rect and self.link_rect.collidepoint(mouse_pos):
            return True
        if self.screen_name == "credits" and self.credit_link_rect and self.credit_link_rect.collidepoint(mouse_pos):
            return True
        if self.screen_name == "cutscene" and self.cutscene_fade_state == "visible":
            btn_w, btn_h = 190, 45
            btn_y = WINDOW.height - 65
            btn2_x = WINDOW.width - 20 - btn_w
            btn1_x = btn2_x - 10 - btn_w
            return (
                pygame.Rect(btn1_x, btn_y, btn_w, btn_h).collidepoint(mouse_pos)
                or pygame.Rect(btn2_x, btn_y, btn_w, btn_h).collidepoint(mouse_pos)
            )
        return False

def main():
    """Instancia CodeQuestPygameMenu e inicia o loop principal do jogo."""
    CodeQuestPygameMenu().run()

if __name__ == "__main__":
    main()
