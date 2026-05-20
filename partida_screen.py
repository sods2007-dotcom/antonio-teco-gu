"""
Tela da partida — com deteccao de resultado do chute.
"""

import pygame
from config import (
    WIDTH, HEIGHT, FPS,
    WHITE, BLACK, GREEN_GRAMA, GRAY, GREEN, RED,
    MENU, QUIT
)
from assets import load_assets
from sprites import Mira, Bola


def partida_screen(window):
    """Roda uma cobranca completa com deteccao de resultado."""
    clock = pygame.time.Clock()
    assets = load_assets()
    mira = Mira()
    bola = Bola()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(bola, mira)

    resultado = ""
    running = True
    next_state = MENU

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:  # Tecla R reseta para nova cobranca
                    mira = Mira()
                    bola.resetar()
                    all_sprites.empty()
                    all_sprites.add(bola, mira)
                    resultado = ""

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mira.estado == 'oscilando_x':
                    mira.travar_horizontal()

            if event.type == pygame.MOUSEBUTTONUP:
                if mira.estado == 'subindo':
                    alvo = mira.disparar()
                    bola.chutar(alvo[0], alvo[1])
                    all_sprites.remove(mira)

        all_sprites.update()

        # Verifica resultado quando a bola chega no gol
        if bola.estado == 'parou_no_gol' and resultado == "":
            resultado = verifica_gol(bola)

        # Desenha tudo
        desenha_campo(window)
        desenha_gol(window)
        all_sprites.draw(window)

        # Mensagem com cor diferente segundo o resultado
        if resultado:
            cor = GREEN if resultado == 'GOL' else RED
            msg = f"{resultado}! Aperte R para nova cobranca"
            texto = assets['font_media'].render(msg, True, cor)
        elif mira.estado == 'oscilando_x':
            msg = "Clique para travar direcao"
            texto = assets['font_pequena'].render(msg, True, WHITE)
        elif mira.estado == 'subindo':
            msg = "Solte para chutar"
            texto = assets['font_pequena'].render(msg, True, WHITE)
        else:
            msg = "..."
            texto = assets['font_pequena'].render(msg, True, WHITE)

        window.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 50))
        pygame.display.update()

    return next_state


def verifica_gol(bola):
    """
    Verifica se a posicao final da bola caiu dentro do gol.
    Retorna 'GOL', 'FORA' ou 'TRAVE'.
    """
    gol_largura = 500
    gol_altura = 180
    gol_x = (WIDTH - gol_largura) // 2
    gol_y = 80

    bx = bola.rect.centerx
    by = bola.rect.centery
    margem_trave = 8

    # Trave esquerda
    if (abs(bx - gol_x) < margem_trave and
            gol_y <= by <= gol_y + gol_altura):
        return 'TRAVE'

    # Trave direita
    if (abs(bx - (gol_x + gol_largura)) < margem_trave and
            gol_y <= by <= gol_y + gol_altura):
        return 'TRAVE'

    # Travessao
    if (abs(by - gol_y) < margem_trave and
            gol_x <= bx <= gol_x + gol_largura):
        return 'TRAVE'

    # Dentro do gol
    if (gol_x < bx < gol_x + gol_largura and
            gol_y < by < gol_y + gol_altura):
        return 'GOL'

    return 'FORA'


def desenha_campo(window):
    """Desenha o fundo do campo."""
    window.fill(GREEN_GRAMA)
    pygame.draw.line(window, WHITE, (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)


def desenha_gol(window):
    """Desenha o gol."""
    gol_largura = 500
    gol_altura = 180
    gol_x = (WIDTH - gol_largura) // 2
    gol_y = 80

    pygame.draw.rect(window, GRAY, (gol_x, gol_y, gol_largura, gol_altura))

    for i in range(1, 10):
        x = gol_x + i * (gol_largura // 10)
        pygame.draw.line(window, (100, 100, 100), (x, gol_y), (x, gol_y + gol_altura), 1)

    for i in range(1, 5):
        y = gol_y + i * (gol_altura // 5)
        pygame.draw.line(window, (100, 100, 100), (gol_x, y), (gol_x + gol_largura, y), 1)

    pygame.draw.rect(window, WHITE, (gol_x - 5, gol_y, 5, gol_altura + 5))
    pygame.draw.rect(window, WHITE, (gol_x + gol_largura, gol_y, 5, gol_altura + 5))
    pygame.draw.rect(window, WHITE, (gol_x - 5, gol_y - 5, gol_largura + 10, 5))