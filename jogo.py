"""
Penalty Shooter - Ponto de entrada do jogo.
Gerencia a transicao entre as diferentes telas atraves de uma
maquina de estados simples.
"""
import pygame
from config import WIDTH, HEIGHT, MENU, QUIT
def tela_placeholder(window, nome_tela):
    """
    Tela temporaria que mostra o nome e espera o usuario apertar uma tecla.
    Sera substituida pelas telas reais nos proximos commits.
    """
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 80)
    text = font.render(nome_tela, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return QUIT
            if event.type == pygame.KEYDOWN:
                running = False
        window.fill((0, 0, 0))
        window.blit(text, text_rect)
        pygame.display.update()
    return QUIT
# ===== Inicializacao =====
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Penalty Shooter')
# ===== Loop principal de telas =====
state = MENU
while state != QUIT:
    if state == MENU:
        state = tela_placeholder(window, "MENU")
    else:
        state = QUIT
# ===== Finalizacao =====
pygame.quit()

