"""
Penalty Shooter - Ponto de entrada do jogo.
Gerencia a transicao entre as diferentes telas atraves de uma
maquina de estados simples.
"""
import pygame
from config import WIDTH, HEIGHT, MENU, SELECAO, PARTIDA, FIM_PARTIDA, CAMPEAO, QUIT
from menu_screen import menu_screen
def tela_placeholder(window, nome_tela):
    """Tela temporaria. Sera substituida pelas telas reais."""
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
    return MENU  # Por enquanto, volta pro menu apos qualquer tecla
# ===== Inicializacao =====
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Penalty Shooter')
# ===== Loop principal de telas =====
state = MENU
while state != QUIT:
    if state == MENU:
        state = menu_screen(window)
    elif state == SELECAO:
        state = tela_placeholder(window, "SELECAO DE TIME")
    elif state == PARTIDA:
        state = tela_placeholder(window, "PARTIDA")
    elif state == FIM_PARTIDA:
        state = tela_placeholder(window, "FIM DE PARTIDA")
    elif state == CAMPEAO:
        state = tela_placeholder(window, "CAMPEAO!")
    else:
        state = QUIT
# ===== Finalizacao =====
pygame.quit()