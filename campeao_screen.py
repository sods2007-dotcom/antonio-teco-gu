"""
Tela de vitoria do torneio.
Mostrada quando o jogador vence as 3 partidas.
Tem animacao de confetes caindo e desenho do trofeu.
"""

import pygame
import random

from config import (
    WIDTH,
    HEIGHT,
    FPS,
    WHITE,
    BLACK,
    GREEN_GRAMA,
    YELLOW,
    RED,
    GREEN,
    MENU,
    QUIT
)

from assets import load_assets


def campeao_screen(window, time_jogador):
    """
    Mostra a tela de campeao com animacao.
    time_jogador é a tupla (nome, cor1, cor2).
    """

    pygame.mouse.set_visible(True)

    clock = pygame.time.Clock()
    assets = load_assets()

    if assets.get('gol'):
        assets['gol'].play()

    nome_time, cor1, cor2 = time_jogador

    titulo = assets['font_grande'].render(
        "CAMPEAO!",
        True,
        YELLOW
    )
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 100))

    subtitulo = assets['font_media'].render(
        f"Parabens, {nome_time}!",
        True,
        WHITE
    )
    subtitulo_rect = subtitulo.get_rect(center=(WIDTH // 2, 180))

    descricao = assets['font_pequena'].render(
        "Voce venceu as quartas, semifinal e final!",
        True,
        WHITE
    )
    descricao_rect = descricao.get_rect(center=(WIDTH // 2, 480))

    botao = assets['font_media'].render(
        "Menu Principal",
        True,
        WHITE
    )
    botao_rect = botao.get_rect(center=(WIDTH // 2, 540))
    botao_box = botao_rect.inflate(40, 20)

    # Lista de confetes (particulas caindo)
    confetes = [criar_confete() for _ in range(80)]

    cores_confete = [
        cor1,
        cor2,
        YELLOW,
        GREEN,
        RED,
        (255, 100, 200)
    ]

    running = True
    next_state = MENU

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if botao_box.collidepoint(event.pos):
                    next_state = MENU
                    running = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    next_state = MENU
                    running = False

        # Atualiza confetes
        for c in confetes:
            c['y'] += c['vy']
            c['x'] += c['vx']
            c['angulo'] += c['va']

            if c['y'] > HEIGHT + 20:
                # Reseta o confete pra cair de novo do topo
                novo = criar_confete()
                c.update(novo)
                c['cor'] = random.choice(cores_confete)

        # Desenha tudo
        window.fill((20, 60, 20))

        for c in confetes:
            desenha_confete(window, c)

        desenha_trofeu(window, 300)

        window.blit(titulo, titulo_rect)
        window.blit(subtitulo, subtitulo_rect)
        window.blit(descricao, descricao_rect)

        pygame.draw.rect(window, WHITE, botao_box, 3)
        window.blit(botao, botao_rect)

        pygame.display.update()

    return next_state


def criar_confete():
    """Cria um confete em posicao aleatoria no topo da tela."""

    return {
        'x': random.randint(0, WIDTH),
        'y': random.randint(-200, 0),
        'vx': random.uniform(-1, 1),
        'vy': random.uniform(2, 5),
        'va': random.uniform(-5, 5),
        'angulo': random.uniform(0, 360),
        'cor': (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        ),
        'tamanho': random.randint(4, 8),
    }


def desenha_confete(window, c):
    """Desenha um confete (retangulo pequeno girado)."""

    s = pygame.Surface(
        (c['tamanho'] * 2, c['tamanho']),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        s,
        c['cor'],
        (0, 0, c['tamanho'] * 2, c['tamanho'])
    )

    s = pygame.transform.rotate(s, c['angulo'])

    window.blit(s, (c['x'], c['y']))


def desenha_trofeu(window, y_centro):
    """Desenha um trofeu simples no centro horizontal."""

    cx = WIDTH // 2

    # Base
    base_largura = 80
    base_altura = 20

    pygame.draw.rect(
        window,
        (100, 70, 30),
        (
            cx - base_largura // 2,
            y_centro + 60,
            base_largura,
            base_altura
        )
    )

    # Haste
    pygame.draw.rect(
        window,
        YELLOW,
        (cx - 8, y_centro + 30, 16, 30)
    )

    # Taca
    pygame.draw.ellipse(
        window,
        YELLOW,
        (cx - 50, y_centro - 50, 100, 100)
    )

    pygame.draw.ellipse(
        window,
        (255, 255, 200),
        (cx - 35, y_centro - 40, 25, 50)
    )

    # Alcas
    pygame.draw.arc(
        window,
        YELLOW,
        (cx - 70, y_centro - 30, 30, 50),
        0.5,
        2.5,
        6
    )

    pygame.draw.arc(
        window,
        YELLOW,
        (cx + 40, y_centro - 30, 30, 50),
        -1.5,
        0.5,
        6
    )