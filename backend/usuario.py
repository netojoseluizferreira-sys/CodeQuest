from dataclasses import dataclass, field


@dataclass
class Usuario:
    """Representa o jogador ativo do CodeQuest."""

    nome: str
    idade: int
    id: int = 1
    xp: int = 0
    nivel: int = 1
    conquistas: list[str] = field(default_factory=list)

    @classmethod
    def criar(cls, nome, idade):
        """Cria um usuario novo com os valores iniciais do jogo.

        Recebe:
            nome: Nome informado no cadastro do perfil.
            idade: Idade informada no cadastro do perfil.

        Retorna:
            Uma instancia de Usuario pronta para ser persistida.
        """
        return cls(nome=nome.strip(), idade=int(idade))

    @classmethod
    def from_dict(cls, dados):
        """Converte dados legados em dicionario para Usuario.

        Recebe:
            dados: Dicionario com campos de usuario vindo de JSON ou compatibilidade.

        Retorna:
            Uma instancia de Usuario com valores padrao quando campos opcionais faltarem.
        """
        return cls(
            id=dados.get("id", 1),
            nome=dados["nome"],
            idade=dados["idade"],
            xp=dados.get("xp", 0),
            nivel=dados.get("nivel", 1),
            conquistas=dados.get("conquistas", []),
        )

    def adicionar_xp(self, quantidade, calcular_nivel):
        """Aplica XP ao usuario e recalcula seu nivel.

        Recebe:
            quantidade: Total de XP que deve ser somado ao usuario.
            calcular_nivel: Funcao que recebe o XP total e retorna o nivel correspondente.

        Retorna:
            Uma tupla com um booleano indicando subida de nivel e o novo nivel.
        """
        self.xp += quantidade
        novo_nivel = calcular_nivel(self.xp)
        subiu = novo_nivel > self.nivel
        self.nivel = novo_nivel
        return subiu, novo_nivel
