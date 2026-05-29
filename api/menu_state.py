from dataclasses import dataclass
from threading import Lock


@dataclass
class MenuState:
    """Estado em memoria da ultima acao disparada pelo menu Pygame."""

    next_page: str | None = None
    message: str = "Aguardando acao do menu Pygame."


class MenuStateStore:
    """Armazena de forma simples o estado do menu entre chamadas HTTP."""

    def __init__(self):
        """Inicializa o armazenamento em memoria.

        Recebe:
            Nenhum parametro.

        Retorna:
            None.
        """
        self._state = MenuState()
        self._lock = Lock()

    def definir(self, next_page, message):
        """Define a proxima pagina desejada pelo menu.

        Recebe:
            next_page: Pagina do Streamlit que deve ser aberta.
            message: Mensagem explicativa da acao.

        Retorna:
            Estado atualizado.
        """
        with self._lock:
            self._state = MenuState(next_page=next_page, message=message)
            return self._state

    def obter(self):
        """Retorna o estado atual do menu.

        Recebe:
            Nenhum parametro.

        Retorna:
            Estado atual do menu.
        """
        with self._lock:
            return MenuState(next_page=self._state.next_page, message=self._state.message)

    def limpar(self):
        """Limpa a proxima pagina pendente.

        Recebe:
            Nenhum parametro.

        Retorna:
            Estado limpo.
        """
        with self._lock:
            self._state = MenuState()
            return self._state


menu_state_store = MenuStateStore()
