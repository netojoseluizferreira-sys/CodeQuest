from dataclasses import dataclass, field


@dataclass
class Usuario:
    """Modelo de dominio do jogador."""

    nome: str
    idade: int
    id: int = 1
    xp: int = 0
    nivel: int = 1
    conquistas: list[str] = field(default_factory=list)

    @classmethod
    def criar(cls, nome, idade):
        """Cria um novo usuario com os valores padrao do jogo."""
        return cls(nome=nome.strip(), idade=int(idade))

    @classmethod
    def from_dict(cls, dados):
        """Converte registros legados em dicionario para Usuario."""
        return cls(
            id=dados.get("id", 1),
            nome=dados["nome"],
            idade=dados["idade"],
            xp=dados.get("xp", 0),
            nivel=dados.get("nivel", 1),
            conquistas=dados.get("conquistas", []),
        )

    def to_dict(self):
        """Converte o usuario para formato simples."""
        return {
            "id": self.id,
            "nome": self.nome,
            "idade": self.idade,
            "xp": self.xp,
            "nivel": self.nivel,
            "conquistas": list(self.conquistas),
        }

    def adicionar_xp(self, quantidade, calcular_nivel):
        """Adiciona XP e retorna se o usuario subiu de nivel."""
        self.xp += quantidade
        novo_nivel = calcular_nivel(self.xp)
        subiu = novo_nivel > self.nivel
        self.nivel = novo_nivel
        return subiu, novo_nivel
