# CodeQuest

**CodeQuest** é uma plataforma educacional gamificada para ensinar lógica de programação e Python por meio de aulas curtas, exercícios, XP e progressão por mundos.

**Status atual:** projeto concluído na versão **Beta 0.9**.

## Sobre o Projeto

O CodeQuest organiza o aprendizado em mundos temáticos. A versão Beta 0.9 entrega o ciclo principal completo: menu inicial em Pygame, navegação web em Streamlit, API REST local em FastAPI, persistência em SQLite, criação/continuação de save, aula teórica e exercícios intercalados.

Cada exercício começa valendo 10 XP. A cada erro, a recompensa disponível cai em 2 XP, até o mínimo de 2 XP. Exercícios já concluídos ficam salvos no SQLite para evitar ganho duplicado de XP após reiniciar o app.

## Estrutura Atual

```text
CodeQuest/
├── app_streamlit.py                         # Ponto de entrada do Streamlit
├── api/                                     # API REST local com FastAPI
│   ├── main.py                              # Fábrica e instância da aplicação
│   ├── menu_state.py                        # Estado da última ação do menu Pygame
│   ├── schemas.py                           # Schemas Pydantic
│   └── routes/                              # Rotas de health, menu, usuários e progresso
├── backend/                                 # Regras de domínio e carregamento de conteúdo
├── frontend/                                # Estado e renderização do Streamlit
├── pygame_client/                           # Menu Pygame, créditos, áudio e botões
├── utils/                                   # Persistência SQLite e repositórios
├── data/                                    # Aulas e exercícios versionados
├── requirements.txt
└── README.md
```

## Funcionalidades da Beta 0.9

- Menu inicial em Pygame chamado a partir do fluxo web.
- Botão **Novo jogo** no Pygame resetando o banco e abrindo criação de perfil no Streamlit.
- Botão **Continuar** no Pygame carregando o save existente ou criando um save inicial.
- Botão **Créditos** funcional no Pygame.
- Botões de voltar no Streamlit retornando para a tela de espera do menu Pygame.
- API REST local em FastAPI para menu, usuário e progresso.
- Interface web em Streamlit para perfil, mundos, aulas e exercícios.
- Persistência local em SQLite.
- Aula 1 com textos e 15 exercícios intercalados.
- Sistema de XP com penalidade por erro: 10, 8, 6, 4 e mínimo de 2 XP.
- Controle de exercícios concluídos para impedir XP duplicado.
- Código modularizado por responsabilidade.

## Como Rodar

1. Crie e ative um ambiente virtual.

```bash
python -m venv venv
```

2. Instale as dependências.

```bash
pip install -r requirements.txt
```

3. Rode o Streamlit.

```bash
streamlit run app_streamlit.py
```

4. Acesse no navegador:

```text
http://localhost:8501
```

Ao iniciar o Streamlit, o projeto sobe a API local e abre o menu Pygame. O fluxo esperado é escolher **Novo jogo** ou **Continuar** na janela Pygame e seguir a jornada pelo navegador.

## API REST

A API local expõe rotas para saúde do serviço, menu, usuário e progresso:

```bash
uvicorn api.main:app --reload
```

Documentação automática:

```text
http://localhost:8000/docs
```

## Menu Pygame

O menu Pygame também pode ser executado isoladamente para desenvolvimento:

```bash
python -m pygame_client.menu_app
```

## Testes e Validação

Validações usadas durante o desenvolvimento:

```bash
python -m compileall api app_streamlit.py backend frontend utils pygame_client
python -m pytest tests
```

## Dados

Conteúdos versionados:

- `data/aulas.json`
- `data/exercicios.json`

## Revisão Técnica da Beta 0.9

- Persistência migrada para SQLite.
- CRUD de usuário organizado com `dataclass`.
- API REST local criada com FastAPI.
- Menu Pygame integrado à API.
- Streamlit consumindo a API para aplicar ações do menu.
- Fluxo Novo jogo/Continuar funcionando entre Pygame, API e Streamlit.
- Tela de créditos disponível no Pygame.
- Frontend e persistência separados em módulos menores.
- Testes locais cobrindo API, banco, XP, usuário, conteúdo e lógica de frontend.

## Roadmap

- Integrar cadastro de usuário diretamente via API em todas as telas do Streamlit.
- Criar autenticação real com login/senha.
- Adicionar novos mundos e módulos: operadores, condicionais, repetições, funções e listas.
- Expandir cutscenes em Pygame antes e depois de cada módulo.
- Criar mapa interativo do Arquipélago de Bythos.
- Adicionar conquistas persistidas por módulo.
- Implementar ranking online.
- Evoluir trilha sonora e efeitos sonoros.
- Criar empacotamento local para execução simplificada.
- Preparar hospedagem online para a API e o app web.
