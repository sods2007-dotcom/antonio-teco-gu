"""
Penalty Shooter - Ponto de entrada do jogo.
"""
import pygame
from config import (
    WIDTH, HEIGHT, MENU, SELECAO, PARTIDA, FIM_PARTIDA, CAMPEAO, QUIT
)
from menu_screen import menu_screen
from selecao_screen import selecao_screen
from partida_screen import partida_screen
from fim_partida_screen import fim_partida_screen
def tela_placeholder(window, nome_tela):
    """Tela temporaria. Sera substituida no Commit #18."""
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
    return MENU
# ===== Inicializacao =====
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Penalty Shooter')
# ===== Contexto compartilhado entre telas =====
# Por enquanto so usado pelo FIM_PARTIDA, mas vai crescer no Commit #17
contexto = {
    'fase_torneio': 'quartas',
    'ultima_partida': None,
}
# ===== Loop principal de telas =====
state = MENU
while state != QUIT:
    if state == MENU:
        state = menu_screen(window)
        # Reset do torneio ao voltar ao menu
        contexto['fase_torneio'] = 'quartas'
    elif state == SELECAO:
        state = selecao_screen(window)
    elif state == PARTIDA:
        state, partida = partida_screen(window)
        contexto['ultima_partida'] = partida
    elif state == FIM_PARTIDA:
        state = fim_partida_screen(
            window,
            contexto['ultima_partida'],
            contexto['fase_torneio']
        )
    elif state == CAMPEAO:
        state = tela_placeholder(window, "CAMPEAO!")
    else:
        state = QUIT
pygame.quit()