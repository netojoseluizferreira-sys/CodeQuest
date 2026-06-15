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
    "CATAPLÉFITE!!! Assim que conectou o pen-drive, a tela acendeu sozinha. Letras vermelhas piscavam na tela: ERRO! Você está sendo transferido para o Arquipélago de Bythos...",
    "Antes que Faísca pudesse reagir, uma luz verde brilhante começou a engoli-lo. Ele sentiu seu corpo sendo puxado, sugado para dentro da tela do computador. Tudo ficou escuro. Ele estava sendo transferido para outra dimensão.",
]
