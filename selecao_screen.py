"""
Tela de selecao de time. Por enquanto eh placeholder.
Sera expandida com 8 times jogaveis no Commit #16.
"""
import pygame
from config import WIDTH, HEIGHT, FPS, WHITE, GREEN_GRAMA, PARTIDA, MENU, QUIT
def selecao_screen(window):
    """Placeholder por enquanto. Retorna (next_state, time_escolhido)."""
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 50)
    titulo = font.render("Selecao de Time", True, WHITE)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 100))
    dica = pygame.font.SysFont(None, 28).render(
        "Aperte ENTER para continuar (placeholder)", True, WHITE
    )
    dica_rect = dica.get_rect(center=(WIDTH // 2, HEIGHT // 2))
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
                    next_state = MENU
                    running = False
                else:
                    next_state = PARTIDA
                    running = False
        window.fill(GREEN_GRAMA)
        window.blit(titulo, titulo_rect)
        window.blit(dica, dica_rect)
        pygame.display.update()
    return next_state