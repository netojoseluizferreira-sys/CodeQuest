"""Constantes de cores locais e cutscene do menu Pygame."""

from backend.worlds import MUNDO_INICIAL, aula_inicial

MUNDO_ATIVO = MUNDO_INICIAL
AULA_ATIVA = aula_inicial(MUNDO_INICIAL)

_VERDE = (30, 100, 50)
_BRANCO = (255, 255, 255)
_VERDE_CLARO = (100, 200, 120)
_KW_VERDE = dict(
    background=_VERDE,
    hover_background=_BRANCO,
    text_color=_BRANCO,
    hover_text_color=_VERDE,
    border_color=_VERDE_CLARO,
)

CUTSCENE_TEXTS = [
    "Em um dia comum, Faísca estava em seu quarto, mexendo no seu computador...",
    "Quando menos esperava, alguém bateu à sua porta. Curioso, ele foi até lá atender.",
    "Quando abriu, era Frederick, o entregador do bairro. Tinha uma encomenda em seu nome. Faísca ficou confuso, pois não estava esperando por nada. Mesmo assim, ele recebeu a caixa.",
    "Quando abriu, ficou surpreso com o que tinha dentro...",
    "Um pen-drive, aparentemente já usado. Colocou o pen-drive de volta na caixa e voltou para o seu quarto, sem dar muita importância.",
    "De volta ao quarto, deixou o pen-drive de lado e voltou ao que estava fazendo. Ainda tinha muito jogo pela frente.",
    "O cansaço começou a tomar conta e, pouco a pouco, Faísca sentia seus olhos ficarem mais pesados. Era hora de descansar.",
    "Ele desligou o monitor e se levantou da cadeira, pronto para ir dormir. Ao se levantar, tropeçou em algo no chão. Era o pen-drive. Olhou para ele por alguns segundos, intrigado e...",
    "CATAPLÓFT!!! Assim que conectou o pen-drive, a tela acendeu sozinha. Letras vermelhas piscavam na tela: ERRO! Você está sendo transferido para o Arquipélago de Bythos...",
    "Antes que Faísca pudesse reagir, uma luz verde brilhante começou a engoli-lo. Ele sentiu seu corpo sendo puxado, sugado para dentro da tela do computador. Tudo ficou escuro. Ele estava sendo transferido para outra dimensão.",
]

WORLD_MAP_BASE_SIZE = (1248, 702)

WORLD_MAP_HOTSPOTS = {
    "mundo_1": {
        "titulo": "Cabana do oraculo",
        "descricao": "Aqui Faisca e voce aprendem os conceitos de programacao e os primeiros passos para pensar como programador.",
        "rect": (14, 60, 14, 24),
    },
    "mundo_2": {
        "titulo": "Tenda do Iniciado",
        "descricao": "O ponto de partida pratico para escrever os primeiros comandos em Python.",
        "rect": (8, 30, 14, 22),
    },
    "mundo_3": {
        "titulo": "Forja Runica",
        "descricao": "Onde operadores aritmeticos, relacionais e logicos sao moldados em codigo.",
        "rect": (22, 12, 14, 22),
    },
    "mundo_4": {
        "titulo": "Torre dos Julgamentos",
        "descricao": "O lugar das decisoes: if, else, elif e caminhos condicionais.",
        "rect": (41, 4, 10, 22),
    },
    "mundo_5": {
        "titulo": "Moinho dos Ventos Arcanos",
        "descricao": "As repeticoes giram aqui: while, for e loops aninhados.",
        "rect": (40, 32, 14, 26),
    },
    "mundo_6": {
        "titulo": "Circulo das Runas",
        "descricao": "Funcoes, parametros, retornos e escopo convergem no centro da ilha.",
        "rect": (51, 55, 16, 22),
    },
    "mundo_7": {
        "titulo": "Biblioteca Eterea",
        "descricao": "Listas, indices e percursos ficam guardados entre pergaminhos flutuantes.",
        "rect": (56, 4, 14, 24),
    },
    "mundo_8": {
        "titulo": "Estufa de Cristal",
        "descricao": "Matrizes e estruturas bidimensionais crescem em grades luminosas.",
        "rect": (73, 10, 14, 18),
    },
    "mundo_9": {
        "titulo": "Castelo de Esmeralda",
        "descricao": "O ultimo portal: recursividade, caso base e o fim da jornada.",
        "rect": (76, 45, 18, 36),
    },
}
