"""Renderização das telas de aula, exercício e conclusão."""

import math

import pygame

from pygame_client.menu_config import _BRANCO, _VERDE, _VERDE_CLARO
from pygame_client.palette import PALETTE
from pygame_client.settings import WINDOW
from pygame_client.ui import desenhar_texto_centralizado, quebrar_texto


class LearningRenderMixin:
    """Desenha o fluxo pedagógico: textos de aula, exercícios e conclusão.

    Espera que a classe principal tenha fontes, superfícies de fundo, estado da
    aula atual e métodos de consulta de segmento/exercício. Não persiste dados;
    apenas transforma o estado atual em elementos visuais.
    """

    def _renderizar_fluxo_aprendizado(self):
        """Despacha para _renderizar_segmento_aula ou _renderizar_segmento_exercicio conforme o segmento atual."""
        segmento = self._segmento_atual()
        if segmento is None:
            self.screen_name = "complete"
            return
        if segmento["tipo"] == "aula":
            self._renderizar_segmento_aula(segmento)
        else:
            self._renderizar_segmento_exercicio(segmento)

    def _desenhar_fundo_aprendizado(self):
        """Desenha o fundo das telas de aula, exercício e conclusão do mundo ativo."""
        mundo_bg = getattr(self, "world_backgrounds", {}).get(self.mundo_ativo)
        if mundo_bg:
            self.screen.blit(mundo_bg, (0, 0))
            mundo_overlay = getattr(self, "world_overlays", {}).get(self.mundo_ativo)
            if mundo_overlay:
                self.screen.blit(mundo_overlay, (0, 0))
            return

        if self.cutscene_bg:
            self.screen.blit(self.cutscene_bg, (0, 0))
        else:
            self.screen.fill((11, 25, 11))
        self.screen.blit(self.lesson_overlay, (0, 0))

    def _renderizar_segmento_aula(self, segmento):
        """Renderiza um segmento de aula sobre fundo imagem_cut com título glow, conteúdo e link YouTube."""
        self._desenhar_fundo_aprendizado()

        # Título PressStart2P com glow verde pulsante (igual à tela inicial)
        _TITULO = segmento["titulo"]
        _GAP = 2
        _ft = self.font_lesson_title
        _char_w = [_ft.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = _ft.get_height()
        _tcy = 52

        self.lesson_glow_timer += 1
        _ga = int(40 + 80 * abs(math.sin(self.lesson_glow_timer * 0.04)))
        _gs = [_ft.render(c, True, _VERDE_CLARO) for c in _TITULO]
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
            self.screen.blit(_ft.render(_c, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft.render(_c, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        # Subtítulo "Aula X: [nome da aula]" em RammettoOne branco com sombra preta
        _sub = self.aula["titulo"]
        _sub_y = _tcy + _char_h // 2 + 42
        _fes = self.font_hub_subtitle
        _ss = _fes.render(_sub, True, (0, 0, 0))
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2 + 2, _sub_y + 2)))
        _ss = _fes.render(_sub, True, _BRANCO)
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2, _sub_y)))

        # Corpo WendyOne em painel de leitura, com respiro e divisao em colunas quando necessario.
        _MARG = 118
        _cw = WINDOW.width - _MARG * 2
        _fc = self.font_lesson_body
        _lh = _fc.get_linesize() + 2
        _body_top = _sub_y + _fes.get_height() // 2 + 32
        _has_cta = bool(segmento.get("video_url"))
        _conteudo = segmento["conteudo"]
        if len(_conteudo) > 4:
            _meio = math.ceil(len(_conteudo) / 2)
            _colunas = [_conteudo[:_meio], _conteudo[_meio:]]
        else:
            _colunas = [_conteudo]

        _gap_col = 38 if len(_colunas) > 1 else 0
        _col_w = (_cw - _gap_col) // len(_colunas)
        _col_heights = []
        for _paragrafos in _colunas:
            _altura_coluna = 0
            for _para in _paragrafos:
                _altura_coluna += len(quebrar_texto(_para, _fc, _col_w - 18)) * _lh + 12
            _col_heights.append(max(0, _altura_coluna - 12))

        _panel_max_bottom = WINDOW.height - (250 if _has_cta else 118)
        _panel_h = min(max(max(_col_heights, default=0) + 36, 150), _panel_max_bottom - (_body_top - 18))
        _panel_rect = pygame.Rect(_MARG - 18, _body_top - 18, _cw + 36, _panel_h)
        _panel = pygame.Surface(_panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(_panel, (0, 0, 0, 118), _panel.get_rect(), border_radius=8)
        pygame.draw.rect(_panel, (*_VERDE_CLARO, 130), _panel.get_rect(), width=2, border_radius=8)
        self.screen.blit(_panel, _panel_rect.topleft)

        _max_y = _panel_rect.bottom - 18
        for _col_idx, _paragrafos in enumerate(_colunas):
            _x = _MARG + _col_idx * (_col_w + _gap_col)
            _y = _body_top
            for _para in _paragrafos:
                _linhas = quebrar_texto(_para, _fc, _col_w - 18)
                _accent_h = min(len(_linhas) * _lh - 4, _max_y - _y)
                if _accent_h > 0:
                    pygame.draw.rect(self.screen, _VERDE_CLARO, pygame.Rect(_x, _y + 4, 4, _accent_h), border_radius=2)
                for _linha in _linhas:
                    if _y + _lh > _max_y:
                        break
                    _shadow = _fc.render(_linha, True, (0, 0, 0))
                    self.screen.blit(_shadow, (_x + 16 + 2, _y + 2))
                    self.screen.blit(_fc.render(_linha, True, _BRANCO), (_x + 16, _y))
                    _y += _lh
                _y += 12
                if _y >= _max_y:
                    break

        # Mensagem CTA e link YouTube quando o segmento disponibiliza apoio externo.
        if _has_cta:
            _cta_font = self.font_status_success
            _cta_lines = [
                "Quer se aprofundar um pouco mais no tema?",
                "Clique no link abaixo e assista a uma aula completa!",
            ]
            _cta_lh = _cta_font.get_linesize() + 2
            _ltxt = "Assistir Aula Completa (YouTube)"
            _lsurf = self.font_lesson_content.render(_ltxt, True, _VERDE_CLARO)
            _cta_h = len(_cta_lines) * _cta_lh + _lsurf.get_height() + 44
            _cta_content_w = max([_cta_font.size(_linha)[0] for _linha in _cta_lines] + [_lsurf.get_width()])
            _cta_w = min(_cw + 36, _cta_content_w + 92)
            _cta_rect = pygame.Rect(WINDOW.width // 2 - _cta_w // 2, _panel_rect.bottom + 18, _cta_w, _cta_h)
            _cta = pygame.Surface(_cta_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(_cta, (0, 0, 0, 112), _cta.get_rect(), border_radius=8)
            pygame.draw.rect(_cta, (*_VERDE_CLARO, 150), _cta.get_rect(), width=2, border_radius=8)
            self.screen.blit(_cta, _cta_rect.topleft)

            _cy = _cta_rect.y + 14
            for _cl in _cta_lines:
                _txt_shadow = _cta_font.render(_cl, True, (0, 0, 0))
                _txt_surf = _cta_font.render(_cl, True, _VERDE_CLARO)
                self.screen.blit(_txt_shadow, _txt_shadow.get_rect(center=(WINDOW.width // 2 + 2, _cy + _cta_lh // 2 + 2)))
                self.screen.blit(_txt_surf, _txt_surf.get_rect(center=(WINDOW.width // 2, _cy + _cta_lh // 2)))
                _cy += _cta_lh

            self.link_rect = _lsurf.get_rect(center=(WINDOW.width // 2, _cy + _lsurf.get_height() // 2 + 4))
            self.screen.blit(_lsurf, self.link_rect)
            pygame.draw.line(
                self.screen, _VERDE_CLARO,
                (self.link_rect.left, self.link_rect.bottom),
                (self.link_rect.right, self.link_rect.bottom),
                2,
            )
        else:
            self.link_rect = None

        self.btn_continuar_y = None

    def _renderizar_segmento_exercicio(self, segmento):
        """Renderiza o exercício atual dentro de um bloco de prática.

        Usa o mesmo fundo e a mesma paleta visual da tela de aula, exibindo
        título, contador, pergunta, campo de resposta ou alternativas e banner
        de status.

        Recebe:
            segmento (dict): Segmento de tipo "exercicios" com chaves "titulo"
            e "exercicios" (list[str] de IDs).
        """
        self.link_rect = None  # Evita clique fantasma em botoes de link que sumiram
        exercicio = self._exercicio_atual()
        numero = self.exercicio_indice + 1
        total = len(segmento["exercicios"])

        self._desenhar_fundo_aprendizado()

        _TITULO = segmento["titulo"]
        _GAP = 2
        _ft = self.font_lesson_practice_title
        _char_w = [_ft.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = _ft.get_height()
        _tcy = 58

        self.lesson_glow_timer += 1
        _ga = int(40 + 80 * abs(math.sin(self.lesson_glow_timer * 0.04)))
        _gs = [_ft.render(c, True, _VERDE_CLARO) for c in _TITULO]
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
            self.screen.blit(_ft.render(_c, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft.render(_c, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        _sub = f"Exercício {numero} de {total}"
        _sub_y = _tcy + _char_h // 2 + 42
        _ss = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2 + 2, _sub_y + 2)))
        _ss = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2, _sub_y)))

        if exercicio is None:
            self._desenhar_paragrafo("Exercício não encontrado.", self.content_x, 250, self.content_width, self.font_body, _BRANCO)
            return

        _pergunta_font = self.font_status_success
        _linhas = quebrar_texto(exercicio["pergunta"], _pergunta_font, 820)
        _question_w = min(max(max(_pergunta_font.size(_linha)[0] for _linha in _linhas) + 96, 620), 900)
        _question_h = max(96, len(_linhas) * (_pergunta_font.get_linesize() + 2) + 42)
        _question_rect = pygame.Rect(WINDOW.width // 2 - _question_w // 2, 178, _question_w, _question_h)
        _question_panel = pygame.Surface(_question_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(_question_panel, (0, 0, 0, 118), _question_panel.get_rect(), border_radius=8)
        pygame.draw.rect(_question_panel, (*_VERDE_CLARO, 150), _question_panel.get_rect(), width=2, border_radius=8)
        self.screen.blit(_question_panel, _question_rect.topleft)

        _lh = _pergunta_font.get_linesize() + 2
        _y = _question_rect.y + max(18, (_question_rect.height - len(_linhas) * _lh) // 2)
        for _linha in _linhas:
            _shadow = _pergunta_font.render(_linha, True, (0, 0, 0))
            _shadow_rect = _shadow.get_rect(center=(_question_rect.centerx + 2, _y + _lh // 2 + 2))
            self.screen.blit(_shadow, _shadow_rect)
            _surface = _pergunta_font.render(_linha, True, _BRANCO)
            self.screen.blit(_surface, _surface.get_rect(center=(_question_rect.centerx, _y + _lh // 2)))
            _y += _lh

        if exercicio["tipo"] != "multipla_escolha":
            placeholder = exercicio.get("placeholder", "Digite sua resposta")
            self._desenhar_input_verde(pygame.Rect(self.content_x, 350, self.content_width, 58), self.resposta_texto, "resposta", placeholder)

        if self.status_kind in {"success", "error"} or exercicio["tipo"] != "multipla_escolha":
            _status_y = WINDOW.height // 2 if self.status_kind == "success" else WINDOW.height - 118
            self._desenhar_status(_status_y)

    def _renderizar_conclusao(self):
        """Renderiza a conclusão do mundo ativo usando a identidade visual da aula."""
        self._desenhar_fundo_aprendizado()

        _TITULO = "Aula concluída"
        _GAP = 2
        _ft = self.font_lesson_title
        _char_w = [_ft.size(c)[0] for c in _TITULO]
        _total_w = sum(_char_w) + _GAP * (len(_TITULO) - 1)
        _tx0 = WINDOW.width // 2 - _total_w // 2
        _char_h = _ft.get_height()
        _tcy = 72

        self.lesson_glow_timer += 1
        _ga = int(40 + 80 * abs(math.sin(self.lesson_glow_timer * 0.04)))
        _gs = [_ft.render(c, True, _VERDE_CLARO) for c in _TITULO]
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
            self.screen.blit(_ft.render(_c, True, (0, 0, 0)), (_x + 3, _tcy - _char_h // 2 + 3))
            _x += _char_w[_i] + _GAP
        _x = _tx0
        for _i, _c in enumerate(_TITULO):
            self.screen.blit(_ft.render(_c, True, _BRANCO), (_x, _tcy - _char_h // 2))
            _x += _char_w[_i] + _GAP

        proximo_label, _proximo_acao = self._proximo_mundo_conclusao()
        numero_atual = self.mundo_ativo.replace("mundo_", "")
        _sub = f"Mundo {numero_atual} concluído"
        _sub_y = _tcy + _char_h // 2 + 42
        _ss = self.font_hub_subtitle.render(_sub, True, (0, 0, 0))
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2 + 2, _sub_y + 2)))
        _ss = self.font_hub_subtitle.render(_sub, True, _BRANCO)
        self.screen.blit(_ss, _ss.get_rect(center=(WINDOW.width // 2, _sub_y)))

        _texto = self._texto_conclusao_mundo(proximo_label)
        _font = self.font_status_success
        _linhas = quebrar_texto(_texto, _font, 760)
        _lh = _font.get_linesize() + 4
        _panel_w = 860
        _panel_h = max(150, len(_linhas) * _lh + 58)
        _panel_rect = pygame.Rect(WINDOW.width // 2 - _panel_w // 2, 235, _panel_w, _panel_h)
        _panel = pygame.Surface(_panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(_panel, (0, 0, 0, 118), _panel.get_rect(), border_radius=8)
        pygame.draw.rect(_panel, (*_VERDE_CLARO, 150), _panel.get_rect(), width=2, border_radius=8)
        self.screen.blit(_panel, _panel_rect.topleft)

        _y = _panel_rect.y + (_panel_rect.height - len(_linhas) * _lh) // 2
        for _linha in _linhas:
            _shadow = _font.render(_linha, True, (0, 0, 0))
            self.screen.blit(_shadow, _shadow.get_rect(center=(_panel_rect.centerx + 2, _y + _lh // 2 + 2)))
            _surface = _font.render(_linha, True, _BRANCO)
            self.screen.blit(_surface, _surface.get_rect(center=(_panel_rect.centerx, _y + _lh // 2)))
            _y += _lh

        if self.status_message.startswith("EM BREVE!"):
            self._desenhar_status(525)

    def _desenhar_cabecalho(self, titulo, subtitulo):
        """Desenha o cabeçalho padrão de 170px com título e subtítulo centralizados.

        Recebe:
            titulo (str): Texto principal renderizado com font_title.
            subtitulo (str): Texto secundário renderizado com font_subtitle em cor accent.
        """
        pygame.draw.rect(self.screen, PALETTE.surface, pygame.Rect(0, 0, WINDOW.width, 170))
        pygame.draw.line(self.screen, PALETTE.border, (0, 170), (WINDOW.width, 170), 2)
        desenhar_texto_centralizado(self.screen, titulo, self.font_title, PALETTE.text, 68)
        desenhar_texto_centralizado(self.screen, subtitulo, self.font_subtitle, PALETTE.accent, 120)

    def _desenhar_label(self, texto, x, y):
        """Renderiza um rótulo de formulário com font_small na cor muted.

        Recebe:
            texto (str): Texto do rótulo.
            x (int): Coordenada horizontal do canto superior esquerdo.
            y (int): Coordenada vertical do canto superior esquerdo.
        """
        self.screen.blit(self.font_small.render(texto, True, PALETTE.muted), (x, y))

    def _desenhar_input(self, rect, valor, campo, placeholder):
        """Renderiza um campo de texto com estilo escuro padrão.

        Destaca a borda em accent quando o campo estiver ativo; mostra
        placeholder em cor muted quando valor for vazio.

        Recebe:
            rect (pygame.Rect): Posição e tamanho do campo.
            valor (str): Texto digitado atualmente.
            campo (str): Nome interno do campo para comparação com self.active_field.
            placeholder (str): Texto exibido quando valor for vazio.
        """
        ativo = self.active_field == campo
        cor_borda = PALETTE.accent if ativo else PALETTE.border
        pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=8)
        pygame.draw.rect(self.screen, cor_borda, rect, width=2, border_radius=8)
        texto = valor or placeholder
        cor = PALETTE.text if valor else PALETTE.muted
        self.screen.blit(self.font_body.render(texto, True, cor), (rect.x + 14, rect.y + 10))

    def _desenhar_input_verde(self, rect, valor, campo, placeholder):
        """Renderiza um campo de texto com estilo verde escuro para telas de fundo verde.

        Análogo a _desenhar_input mas com paleta _VERDE/_VERDE_CLARO em vez de PALETTE.

        Recebe:
            rect (pygame.Rect): Posição e tamanho do campo.
            valor (str): Texto digitado atualmente.
            campo (str): Nome interno do campo para comparação com self.active_field.
            placeholder (str): Texto exibido quando valor for vazio.
        """
        ativo = self.active_field == campo
        cor_borda = _VERDE_CLARO if ativo else _VERDE
        pygame.draw.rect(self.screen, (15, 35, 15), rect, border_radius=8)
        pygame.draw.rect(self.screen, cor_borda, rect, width=2, border_radius=8)
        texto = valor or placeholder
        cor = _BRANCO if valor else (100, 150, 100)
        self.screen.blit(self.font_body.render(texto, True, cor), (rect.x + 14, rect.y + 10))

    def _desenhar_paragrafo(self, texto, x, y, largura, font, color):
        """Renderiza um bloco de texto quebrado em múltiplas linhas.

        Recebe:
            texto (str): Conteúdo textual a renderizar.
            x (int): Margem esquerda em pixels.
            y (int): Coordenada vertical inicial.
            largura (int): Largura máxima disponível em pixels.
            font (pygame.font.Font): Fonte usada na renderização.
            color (tuple[int, int, int]): Cor RGB do texto.

        Retorna:
            int: Coordenada y imediatamente após o último pixel do bloco de texto.
        """
        linha_altura = font.get_linesize() + 4
        for linha in quebrar_texto(texto, font, largura):
            self.screen.blit(font.render(linha, True, color), (x, y))
            y += linha_altura
        return y

    def _desenhar_status(self, y):
        """Renderiza o banner de status quando status_kind for "success" ou "error".

        Para "normal", exibe apenas o texto em cor muted. Para "success", desenha
        um retangulo com borda verde. Para "error", usa apenas texto vermelho com
        sombra, evitando que o aviso pareca um botao clicavel.

        Recebe:
            y (int): Coordenada vertical central do banner.
        """
        if self.status_kind in {"success", "error"}:
            color = PALETTE.success if self.status_kind == "success" else PALETTE.error
            font = self.font_hub_subtitle if self.status_kind == "error" else self.font_body
            linhas = quebrar_texto(self.status_message, font, self.content_width - 80)
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

            altura = max(58, (len(linhas) * linha_altura) + 24)
            largura = min(
                max(max(font.size(linha)[0] for linha in linhas) + 96, 420),
                self.content_width,
            )
            rect = pygame.Rect(WINDOW.width // 2 - largura // 2, y - altura // 2, largura, altura)
            pygame.draw.rect(self.screen, PALETTE.surface, rect, border_radius=10)
            pygame.draw.rect(self.screen, color, rect, width=2, border_radius=10)
            texto_y = rect.y + 12
            for linha in linhas:
                surface = font.render(linha, True, color)
                surface_rect = surface.get_rect(center=(rect.centerx, texto_y + linha_altura // 2))
                self.screen.blit(surface, surface_rect)
                texto_y += linha_altura
            return

        desenhar_texto_centralizado(self.screen, self.status_message, self.font_tiny, PALETTE.muted, y)
