# Penalty Shooter

Jogo de pênaltis inspirado no Penalty Shooters 2 da Poki, desenvolvido em Python com a biblioteca PyGame.

Projeto Final da disciplina de Design de Software — Insper, 2026.

## Integrantes do grupo

- Gustavo Pimenta
- Antonio Refinetti
- Stefano di Sora

## Descrição do projeto

Penalty Shooter é um jogo de cobranças de pênaltis em formato de torneio. O jogador escolhe um time entre 8 disponíveis e enfrenta adversários controlados pelo computador em 3 partidas eliminatórias (quartas de final, semifinal e final), alternando entre o papel de cobrador e goleiro a cada cobrança.

A cada partida, cada time tem 5 chances de marcar gol. Vence quem fizer mais gols. Em caso de empate após as 5 cobranças, a partida vai para a **prorrogação (morte súbita)**: cada lado cobra uma vez por rodada até que um marque e o outro não.

A dificuldade do goleiro adversário aumenta a cada fase do torneio: ele defende menos nas quartas e bem mais na final.

### Mecânica de jogo

**Quando você é o batedor:**
- Uma mira vermelha se move horizontalmente em frente ao gol
- Clique uma vez para travar a **direção** horizontal
- A mira passa a subir e descer sozinha — clique de novo para travar a **altura** e chutar

**Quando você é o goleiro:**
- O batedor adversário corre em direção à bola
- Um alvo aparece indicando onde a bola vai
- Clique no ponto onde você acha que a bola vai cair para o goleiro mergulhar e defender

### Controles

- **Mouse:** toda a interação principal (mirar, chutar, defender, navegar nos menus)
- **P:** pausar / continuar durante a partida
- **ESC:** voltar ao menu
- **ENTER:** confirmar nas telas de fim de partida

## Como instalar e rodar

### Requisitos

- Python 3.x instalado
- Biblioteca PyGame (recomendado: pygame-ce)

### Instalação

Abra o terminal na pasta do projeto e execute:

```
pip install pygame-ce
```

Caso o comando acima dê erro, tente:

```
pip install pygame
```

### Execução

Na pasta raiz do projeto, execute:

```
python jogo.py
```

## Estrutura do projeto

```
penalty-shooter/
    jogo.py
    config.py
    assets.py
    sprites.py
    menu_screen.py
    selecao_screen.py
    partida_screen.py
    fim_partida_screen.py
    campeao_screen.py
    assets/
        img/
        snd/
        font/
    README.md
```

## Funcionalidades

- Torneio de 3 fases (quartas, semifinal, final) com seleção entre 8 times
- Alternância entre cobrar e defender a cada cobrança
- Goleiro com dificuldade progressiva conforme avança o torneio
- Prorrogação em morte súbita quando há empate
- Efeitos sonoros (chute, gol, defesa, trave) e música ambiente de torcida
- Animações de bola, goleiro mergulhando, batedor correndo e confetes na vitória
- Placar visual ao vivo e função de pausa

## Vídeo de apresentação

[Assista no YouTube](https://youtu.be/XfsA00b_igU?si=m03qhryGekXsog2U)

## Tecnologias utilizadas

- Python 3
- PyGame (PyGame Community Edition)
- Git / GitHub

## Créditos dos sons

Todos os sons foram obtidos em [freesound.org](https://freesound.org/):

- **chute.wav** — autor anonimo
- **gol.mp3** — autor anonimo
- **perdeu.mp3** — autor anonimo
- **trave.wav** — autor anonimo
- **torcida.wav** — autor anonimo

## Sobre o desenvolvimento

Este projeto foi desenvolvido como Projeto Final da disciplina de Design de Software do primeiro semestre de Engenharia/Ciências Econômicas do Insper, semestre 2026/1.

Foi utilizada assistência de IA generativa (Claude, da Anthropic) como ferramenta de tutoria durante o desenvolvimento. Os integrantes do grupo são responsáveis pelo entendimento e explicação de todo o código presente no projeto.