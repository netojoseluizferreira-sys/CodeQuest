"""Fluxos de navegação, mundos, usuário e respostas do menu Pygame."""

from backend.worlds import MUNDO_2_ID, MUNDO_3_ID, MUNDO_INICIAL, aula_inicial, nome_mundo, proximo_mundo
from pygame_client.content import carregar_aula_pygame, carregar_exercicios_pygame, obter_exercicio
from pygame_client.learning_progress import registrar_resposta
from pygame_client.menu_config import CUTSCENE_TEXTS
from utils.database import (
    STATUS_BLOQUEADO,
    STATUS_DISPONIVEL,
    STATUS_EM_BREVE,
    carregar_usuario,
    criar_usuario,
    exercicio_foi_concluido,
    obter_status_mundo,
    resetar_banco_de_dados,
)


class NavigationMixin:
    """Organiza transições de tela, carregamento de mundos e respostas do jogador.

    O mixin conversa com o banco SQLite, com os carregadores de conteúdo e com
    as regras de XP. Seus métodos retornam `None` na maior parte dos casos e
    modificam `screen_name`, mensagens de status e índices do fluxo de aula.
    """

    def _definir_status(self, mensagem, kind="normal"):
        """Atualiza a mensagem de status e seu estilo visual exibido por _desenhar_status.

        Recebe:
            mensagem (str): Texto a exibir.
            kind (str): "normal" (texto muted), "success" (borda verde) ou "error" (borda vermelha).
        """
        self.status_message = mensagem
        self.status_kind = kind

    def _mensagem_conquistas_desbloqueadas(self, conquistas):
        """Monta o texto de aviso para conquistas recem-desbloqueadas."""
        if len(conquistas) == 1:
            return (
                "Conquista desbloqueada!\n"
                f"{conquistas[0]['nome']}\n"
                "Vá ao perfil para visualizar."
            )

        nomes = ", ".join(conquista["nome"] for conquista in conquistas)
        return f"Conquistas desbloqueadas!\n{nomes}\nVá ao perfil para visualizar."

    def _novo_jogo(self):
        """Reseta o banco de dados, limpa o estado do usuário e navega para a criação de personagem."""
        resetar_banco_de_dados()
        self.usuario = None
        self.nome_input = ""
        self.idade_input = ""
        self.active_field = "nome"
        self._definir_status("Crie seu personagem para começar uma nova jornada.")
        self.screen_name = "create"

    def _continuar(self):
        """Carrega o save existente ou direciona o jogador para criar perfil.

        Recebe:
            Nenhum parâmetro.

        Retorna:
            None: Atualiza self.usuario, status_message e screen_name como efeito colateral.
        """
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self.nome_input = ""
            self.idade_input = ""
            self.active_field = "nome"
            self._definir_status("Crie seu perfil para continuar.", "normal")
            self.screen_name = "create"
            return

        self._definir_status("Save carregado. Continue sua jornada.", "success")
        self._abrir_hub()

    def _criar_personagem(self):
        """Valida os campos do formulário de criação, persiste o usuário e vai para o hub.

        Exibe erros de status quando nome estiver vazio, idade não for numérica
        ou estiver fora do intervalo [1, 120].
        """
        nome = self.nome_input.strip()
        if not nome:
            self._definir_status("Informe um nome para o personagem.", "error")
            return
        try:
            idade = int(self.idade_input)
        except ValueError:
            self._definir_status("Informe uma idade numérica.", "error")
            return
        if idade < 1 or idade > 120:
            self._definir_status("A idade precisa estar entre 1 e 120.", "error")
            return

        self.usuario = criar_usuario(nome, idade)
        conquistas = getattr(self.usuario, "conquistas_desbloqueadas", [])
        if conquistas:
            self._definir_status(self._mensagem_conquistas_desbloqueadas(conquistas), "success")
        else:
            self._definir_status("Personagem criado. Escolha seu próximo destino.", "success")
        self._abrir_hub()

    def _abrir_hub(self):
        """Navega para o hub; redireciona para criação de personagem se não houver save."""
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self.screen_name = "create"
            return
        self.screen_name = "hub"
        self.active_field = "nome"

    def _abrir_mundos(self):
        """Navega para a seleção de mundos; bloqueia com erro se não houver personagem criado."""
        if carregar_usuario() is None:
            self._definir_status("Crie um personagem antes de viajar.", "error")
            self.screen_name = "create"
            return
        self.screen_name = "worlds"
        self._definir_status("Escolha um destino para estudar.")

    def _selecionar_mundo(self, mundo_id):
        """Consulta a regra de acesso do mundo e inicia, bloqueia ou mostra aviso."""
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self._definir_status("Crie um personagem antes de estudar.", "error")
            self.screen_name = "create"
            return

        status = obter_status_mundo(mundo_id, self.usuario)
        if status["estado"] == STATUS_DISPONIVEL:
            self._iniciar_mundo(mundo_id, aula_inicial(mundo_id))
            return
        if status["estado"] == STATUS_BLOQUEADO:
            self._definir_status(status["mensagem"], "error")
            return
        if status["estado"] == STATUS_EM_BREVE:
            self._mostrar_mundo_em_breve(mundo_id)

    def _mostrar_mundo_em_breve(self, mundo_id=None):
        """Mostra o aviso de mundo indisponível mantendo o jogador na seleção de mundos.

        Recebe:
            mundo_id (str | None): Mundo indisponível, quando houver.

        Retorna:
            None: Atualiza apenas a mensagem de status exibida na tela de mundos.
        """
        kind = "success" if getattr(self, "screen_name", None) == "complete" else "normal"
        self._definir_status(
            "EM BREVE!\nOs segredos deste mundo ainda não estão prontos para serem revelados. "
            "Continue sua jornada pelos mundos disponíveis enquanto isso.",
            kind,
        )

    def _mostrar_mundo_3_em_breve(self):
        """Mostra o aviso de indisponibilidade do Mundo 3 na tela de conclusão.

        Retorna:
            None: Atualiza a mensagem de status exibida na tela atual.
        """
        self._mostrar_mundo_em_breve(MUNDO_3_ID)

    def _proximo_mundo_conclusao(self):
        """Define o botão de próximo mundo exibido na tela de conclusão.

        Retorna:
            tuple[str, Callable]: Texto do botão e ação correspondente.
        """
        proximo = proximo_mundo(self.mundo_ativo)
        if proximo is None:
            return "Mundos", self._abrir_mundos
        return proximo["numero"], lambda mundo_id=proximo["id"]: self._selecionar_mundo(mundo_id)

    def _texto_conclusao_mundo(self, proximo_label):
        """Monta a mensagem de conclusão conforme o mundo recém-finalizado.

        Recebe:
            proximo_label (str): Nome do próximo mundo exibido no botão.

        Retorna:
            str: Texto orientando o jogador a ver o perfil ou seguir adiante.
        """
        return (
            f"Você completou o {nome_mundo(self.mundo_ativo)}. Agora pode visitar o perfil para ver seu progresso "
            f"ou seguir para o {proximo_label} e continuar sua jornada."
        )

    def _abrir_perfil(self):
        """Navega para a tela de perfil do jogador."""
        self.screen_name = "profile"

    def _abrir_creditos(self):
        """Toca o som de créditos, zera o scroll e navega para a tela de créditos."""
        self.audio.tocar_creditos()
        self.screen_name = "credits"
        self.credit_scroll = 0

    def _abrir_cutscene(self):
        """Captura o frame atual do hub para o fade de entrada e inicia a cutscene do início.

        Armazena o frame capturado em _cutscene_prev_frame para uso em _renderizar_cutscene
        durante o estado "fade_out_entry". Reseta índice, alpha e estado de fade.
        """
        self._cutscene_prev_frame = self.screen.copy()
        self.cutscene_index = 0
        self.cutscene_fade_alpha = 0
        self.cutscene_fade_state = "fade_out_entry"
        self.cutscene_fade_next = None
        self.screen_name = "cutscene"

    def _avancar_cutscene(self):
        """Avança diretamente para a próxima cena (sem fade) ou abre mundos na última.

        Ignorado enquanto o fade de entrada estiver em andamento (estado != "visible").
        """
        if self.cutscene_fade_state != "visible":
            return
        if self.cutscene_index >= len(CUTSCENE_TEXTS) - 1:
            self._abrir_mundos()
        else:
            self.cutscene_index += 1

    def _iniciar_mundo_1(self):
        """Carrega a aula e exercícios do Mundo 1 e inicia o fluxo de aprendizagem.

        Redireciona para criação de personagem se não houver save, ou exibe erro
        de status quando o arquivo de aula não puder ser carregado.
        """
        self._selecionar_mundo(MUNDO_INICIAL)

    def _iniciar_mundo_2(self):
        """Carrega a aula e exercícios do Mundo 2 e inicia o fluxo de aprendizagem."""
        self._selecionar_mundo(MUNDO_2_ID)

    def _iniciar_mundo(self, mundo, aula_id):
        """Carrega uma aula de mundo e inicia o fluxo visual de aprendizagem.

        Recebe:
            mundo (str): Chave do mundo em data/aulas.json e data/exercicios.json.
            aula_id (str): Chave da aula dentro do mundo.
        """
        self.usuario = carregar_usuario()
        if self.usuario is None:
            self._definir_status("Crie um personagem antes de estudar.", "error")
            self.screen_name = "create"
            return

        self.mundo_ativo = mundo
        self.aula_ativa = aula_id
        self.aula = carregar_aula_pygame(self.mundo_ativo, self.aula_ativa)
        self.exercicios = carregar_exercicios_pygame(self.mundo_ativo)
        if not self.aula:
            self._definir_status("Não foi possível carregar a aula.", "error")
            return
        self.trilha_indice = 0
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self._definir_status("Leia com calma e avance no seu ritmo.")
        self.screen_name = "lesson"
        self._pular_exercicios_concluidos()

    def _segmento_atual(self):
        """Retorna o segmento na posição trilha_indice da trilha da aula carregada.

        Retorna:
            dict | None: Dicionário do segmento atual, ou None quando não houver
            aula carregada ou trilha_indice ultrapassar o total de segmentos.
        """
        if not self.aula:
            return None
        trilha = self.aula.get("trilha", [])
        if self.trilha_indice >= len(trilha):
            return None
        return trilha[self.trilha_indice]

    def _pular_exercicios_concluidos(self):
        """Avança pelos exercícios já concluídos no banco sem pular textos de aula.

        Consulta o SQLite para o usuário ativo. Enquanto o segmento atual for
        de prática, incrementa exercicio_indice para ignorar exercícios já
        concluídos; ao terminar um bloco inteiro, avança para o próximo segmento
        da trilha, que pode ser um texto de aula ou outro bloco de prática.

        Retorna:
            None: Atualiza trilha_indice, exercicio_indice e screen_name como
            efeito colateral.
        """
        self.usuario = carregar_usuario()
        while self.usuario is not None:
            segmento = self._segmento_atual()
            if segmento is None:
                self.screen_name = "complete"
                return
            if segmento["tipo"] != "exercicios":
                return

            exercicios_ids = segmento["exercicios"]
            while self.exercicio_indice < len(exercicios_ids):
                exercicio_id = exercicios_ids[self.exercicio_indice]
                if not exercicio_foi_concluido(self.mundo_ativo, exercicio_id, self.usuario):
                    return
                self.exercicio_indice += 1

            self.trilha_indice += 1
            self.exercicio_indice = 0
            self.resposta_texto = ""
            self.exercicio_respondido = False

    def _exercicio_atual(self):
        """Retorna o exercício na posição exercicio_indice do segmento de prática atual.

        Retorna:
            dict | None: Dicionário do exercício, ou None quando o segmento não
            for do tipo "exercicios" ou o ID não for encontrado em self.exercicios.
        """
        segmento = self._segmento_atual()
        if not segmento or segmento["tipo"] != "exercicios":
            return None
        exercicio_id = segmento["exercicios"][self.exercicio_indice]
        return obter_exercicio(self.exercicios, exercicio_id)

    def _avancar_segmento(self):
        """Incrementa trilha_indice, reseta o estado de exercício e navega para "complete" ao final."""
        self.trilha_indice += 1
        self.exercicio_indice = 0
        self.resposta_texto = ""
        self.exercicio_respondido = False
        self._pular_exercicios_concluidos()
        self._definir_status("Continue sua jornada.")
        if self._segmento_atual() is None:
            self.screen_name = "complete"

    def _avancar_exercicio(self):
        """Vai para o próximo exercício do bloco ou avança para o próximo segmento ao esgotar a lista."""
        segmento = self._segmento_atual()
        if not segmento:
            self.screen_name = "complete"
            return
        self.exercicio_indice += 1
        if self.exercicio_indice >= len(segmento["exercicios"]):
            self._avancar_segmento()
        else:
            self.resposta_texto = ""
            self.exercicio_respondido = False
            self._pular_exercicios_concluidos()
            self._definir_status("Próximo desafio.")

    def _responder_texto_livre(self):
        """Valida que o campo de resposta não está vazio e encaminha para _responder_exercicio."""
        if not self.resposta_texto.strip():
            self._definir_status("Digite uma resposta antes de enviar.", "error")
            return
        self._responder_exercicio(self.resposta_texto)

    def _responder_exercicio(self, resposta):
        """Valida a resposta via registrar_resposta, atualiza XP e define o feedback de status.

        Recebe:
            resposta (int | str): Índice da alternativa escolhida (múltipla escolha)
            ou texto digitado (texto livre).
        """
        exercicio = self._exercicio_atual()
        self.usuario = carregar_usuario()
        if exercicio is None or self.usuario is None:
            self._definir_status("Não foi possível responder agora.", "error")
            return

        resultado = registrar_resposta(self.mundo_ativo, exercicio, resposta, self.usuario)
        conquistas = resultado.get("conquistas_desbloqueadas", [])
        if conquistas:
            self._definir_status(self._mensagem_conquistas_desbloqueadas(conquistas), "success")
        else:
            self._definir_status(resultado["mensagem"], "success" if resultado["acertou"] else "error")
        if resultado["acertou"]:
            self.usuario = carregar_usuario()
            self.exercicio_respondido = True
            self.active_field = "nome"

    def _voltar_contextual(self):
        """Navega para a tela anterior mais lógica com base em screen_name atual.

        "hub"/"create" → tela inicial; "worlds"/"profile"/"complete"/"cutscene" → hub;
        "lesson" → mundos; "credits" → início; outros → sair.
        """
        if self.screen_name in {"hub", "create"}:
            self._voltar_inicio()
        elif self.screen_name in {"worlds", "profile", "complete", "cutscene"}:
            self._abrir_hub()
        elif self.screen_name == "lesson":
            self._abrir_mundos()
        elif self.screen_name == "credits":
            self._voltar_inicio()
        else:
            self._sair()

    def _voltar_inicio(self):
        """Navega para a tela inicial e reseta a mensagem de status."""
        self.screen_name = "start"
        self._definir_status("Bem-vindo ao CodeQuest.")

    def _sair(self):
        """Define self.running como False, encerrando o loop principal no próximo ciclo."""
        self.running = False
