import requests


class StreamlitApiClient:
    """Cliente HTTP usado pelo Streamlit para consultar a API local."""

    def __init__(self, base_url="http://127.0.0.1:8000", timeout=1.5):
        """Inicializa o cliente HTTP do Streamlit.

        Recebe:
            base_url: URL base da API FastAPI.
            timeout: Tempo maximo de espera por chamada HTTP.

        Retorna:
            None.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self):
        """Verifica se a API esta disponivel.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario retornado pela API.
        """
        return self._request("GET", "/health")

    def obter_estado_menu(self):
        """Consulta a ultima acao solicitada pelo menu Pygame.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario com proxima pagina e mensagem.
        """
        return self._request("GET", "/menu/estado")

    def limpar_estado_menu(self):
        """Limpa a acao pendente do menu Pygame.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario com o estado limpo.
        """
        return self._request("POST", "/menu/limpar")

    def _request(self, method, path, **kwargs):
        """Executa uma chamada HTTP para a API local.

        Recebe:
            method: Metodo HTTP da chamada.
            path: Caminho da rota.
            kwargs: Argumentos extras repassados ao requests.

        Retorna:
            Corpo JSON retornado pela API.
        """
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()
