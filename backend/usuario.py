"""Modelo de dominio que representa o jogador e sua progressao."""

from dataclasses import dataclass, field


@dataclass
class Usuario:
    """Representa o jogador ativo do CodeQuest com seus atributos de progressão."""

    nome: str
    idade: int
    id: int = 1
    xp: int = 0
    nivel: int = 1
    conquistas: list[str] = field(default_factory=list)

    @classmethod
    def criar(cls, nome, idade):
        """Cria um Usuario novo com os valores padrão de início de jogo.

        Recebe:
            nome (str): Nome informado no cadastro; espaços extras nas bordas
            são removidos com strip().
            idade (int | str): Idade informada; convertida para int.

        Retorna:
            Usuario: Instância com id=1, xp=0, nivel=1 e conquistas vazias.
        """
        return cls(nome=nome.strip(), idade=int(idade))

    @classmethod
    def from_dict(cls, dados):
        """Constrói um Usuario a partir de um dicionário, tolerando campos ausentes.

        Usada para migração de saves legados em JSON e para carregar dados de
        fontes externas sem garantia de todos os campos opcionais presentes.

        Recebe:
            dados (dict): Dicionário com pelo menos as chaves "nome" e "idade".
            Campos opcionais: "id" (padrão 1), "xp" (0), "nivel" (1),
            "conquistas" ([]).

        Retorna:
            Usuario: Instância preenchida com valores do dicionário, usando
            padrões para campos ausentes.
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
        """Soma XP ao usuário e recalcula o nível usando a função fornecida.

        Recebe:
            quantidade (int): Pontos de XP a adicionar ao total atual.
            calcular_nivel (Callable[[int], int]): Função que recebe o XP total
            e retorna o nível correspondente.

        Retorna:
            tuple[bool, int]: Par (subiu_nivel, novo_nivel) onde subiu_nivel é
            True quando o nível aumentou em relação ao anterior.
        """
        self.xp += quantidade
        novo_nivel = calcular_nivel(self.xp)
        subiu = novo_nivel > self.nivel
        self.nivel = novo_nivel
        return subiu, novo_nivel
