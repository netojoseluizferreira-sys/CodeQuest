"""Renderização das telas gerais do CodeQuest em Pygame."""

import math
import pygame

from backend.xp_system import xp_para_proximo_nivel
from backend.worlds import obter_mundo
from pygame_client.menu_config import CUTSCENE_TEXTS, WORLD_MAP_BASE_SIZE, WORLD_MAP_HOTSPOTS, _BRANCO, _VERDE, _VERDE_CLARO
from pygame_client.palette import PALETTE
from pygame_client.settings import WINDOW
from pygame_client.ui import quebrar_texto, quebrar_texto_multilinha
from utils.asset_paths import data_path
from utils.database import carregar_usuario, listar_conquistas_com_estado


class RenderMixin:
    """Desenha telas gerais que não pertencem diretamente ao fluxo de aula.

    Inclui menu inicial, criação de personagem, hub, seleção de mundos, perfil,
    cutscene e créditos. Os métodos consomem o estado mantido por
    `CodeQuestPygameMenu` e não retornam valores.
    """

    def _renderizar(self):
        """Renderiza a tela ativa e todos os botões por cima, depois chama display.flip."""
        if self.screen_name == "start":
            self._renderizar_fundo_video()
            self._renderizar_inicio()
        elif self.screen_name == "hub":
            self._renderizar_fundo_hub()
            self._renderizar_hub()
        elif self.screen_name == "profile":
            self._renderizar_fundo_perfil()
            self._renderizar_perfil()
        elif self.screen_name == "worlds":
            self._renderizar_fundo_mapa_mundos()
            self._renderizar_mundos()
        elif self.screen_name == "cutscene":
            self._renderizar_cutscene()
        else:
            if self.screen_name == "create":
                self._renderizar_fundo_perfil()
                self.screen.blit(self.lesson_overlay, (0, 0))
            elif self.screen_name == "credits":
                self.screen.fill((11, 25, 11))
            else:
                self.screen.fill(PALETTE.background)
            if self.screen_name == "create":
                self._renderizar_criacao()
            elif self.screen_name == "credits":
                self._renderizar_creditos()
            elif self.screen_name == "lesson":
                self._renderizar_fluxo_aprendizado()
            elif self.screen_name == "complete":
                self._renderizar_conclusao()

        mouse_pos = pygame.mouse.get_pos()
        _btn_font = self.font_start_btn if self.screen_name in {"start", "hub", "profile", "worlds"} else self.font_body
        botoes = self._botoes_tela()
        for button in botoes:
            button.draw(self.screen, _btn_font, mouse_pos)
        self._atualizar_cursor(mouse_pos, botoes)
        pygame.display.flip()

    def _renderizar_fundo_video(self):
        """Blita o frame atual da animação de fundo da tela inicial e avança o timer."""
        if not self.video_frame_paths:
            self.screen.fill(PALETTE.background)
            return
        self.video_frame_timer += 1
        if self.video_frame_timer >= 2:
            self.video_frame_timer = 0
            self.video_frame_index = (self.video_frame_index + 1) % len(self.video_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.video_frame_paths, self.video_frame_index), (0, 0))

    def _renderizar_fundo_hub(self):
        """Blita o frame atual da animação de fundo do hub e avança o timer."""
        if not self.hub_frame_paths:
            self.screen.fill((20, 40, 20))
            return
        self.hub_frame_timer += 1
        if self.hub_frame_timer >= 2:
            self.hub_frame_timer = 0
            self.hub_frame_index = (self.hub_frame_index + 1) % len(self.hub_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.hub_frame_paths, self.hub_frame_index), (0, 0))

    def _renderizar_fundo_perfil(self):
        """Blita o frame atual da animação de fundo do perfil e avança o timer."""
        if not self.perfil_frame_paths:
            self.screen.fill((11, 25, 11))
            return
        self.perfil_frame_timer += 1
        if self.perfil_frame_timer >= 2:
            self.perfil_frame_timer = 0
            self.perfil_frame_index = (self.perfil_frame_index + 1) % len(self.perfil_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.perfil_frame_paths, self.perfil_frame_index), (0, 0))

    def _renderizar_fundo_mundos(self):
        """Blita o frame atual da animação de fundo da tela de mundos e avança o timer."""
        if not self.mundos_frame_paths:
            self.screen.fill((20, 40, 20))
            return
        self.mundos_frame_timer += 1
        if self.mundos_frame_timer >= 2:
            self.mundos_frame_timer = 0
            self.mundos_frame_index = (self.mundos_frame_index + 1) % len(self.mundos_frame_paths)
        self.screen.blit(self._obter_frame_animado(self.mundos_frame_paths, self.mundos_frame_index), (0, 0))

    def _renderizar_fundo_mapa_mundos(self):
        """Desenha o fundo do castelo escurecido para o mapa do arquipelago."""
        fundo = self.world_backgrounds.get("mundo_9")
        if fundo:
            self.screen.blit(fundo, (0, 0))
        else:
            self._renderizar_fundo_mundos()
        sombra = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 172))
        self.screen.blit(sombra, (0, 0))

    def _retangulo_mapa_mundos(self):
        """Retorna a moldura do mapa, mantendo a proporcao da imagem original."""
        base_w, base_h = WORLD_MAP_BASE_SIZE
        max_w, max_h = 900, 506
        escala = min(max_w / base_w, max_h / base_h)
        largura = int(base_w * escala)
        altura = int(base_h * escala)
        rect = pygame.Rect(0, 0, largura, altura)
        rect.center = (WINDOW.width // 2, 362)
        return rect

    def _hotspots_mapa_mundos(self):
        """Calcula as areas clicaveis dos mundos dentro do mapa renderizado."""
        mapa_rect = self._retangulo_mapa_mundos()
        hotspots = []
        for mundo_id, dados in WORLD_MAP_HOTSPOTS.items():
            x, y, w, h = dados["rect"]
            rect = pygame.Rect(
                mapa_rect.x + int(mapa_rect.w * x / 100),
                mapa_rect.y + int(mapa_rect.h * y / 100),
                int(mapa_rect.w * w / 100),
                int(mapa_rect.h * h / 100),
            )
            hotspots.append((mundo_id, dados, rect))
        return hotspots

    def _mundo_no_mapa(self, pos):
        """Retorna o mundo clicado no mapa ou None."""
        for mundo_id, _dados, rect in self._hotspots_mapa_mundos():
            if rect.collidepoint(pos):
                return mundo_id
        return None

    def _renderizar_inicio(self):
        """Renderiza o overlay, título "CodeQuest" com glow pulsante e subtítulo da tela inicial."""
        self.screen.blit(self.start_overlay, (0, 0))

        # Titulo renderizado letra por letra com espaçamento manual uniforme
        _TITULO = "CodeQuest"
        _GAP = 2  # pixels extras entre caracteres alem da largura individual
        _char_w = [self.font_title_large.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title_large.get_height()
        _tcy = 270  # centro vertical do titulo

        # Glow verde pulsante por tras do titulo
        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title_large.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        # Sombra do titulo (offset +3px)
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title_large.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        # Titulo principal branco
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title_large.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        # Subtitulo com sombra nas letras deslocada 2px
        _subtitulo = "Uma Jornada pelo Arquipélago de Bythos"
        _sub_som = self.font_subtitle_small.render(_subtitulo, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 327)))
        _sub_surf = self.font_subtitle_small.render(_subtitulo, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 325)))

        if self.status_kind in {"success", "error"}:
            self._desenhar_status(600)

    def _renderizar_criacao(self):
        """Renderiza o título "Criar personagem" com glow e os campos nome/idade."""
        _TITULO = "Criar personagem"
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 120

        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "Defina quem vai explorar Bythos"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 187)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 185)))

        _lbl = self.font_credit_body_bold.render("Nome do aventureiro", True, _BRANCO)
        self.screen.blit(_lbl, (390, 252))
        self._desenhar_input_verde(pygame.Rect(390, 285, 500, 50), self.nome_input, "nome", "Digite seu nome")

        _lbl = self.font_credit_body_bold.render("Idade", True, _BRANCO)
        self.screen.blit(_lbl, (390, 352))
        self._desenhar_input_verde(pygame.Rect(390, 385, 220, 50), self.idade_input, "idade", "18")

        if self.status_kind in {"success", "error"}:
            self._desenhar_status_hub(610)

    def _renderizar_hub(self):
        """Renderiza o hub com overlay, título "Menu de Jornada", saudação ao jogador e status."""
        self.screen.blit(self.hub_overlay, (0, 0))

        nome = self.usuario.nome if self.usuario else "Aventureiro"

        _TITULO = "Menu de Jornada"
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 255

        self.hub_glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.hub_glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = f"Bem-vindo, {nome}"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 327)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 325)))

        if self.status_kind in {"success", "error"}:
            self._desenhar_status_hub(665)

    def _desenhar_status_hub(self, y):
        """Desenha feedback centralizado para telas de hub e criação.

        Usa banner verde para sucesso e texto vermelho com sombra para erro,
        mantendo o aviso de erro visualmente separado dos botoes.

        Recebe:
            y (int): Coordenada vertical do centro do feedback.
        """
        color = PALETTE.success if self.status_kind == "success" else PALETTE.error
        font = self.font_hub_subtitle if self.status_kind == "error" else self.font_status_success
        linhas = quebrar_texto_multilinha(self.status_message, font, WINDOW.width - 200)
        linha_altura = font.get_linesize()
        if self.status_kind == "error":
            texto_y = y - (len(linhas) * linha_altura) // 2
            for linha in linhas:
                sombra = font.render(linha, True, (0, 0, 0))
                self.screen.blit(sombra, sombra.get_rect(center=(WINDOW.width // 2 + 2, texto_y + linha_altura // 2 + 2)))
                surface = font.render(linha, True, color)
                self.screen.blit(surface, surface.get_rect(center=(WINDOW.width // 2, texto_y + linha_altura // 2)))
                texto_y += linha_altura
            return

        max_w = max(font.size(l)[0] for l in linhas)
        box_w = min(max_w + 56, WINDOW.width - 170)
        altura = max(48, len(linhas) * linha_altura + 16)
        rect = pygame.Rect(WINDOW.width // 2 - box_w // 2, y - altura // 2, box_w, altura)
        pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, width=2, border_radius=10)
        texto_y = rect.y + 8
        for linha in linhas:
            sombra = font.render(linha, True, (0, 0, 0))
            self.screen.blit(sombra, sombra.get_rect(center=(rect.centerx + 2, texto_y + linha_altura // 2 + 2)))
            surface = font.render(linha, True, _BRANCO)
            self.screen.blit(surface, surface.get_rect(center=(rect.centerx, texto_y + linha_altura // 2)))
            texto_y += linha_altura

    def _renderizar_mundos_grade_antiga(self):
        """Renderiza a tela de seleção de mundos com fundo animado, título com glow e caixa de aviso."""
        self.screen.blit(self.mundos_overlay, (0, 0))

        _TITULO = "Arquipélago de Bythos"
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 175

        self.mundos_glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.mundos_glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "Escolha o próximo destino"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 242)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 240)))

        # Caixa de aviso com a mensagem de status
        _aviso_font = self.font_status_success
        _aviso_linhas = []
        for _parte in self.status_message.splitlines():
            _aviso_linhas.extend(quebrar_texto(_parte, _aviso_font, WINDOW.width - 340))
        _lh = _aviso_font.get_linesize()
        _pad = 12
        _aviso_h = len(_aviso_linhas) * _lh + _pad * 2
        _aviso_w = min(max(_aviso_font.size(l)[0] for l in _aviso_linhas) + 56, WINDOW.width - 300)
        _aviso_rect = pygame.Rect(WINDOW.width // 2 - _aviso_w // 2, 548, _aviso_w, _aviso_h)
        _cor_borda_aviso = _VERDE_CLARO
        if self.status_kind == "success":
            _cor_borda_aviso = PALETTE.success
        elif self.status_kind == "error":
            _cor_borda_aviso = PALETTE.error
        pygame.draw.rect(self.screen, (20, 55, 30), _aviso_rect, border_radius=10)
        pygame.draw.rect(self.screen, _cor_borda_aviso, _aviso_rect, width=2, border_radius=10)
        _ty = _aviso_rect.y + _pad
        for _l in _aviso_linhas:
            _ss = _aviso_font.render(_l, True, (0, 0, 0))
            self.screen.blit(_ss, _ss.get_rect(center=(_aviso_rect.centerx + 1, _ty + _lh // 2 + 1)))
            _ss = _aviso_font.render(_l, True, _BRANCO)
            self.screen.blit(_ss, _ss.get_rect(center=(_aviso_rect.centerx, _ty + _lh // 2)))
            _ty += _lh

    def _renderizar_mundos(self):
        """Renderiza o mapa clicavel do Arquipelago de Bythos."""
        _titulo = "Arquipelago de Bythos"
        _gap = 2
        _char_w = [self.font_title.size(c)[0] for c in _titulo]
        _total_w = sum(_char_w) + _gap * (len(_titulo) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 58

        self.mundos_glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.mundos_glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _titulo]
        for _surf in _glow_surfs:
            _surf.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _idx, _surf in enumerate(_glow_surfs):
                        self.screen.blit(_surf, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_idx] + _gap

        _x = _tx0
        for _idx, _char in enumerate(_titulo):
            self.screen.blit(self.font_title.render(_char, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_idx] + _gap
        _x = _tx0
        for _idx, _char in enumerate(_titulo):
            self.screen.blit(self.font_title.render(_char, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_idx] + _gap

        _sub = "Clique em uma construcao para entrar no mundo"
        _sub_shadow = self.font_small.render(_sub, True, (0, 0, 0))
        _sub_surf = self.font_small.render(_sub, True, _VERDE_CLARO)
        self.screen.blit(_sub_shadow, _sub_shadow.get_rect(center=(WINDOW.width // 2 + 2, 104)))
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 102)))

        _mapa_rect = self._retangulo_mapa_mundos()
        _moldura_rect = _mapa_rect.inflate(24, 24)
        pygame.draw.rect(self.screen, (5, 18, 12), _moldura_rect, border_radius=10)
        pygame.draw.rect(self.screen, _VERDE_CLARO, _moldura_rect, width=8, border_radius=10)
        pygame.draw.rect(self.screen, (215, 255, 205), _mapa_rect.inflate(6, 6), width=2, border_radius=6)

        if self.bythos_world_map:
            _mapa = pygame.transform.smoothscale(self.bythos_world_map, _mapa_rect.size)
            self.screen.blit(_mapa, _mapa_rect.topleft)
        else:
            pygame.draw.rect(self.screen, (10, 38, 24), _mapa_rect)

        _mouse_pos = pygame.mouse.get_pos()
        _hovered = None
        _pulse = int(8 + 5 * abs(math.sin(self.mundos_glow_timer * 0.08)))
        for _mundo_id, _dados, _rect in self._hotspots_mapa_mundos():
            _foco = _rect.collidepoint(_mouse_pos)
            if _foco:
                _hovered = (_mundo_id, _dados, _rect)
            _cx, _cy = _rect.center
            _raio = _pulse + (5 if _foco else 0)
            pygame.draw.circle(self.screen, (80, 255, 120), (_cx, _cy), _raio, 2)
            pygame.draw.circle(self.screen, (17, 120, 52), (_cx, _cy), 7)
            pygame.draw.circle(self.screen, (230, 255, 210), (_cx, _cy), 3)

        self._renderizar_info_mapa_mundos(_hovered)

    def _renderizar_info_mapa_mundos(self, hovered):
        """Desenha apenas nome e descricao do mundo sob o mouse."""
        _titulo_font = self.font_block_title
        _body_font = self.font_small

        if self.status_kind == "error" and self.status_message:
            _titulo = "Acesso bloqueado"
            _linhas = []
            for _parte in self.status_message.splitlines():
                _linhas.extend(quebrar_texto(_parte, _body_font, 760))
            _cor = PALETTE.error
        elif self.status_message.startswith("EM BREVE!"):
            _titulo = "Em breve"
            _linhas = []
            for _parte in self.status_message.splitlines():
                _linhas.extend(quebrar_texto(_parte, _body_font, 760))
            _cor = _VERDE_CLARO
        elif hovered is None:
            _titulo = "Passe o mouse sobre um local"
            _linhas = ["Clique em uma construcao do mapa para acessar a aula."]
            _cor = _VERDE_CLARO
        else:
            _mundo_id, _dados, _rect = hovered
            _mundo = obter_mundo(_mundo_id)
            if _mundo:
                _titulo = f"{_mundo['numero']} - {_mundo['nome']}"
            else:
                _titulo = _dados["titulo"]
            _linhas = [_dados["descricao"]]
            _cor = _VERDE_CLARO

        _linhas_quebradas = []
        for _linha in _linhas:
            _linhas_quebradas.extend(quebrar_texto(_linha, _body_font, 760))

        _max_text_w = _titulo_font.size(_titulo)[0]
        for _linha in _linhas_quebradas:
            _max_text_w = max(_max_text_w, _body_font.size(_linha)[0])
        _panel_w = min(max(_max_text_w + 56, 420), WINDOW.width - 360)
        _title_h = _titulo_font.get_linesize()
        _body_h = _body_font.get_linesize()
        _panel_h = min(86, max(58, 18 + _title_h + 4 + len(_linhas_quebradas) * _body_h + 12))
        _mapa_rect = self._retangulo_mapa_mundos()
        _panel_y = min(_mapa_rect.bottom + 46, WINDOW.height - 92 - _panel_h)
        _panel_rect = pygame.Rect(WINDOW.width // 2 - _panel_w // 2, _panel_y, _panel_w, _panel_h)

        pygame.draw.rect(self.screen, (7, 22, 14), _panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, _VERDE_CLARO, _panel_rect, width=2, border_radius=10)

        _titulo_sombra = _titulo_font.render(_titulo, True, (0, 0, 0))
        _titulo_surf = _titulo_font.render(_titulo, True, _cor)
        _y = _panel_rect.y + 10
        self.screen.blit(_titulo_sombra, _titulo_sombra.get_rect(center=(_panel_rect.centerx + 2, _y + _title_h // 2 + 2)))
        self.screen.blit(_titulo_surf, _titulo_surf.get_rect(center=(_panel_rect.centerx, _y + _title_h // 2)))

        _y += _title_h + 4
        for _linha in _linhas_quebradas:
            if _y + _body_h > _panel_rect.bottom - 8:
                break
            _sombra = _body_font.render(_linha, True, (0, 0, 0))
            _texto = _body_font.render(_linha, True, _BRANCO)
            self.screen.blit(_sombra, _sombra.get_rect(center=(_panel_rect.centerx + 1, _y + _body_h // 2 + 1)))
            self.screen.blit(_texto, _texto.get_rect(center=(_panel_rect.centerx, _y + _body_h // 2)))
            _y += _body_h

    def _renderizar_perfil(self):
        """Renderiza o perfil do usuário com quatro cards de estatísticas e seção de conquistas."""
        self.screen.blit(self.perfil_overlay, (0, 0))

        self.usuario = carregar_usuario()
        if self.usuario is None:
            self._desenhar_paragrafo("Nenhum personagem criado ainda.", 360, 300, 560, self.font_body, PALETTE.text)
            return

        _TITULO = self.usuario.nome
        _GAP = 2
        _char_w = [self.font_title.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = self.font_title.get_height()
        _tcy = 120

        self.glow_timer += 1
        _glow_alpha = int(40 + 80 * abs(math.sin(self.glow_timer * 0.04)))
        _glow_surfs = [self.font_title.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _glow_surfs:
            _s.set_alpha(_glow_alpha)
        for _spread in (8, 5, 2):
            for _dx in (-_spread, 0, _spread):
                for _dy in (-_spread, 0, _spread):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_glow_surfs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, (0, 0, 0))
            self.screen.blit(_s, (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP

        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            _s = self.font_title.render(_c, True, _BRANCO)
            self.screen.blit(_s, (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "Seu progresso em Bythos"
        _sub_som = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_sub_som, _sub_som.get_rect(center=(WINDOW.width // 2 + 2, 187)))
        _sub_surf = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_sub_surf, _sub_surf.get_rect(center=(WINDOW.width // 2, 185)))

        _CW, _CH = 280, 140
        _HGAP, _VGAP = 40, 25
        _GX = WINDOW.width // 2 - (_CW * 2 + _HGAP) // 2
        _GY = 230
        _COR_FUNDO = (30, 80, 50)
        _COR_BORDA = (100, 200, 120)

        cards = [
            ("Nível", str(self.usuario.nivel)),
            ("XP Total", str(self.usuario.xp)),
            ("Prox. Nível", str(xp_para_proximo_nivel(self.usuario.xp))),
            ("Idade", str(self.usuario.idade)),
        ]
        for idx, (label, valor) in enumerate(cards):
            col = idx % 2
            row = idx // 2
            cx = _GX + col * (_CW + _HGAP)
            cy = _GY + row * (_CH + _VGAP)
            rect = pygame.Rect(cx, cy, _CW, _CH)
            pygame.draw.rect(self.screen, _COR_FUNDO, rect, border_radius=12)
            pygame.draw.rect(self.screen, _COR_BORDA, rect, width=2, border_radius=12)
            _lbl_surf = self.font_profile_label.render(label, True, _COR_BORDA)
            self.screen.blit(_lbl_surf, _lbl_surf.get_rect(center=(cx + _CW // 2, cy + 36)))
            _val_surf = self.font_profile_value.render(valor, True, _BRANCO)
            self.screen.blit(_val_surf, _val_surf.get_rect(center=(cx + _CW // 2, cy + 96)))

        _sect_y = _GY + 2 * (_CH + _VGAP)
        _sect_rect = pygame.Rect(_GX, _sect_y, _CW * 2 + _HGAP, 130)
        pygame.draw.rect(self.screen, _COR_FUNDO, _sect_rect, border_radius=12)
        pygame.draw.rect(self.screen, _COR_BORDA, _sect_rect, width=2, border_radius=12)
        _conq_lbl = self.font_profile_label.render("Conquistas", True, _COR_BORDA)
        self.screen.blit(_conq_lbl, _conq_lbl.get_rect(center=(_sect_rect.centerx, _sect_rect.y + 28)))
        self._desenhar_conquistas_perfil(_sect_rect)

    def _desenhar_conquistas_perfil(self, section_rect):
        """Desenha os slots visuais de conquistas e seus tooltips."""
        conquistas = listar_conquistas_com_estado(self.usuario)
        mouse_pos = pygame.mouse.get_pos()
        self.achievement_slot_rects = []

        slot_size = 72
        icon_size = 52
        gap = 28
        total_width = len(conquistas) * slot_size + max(0, len(conquistas) - 1) * gap
        x = section_rect.centerx - total_width // 2
        y = section_rect.y + 48
        tooltip = None

        for conquista in conquistas:
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)
            hovered = slot_rect.collidepoint(mouse_pos)
            self.achievement_slot_rects.append(slot_rect)

            fundo = (14, 54, 25) if not hovered else (22, 78, 36)
            borda = _VERDE_CLARO if hovered else (100, 200, 120)
            pygame.draw.rect(self.screen, fundo, slot_rect, border_radius=8)
            pygame.draw.rect(self.screen, borda, slot_rect, width=2, border_radius=8)
            if hovered:
                pygame.draw.rect(self.screen, _VERDE_CLARO, slot_rect.inflate(10, 10), width=2, border_radius=10)

            imagem = self._carregar_imagem_conquista(conquista["imagem"], icon_size)
            if imagem is not None:
                self.screen.blit(imagem, imagem.get_rect(center=slot_rect.center))

            if hovered:
                tooltip = (conquista["tooltip_titulo"], conquista["tooltip_texto"], slot_rect)
            x += slot_size + gap

        if tooltip:
            self._desenhar_tooltip_conquista(*tooltip)

    def _carregar_imagem_conquista(self, caminho_relativo, tamanho):
        """Carrega e escala um icone de conquista usando cache local."""
        if not hasattr(self, "_achievement_image_cache"):
            self._achievement_image_cache = {}
        caminho = data_path(caminho_relativo)
        chave = (caminho, tamanho)
        if chave in self._achievement_image_cache:
            return self._achievement_image_cache[chave]
        if not caminho.exists():
            return None

        imagem = pygame.image.load(str(caminho)).convert_alpha()
        imagem = pygame.transform.smoothscale(imagem, (tamanho, tamanho))
        self._achievement_image_cache[chave] = imagem
        return imagem

    def _desenhar_tooltip_conquista(self, titulo, texto, slot_rect):
        """Renderiza o tooltip textual de uma conquista."""
        font_titulo = self.font_credit_small_bold
        font_texto = self.font_small
        linhas_texto = quebrar_texto(texto, font_texto, 300)
        largura = max([font_titulo.size(titulo)[0]] + [font_texto.size(linha)[0] for linha in linhas_texto]) + 28
        altura = font_titulo.get_linesize() + len(linhas_texto) * font_texto.get_linesize() + 24
        x = min(slot_rect.centerx - largura // 2, WINDOW.width - largura - 20)
        x = max(20, x)
        y = max(20, slot_rect.y - altura - 10)
        rect = pygame.Rect(x, y, largura, altura)

        pygame.draw.rect(self.screen, (10, 32, 18), rect, border_radius=8)
        pygame.draw.rect(self.screen, _VERDE_CLARO, rect, width=2, border_radius=8)
        self.screen.blit(font_titulo.render(titulo, True, _VERDE_CLARO), (rect.x + 14, rect.y + 10))
        texto_y = rect.y + 10 + font_titulo.get_linesize()
        for linha in linhas_texto:
            self.screen.blit(font_texto.render(linha, True, _BRANCO), (rect.x + 14, texto_y))
            texto_y += font_texto.get_linesize()

    def _renderizar_cutscene(self):
        """Renderiza a cena atual da cutscene com três estados de fade.

        Estados:
        - "fade_out_entry": hub escurece para preto (único fade — ocorre só na entrada).
        - "fade_in": primeira cena aparece saindo do preto.
        - "visible": cena visível, transições entre cenas são instantâneas.

        Renderiza: fundo imagem_cut.jpeg com overlay escuro; imagem principal 960×400
        centralizada com glow pulsante e borda arredondada; caixa de texto estilo
        alerta abaixo da imagem; caixa-contador no canto inferior esquerdo; botões
        "Pular história" e "Avançar →" lado a lado no canto inferior direito.
        """
        _FADE_SPEED = 8
        _IMG_W, _IMG_H = 900, 500
        _IMG_X = (WINDOW.width - _IMG_W) // 2
        _IMG_Y = 50
        _BTN_W, _BTN_H = 190, 45
        _BTN_Y = WINDOW.height - 65
        _BTN2_X = WINDOW.width - 20 - _BTN_W
        _BTN1_X = _BTN2_X - 10 - _BTN_W
        _ARROW_RECT = pygame.Rect(_BTN2_X, _BTN_Y, _BTN_W, _BTN_H)
        _PULAR_RECT = pygame.Rect(_BTN1_X, _BTN_Y, _BTN_W, _BTN_H)

        # Fase de entrada: hub escurecendo para preto — único fade do modo cutscene
        if self.cutscene_fade_state == "fade_out_entry":
            if self._cutscene_prev_frame:
                self.screen.blit(self._cutscene_prev_frame, (0, 0))
            else:
                self.screen.fill((0, 0, 0))
            self.cutscene_fade_alpha = min(255, self.cutscene_fade_alpha + _FADE_SPEED)
            _ov = pygame.Surface((WINDOW.width, WINDOW.height))
            _ov.fill((0, 0, 0))
            _ov.set_alpha(self.cutscene_fade_alpha)
            self.screen.blit(_ov, (0, 0))
            if self.cutscene_fade_alpha >= 255:
                self.cutscene_fade_state = "fade_in"
                self.cutscene_fade_alpha = 255
            return

        # Fundo: imagem_cut.jpeg escalada + overlay escuro semitransparente
        if self.cutscene_bg:
            self.screen.blit(self.cutscene_bg, (0, 0))
            _bg_ov = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
            _bg_ov.fill((0, 0, 0, 150))
            self.screen.blit(_bg_ov, (0, 0))
        else:
            self.screen.fill((11, 25, 11))

        # Glow pulsante ao redor da imagem principal
        _gt = pygame.time.get_ticks()
        _g_a = int(40 + 60 * abs(math.sin(_gt * 0.0015)))
        _glow_surf = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
        for _sp, _fa in ((16, max(0, _g_a // 5)), (10, max(0, _g_a // 3)), (5, max(0, _g_a // 2))):
            pygame.draw.rect(
                _glow_surf, (*_VERDE_CLARO, _fa),
                pygame.Rect(_IMG_X - _sp, _IMG_Y - _sp, _IMG_W + _sp * 2, _IMG_H + _sp * 2),
                border_radius=12 + _sp,
            )
        self.screen.blit(_glow_surf, (0, 0))

        # Imagem principal com máscara e borda arredondadas para esconder quinas.
        _img = self.cutscene_images[self.cutscene_index] if self.cutscene_index < len(self.cutscene_images) else None
        if _img:
            _img_round = pygame.Surface((_IMG_W, _IMG_H), pygame.SRCALPHA)
            _img_round.blit(_img, (0, 0))
            _mask = pygame.Surface((_IMG_W, _IMG_H), pygame.SRCALPHA)
            pygame.draw.rect(_mask, _BRANCO, _mask.get_rect(), border_radius=16)
            _img_round.blit(_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(_img_round, (_IMG_X, _IMG_Y))
        else:
            pygame.draw.rect(self.screen, (20, 50, 30), pygame.Rect(_IMG_X, _IMG_Y, _IMG_W, _IMG_H), border_radius=16)
        pygame.draw.rect(
            self.screen, _VERDE_CLARO,
            pygame.Rect(_IMG_X, _IMG_Y, _IMG_W, _IMG_H),
            width=6, border_radius=16,
        )

        # Caixa de texto estilo alerta abaixo da imagem
        _font = self.font_cutscene_text
        _text_max_w = _IMG_W - 56
        _linhas = quebrar_texto(CUTSCENE_TEXTS[self.cutscene_index], _font, _text_max_w)
        _lh = _font.get_linesize() + 2
        _pad = 14
        _box_h = len(_linhas) * _lh + _pad * 2
        _box_top = _IMG_Y + _IMG_H + 14
        _box_rect = pygame.Rect(_IMG_X, _box_top, _IMG_W, _box_h)
        pygame.draw.rect(self.screen, (20, 55, 30), _box_rect, border_radius=10)
        pygame.draw.rect(self.screen, _VERDE_CLARO, _box_rect, width=2, border_radius=10)
        _ty = _box_top + _pad
        _text_x = _box_rect.x + 28
        for _l in _linhas:
            _sombra = _font.render(_l, True, (0, 0, 0))
            self.screen.blit(_sombra, (_text_x + 1, _ty + 1))
            _surf = _font.render(_l, True, _BRANCO)
            self.screen.blit(_surf, (_text_x, _ty))
            _ty += _lh

        # Caixa-contador estilo alerta no canto inferior esquerdo
        _cnt_text = f"{self.cutscene_index + 1} / {len(CUTSCENE_TEXTS)}"
        _cnt_font = self.font_credit_section
        _cnt_w = _cnt_font.size(_cnt_text)[0] + 40
        _cnt_rect = pygame.Rect(20, _BTN_Y, _cnt_w, _BTN_H)
        pygame.draw.rect(self.screen, (20, 55, 30), _cnt_rect, border_radius=8)
        pygame.draw.rect(self.screen, _VERDE_CLARO, _cnt_rect, width=2, border_radius=8)
        _cnt_surf = _cnt_font.render(_cnt_text, True, _BRANCO)
        self.screen.blit(_cnt_surf, _cnt_surf.get_rect(center=_cnt_rect.center))

        # Botões "Pular história" e "Avançar →" lado a lado no canto inferior direito
        _mouse = pygame.mouse.get_pos()
        for _rect, _label in ((_PULAR_RECT, "Pular história"), (_ARROW_RECT, "Avançar →")):
            _hov = _rect.collidepoint(_mouse) and self.cutscene_fade_state == "visible"
            pygame.draw.rect(self.screen, _BRANCO if _hov else _VERDE, _rect, border_radius=8)
            pygame.draw.rect(self.screen, _VERDE_CLARO, _rect, width=2, border_radius=8)
            _b_surf = self.font_start_btn.render(_label, True, _VERDE if _hov else _BRANCO)
            self.screen.blit(_b_surf, _b_surf.get_rect(center=_rect.center))

        # Fade de entrada saindo do preto
        if self.cutscene_fade_state == "fade_in":
            self.cutscene_fade_alpha = max(0, self.cutscene_fade_alpha - _FADE_SPEED)
            if self.cutscene_fade_alpha == 0:
                self.cutscene_fade_state = "visible"

        if self.cutscene_fade_alpha > 0:
            _ov = pygame.Surface((WINDOW.width, WINDOW.height))
            _ov.fill((0, 0, 0))
            _ov.set_alpha(self.cutscene_fade_alpha)
            self.screen.blit(_ov, (0, 0))

    def _renderizar_creditos(self):
        """Renderiza os créditos com fundo e painel translúcido no padrão das aulas."""
        self.credit_link_rect = None
        if self.creditos_frame_paths:
            self.creditos_frame_timer += 1
            if self.creditos_frame_timer >= 6:
                self.creditos_frame_timer = 0
                self.creditos_frame_index = (self.creditos_frame_index + 1) % len(self.creditos_frame_paths)
            self.screen.blit(self._obter_frame_animado(self.creditos_frame_paths, self.creditos_frame_index), (0, 0))
            _cred_ov = pygame.Surface((WINDOW.width, WINDOW.height), pygame.SRCALPHA)
            _cred_ov.fill((0, 0, 0, 120))
            self.screen.blit(_cred_ov, (0, 0))
        else:
            self.screen.fill((11, 25, 11))

        _MARG = 118
        _CW = WINDOW.width - _MARG * 2
        _ft_titulo = self.font_lesson_title
        _ft_sub = self.font_hub_subtitle
        _ft_body = self.font_lesson_content
        _LH_SUB = _ft_sub.get_linesize() + 2
        _LH_BODY = _ft_body.get_linesize() + 4
        _ESPACO_SECAO = 28

        _secoes = [
            ("EQUIPE DE DESENVOLVIMENTO", [
                ("sub",   "Neto  —  Backend e Persistência"),
                ("body",  "Sistema de XP, SQLite, organização de dados e arquitetura."),
                ("space", ""),
                ("sub",   "Anthony  —  Interface e Experiência"),
                ("body",  "Telas Pygame, navegação, estilo visual e polimento de interação."),
                ("space", ""),
                ("sub",   "Mayanderson  —  Conteúdo e Pedagogia"),
                ("body",  "Aulas, exercícios, progressão pedagógica, narrativa e revisão."),
            ]),
            ("INSTITUIÇÃO E DISCIPLINA", [
                ("sub",  "Universidade Federal de Alagoas (UFAL)"),
                ("body", "Curso: Ciência da Computação — 1° Período"),
                ("body", "Disciplina: Algoritmos e Programação de Computadores"),
                ("body", "Professor: Alexandre Barbosa"),
            ]),
            ("TECNOLOGIAS UTILIZADAS", [
                ("body", "Python  |  Pygame  |  SQLite  |  Pytest  |  Git e GitHub"),
            ]),
            ("AGRADECIMENTOS", [
                ("body", "Ao Professor Alexandre Barbosa pela orientação ao longo da disciplina."),
                ("body", "Aos colegas que testaram o jogo e ajudaram com feedback."),
            ]),
            ("MENSAGEM FINAL", [
                ("body",  "Este projeto foi desenvolvido por Mayanderson, Neto e Anthony, alunos do primeiro período da UFAL."),
                ("space", ""),
                ("body",  "Obrigado por embarcar nessa jornada pelo Arquipélago de Bythos."),
                ("space", ""),
                ("body",  "Que o CodeQuest ajude a acender sua curiosidade por programação."),
            ]),
            ("DATA", [
                ("body", "Maio — Junho de 2025"),
            ]),
            ("LINKS", [
                ("link", "https://github.com/netojoseluizferreira-sys/CodeQuest"),
            ]),
        ]

        def _secao_h(linhas, titulo):
            """Calcula a altura total necessária para renderizar uma seção dos créditos."""
            h = _ft_sub.get_linesize() + 14
            for style, text in linhas:
                if style == "sub":
                    h += len(quebrar_texto(text, _ft_sub, _CW)) * _LH_SUB
                elif style in {"body", "link"}:
                    h += len(quebrar_texto(text, _ft_body, _CW)) * _LH_BODY
                elif style == "space":
                    h += 14
            return h

        _TITULO = "Créditos"
        _GAP = 2
        _char_w = [_ft_titulo.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = _ft_titulo.get_height()
        _tcy = 52

        self.lesson_glow_timer += 1
        _ga = int(40 + 80 * abs(math.sin(self.lesson_glow_timer * 0.04)))
        _gs = [_ft_titulo.render(c, True, _VERDE_CLARO) for c in _TITULO]
        for _s in _gs:
            _s.set_alpha(_ga)
        for _sp in (8, 5, 2):
            for _dx in (-_sp, 0, _sp):
                for _dy in (-_sp, 0, _sp):
                    if _dx == 0 and _dy == 0:
                        continue
                    _x = _tx0
                    for _i, _s in enumerate(_gs):
                        self.screen.blit(_s, (_x + _dx, _tcy - _char_h // 2 + _dy))
                        _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft_titulo.render(_c, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft_titulo.render(_c, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = "CodeQuest"
        _sub_y = _tcy + _char_h // 2 + 42
        _ss = _ft_sub.render(_sub, True, (0, 0, 0))
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2 + 2, _sub_y + 2)))
        _ss = _ft_sub.render(_sub, True, _BRANCO)
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2, _sub_y)))

        _AREA_TOP = _sub_y + _ft_sub.get_height() // 2 + 32
        _AREA_BOTTOM = WINDOW.height - 118
        _panel_rect = pygame.Rect(_MARG - 18, _AREA_TOP - 18, _CW + 36, _AREA_BOTTOM - _AREA_TOP + 36)
        _panel = pygame.Surface(_panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(_panel, (0, 0, 0, 118), _panel.get_rect(), border_radius=8)
        pygame.draw.rect(_panel, (*_VERDE_CLARO, 130), _panel.get_rect(), width=2, border_radius=8)
        self.screen.blit(_panel, _panel_rect.topleft)

        self.screen.set_clip(_panel_rect)

        y = _AREA_TOP - self.credit_scroll
        for _titulo_sec, _linhas in _secoes:
            _sh = _secao_h(_linhas, _titulo_sec)
            if y + _sh >= _panel_rect.top and y <= _panel_rect.bottom:
                _ty = y
                _titulo_sombra = _ft_sub.render(_titulo_sec, True, (0, 0, 0))
                _titulo_surf = _ft_sub.render(_titulo_sec, True, _VERDE_CLARO)
                pygame.draw.rect(
                    self.screen,
                    _VERDE_CLARO,
                    pygame.Rect(_MARG, _ty + 8, 4, _ft_sub.get_linesize()),
                    border_radius=2,
                )
                self.screen.blit(_titulo_sombra, (_MARG + 18 + 2, _ty + 2))
                self.screen.blit(_titulo_surf, (_MARG + 18, _ty))
                _ty += _ft_sub.get_linesize() + 14
                for style, text in _linhas:
                    if style == "sub":
                        for _sub in quebrar_texto(text, _ft_sub, _CW - 18):
                            _ss = _ft_sub.render(_sub, True, (0, 0, 0))
                            self.screen.blit(_ss, (_MARG + 18 + 2, _ty + 2))
                            _ss = _ft_sub.render(_sub, True, _BRANCO)
                            self.screen.blit(_ss, (_MARG + 18, _ty))
                            _ty += _LH_SUB
                    elif style in {"body", "link"}:
                        for _sub in quebrar_texto(text, _ft_body, _CW - 18):
                            _cor_texto = _VERDE_CLARO if style == "link" else _BRANCO
                            _shadow = _ft_body.render(_sub, True, (0, 0, 0))
                            _surf = _ft_body.render(_sub, True, _cor_texto)
                            self.screen.blit(_shadow, (_MARG + 18 + 2, _ty + 2))
                            _rect = self.screen.blit(_surf, (_MARG + 18, _ty))
                            if style == "link":
                                self.credit_link_rect = _rect if self.credit_link_rect is None else self.credit_link_rect.union(_rect)
                                pygame.draw.line(
                                    self.screen,
                                    _VERDE_CLARO,
                                    (_rect.left, _rect.bottom),
                                    (_rect.right, _rect.bottom),
                                    2,
                                )
                            _ty += _LH_BODY
                    elif style == "space":
                        _ty += 14
            y += _sh + _ESPACO_SECAO

        self.screen.set_clip(None)
