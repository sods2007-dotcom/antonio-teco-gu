"""
Tela da partida — onde as cobrancas e defesas acontecem.
Esta tela vai crescendo ao longo do projeto. Por enquanto, soh
desenha o campo, o gol e espera o jogador apertar uma tecla.
"""
import pygame
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, GRAY, MENU, QUIT
)
def partida_screen(window):
    """
    Roda uma partida. Por enquanto, soh mostra o campo e o gol.
    Retorna o proximo estado (MENU ou QUIT).
    """
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    running = True
    next_state = MENU
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                running = False
        # Desenha o cenario
        desenha_campo(window)
        desenha_gol(window)
        # Texto temporario
        texto = font.render(
            "Aperte qualquer tecla para voltar", True, WHITE
        )
        window.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
        pygame.display.update()
    return next_state
def desenha_campo(window):
    """Desenha o fundo do campo (grama verde com linhas brancas)."""
    window.fill(GREEN_GRAMA)
    # Linha de fundo (decorativa)
    pygame.draw.line(window, WHITE, (0, HEIGHT - 100), (WIDTH, HEIGHT - 100), 2)
def desenha_gol(window):
    """Desenha o gol — duas traves brancas com rede cinza atras."""
    gol_largura = 500
    gol_altura = 180
    gol_x = (WIDTH - gol_largura) // 2
    gol_y = 80
    # Rede (retangulo cinza atras)
    pygame.draw.rect(window, GRAY, (gol_x, gol_y, gol_largura, gol_altura))
    # Linhas verticais da rede
    for i in range(1, 10):
        x = gol_x + i * (gol_largura // 10)
        pygame.draw.line(window, (100, 100, 100),
                         (x, gol_y), (x, gol_y + gol_altura), 1)
    # Linhas horizontais da rede
    for i in range(1, 5):
        y = gol_y + i * (gol_altura // 5)
        pygame.draw.line(window, (100, 100, 100),
                         (gol_x, y), (gol_x + gol_largura, y), 1)
    # Traves (linhas brancas grossas)
    pygame.draw.rect(window, WHITE,
                    (gol_x - 5, gol_y, 5, gol_altura + 5))
    pygame.draw.rect(window, WHITE,
                    (gol_x + gol_largura, gol_y, 5, gol_altura + 5))
    pygame.draw.rect(window, WHITE,
                    (gol_x - 5, gol_y - 5, gol_largura + 10, 5))