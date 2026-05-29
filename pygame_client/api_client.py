import requests


class CodeQuestApiClient:
    """Cliente HTTP usado pelo menu Pygame para conversar com a API."""

    def __init__(self, base_url="http://127.0.0.1:8000", timeout=2.0):
        """Inicializa o cliente da API.

        Recebe:
            base_url: URL base da API FastAPI.
            timeout: Tempo maximo de espera por chamada HTTP.

        Retorna:
            None.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self):
        """Verifica se a API esta acessivel.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario retornado pela rota de health.
        """
        return self._post_or_get("GET", "/health")

    def novo_jogo(self):
        """Solicita novo jogo para a API.

        Recebe:
            Nenhum parametro.

        Retorna:
            Dicionario com estado do menu atualizado.
        """
        return self._post_or_get("POST", "/menu/novo-jogo")

    def continuar(self, nome="Aventureiro", idade=18):
        """Solicita continuar jogo para a API.

        Recebe:
            nome: Nome usado quando a API precisar criar um save.
            idade: Idade usada quando a API precisar criar um save.

        Retorna:
            Dicionario com dados do usuario carregado ou criado.
        """
        return self._post_or_get(
            "POST",
            "/menu/continuar",
            json={"nome": nome, "idade": idade},
        )

    def _post_or_get(self, method, path, **kwargs):
        """Executa uma requisicao HTTP curta.

        Recebe:
            method: Metodo HTTP usado na chamada.
            path: Caminho da rota da API.
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
