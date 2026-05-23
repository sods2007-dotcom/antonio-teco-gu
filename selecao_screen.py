"""
Tela de selecao de time. Mostra um grid 4x2 com os 8 times disponiveis.
"""
import pygame
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, TIMES,
    PARTIDA, MENU, QUIT
)
from assets import load_assets
def selecao_screen(window):
    """
    Mostra a selecao de times. Retorna (next_state, time_escolhido).
    """
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    assets = load_assets()
    # Layout: 4 colunas, 2 linhas
    colunas = 4
    linhas = 2
    card_largura = 160
    card_altura = 130
    espaco_x = 20
    espaco_y = 20
    total_largura = colunas * card_largura + (colunas - 1) * espaco_x
    inicio_x = (WIDTH - total_largura) // 2
    inicio_y = 180
    # Cria lista de retangulos dos cards
    cards = []
    for i, time in enumerate(TIMES):
        col = i % colunas
        lin = i // colunas
        x = inicio_x + col * (card_largura + espaco_x)
        y = inicio_y + lin * (card_altura + espaco_y)
        rect = pygame.Rect(x, y, card_largura, card_altura)
        cards.append((rect, time))
    titulo = assets['font_grande'].render("ESCOLHA SEU TIME", True, WHITE)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 90))
    dica = assets['font_pequena'].render(
        "Clique em um time para comecar o torneio", True, (200, 200, 200)
    )
    dica_rect = dica.get_rect(center=(WIDTH // 2, 540))
    running = True
    next_state = MENU
    time_escolhido = None
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    next_state = MENU
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, time in cards:
                    if rect.collidepoint(event.pos):
                        time_escolhido = time
                        next_state = PARTIDA
                        running = False
                        break
        window.fill(GREEN_GRAMA)
        window.blit(titulo, titulo_rect)
        for rect, (nome, cor1, cor2) in cards:
            desenha_card_time(window, assets, rect, nome, cor1, cor2,
                            hover=rect.collidepoint(mouse_pos))
        window.blit(dica, dica_rect)
        pygame.display.update()
    return next_state, time_escolhido
def desenha_card_time(window, assets, rect, nome, cor1, cor2, hover=False):
    """Desenha o card de um time."""
    # Fundo com cor primaria
    pygame.draw.rect(window, cor1, rect)
    # Faixa central com cor secundaria
    faixa_altura = 30
    faixa_y = rect.centery - faixa_altura // 2
    pygame.draw.rect(window, cor2, (rect.x, faixa_y, rect.width, faixa_altura))
    # Borda
    cor_borda = (255, 255, 0) if hover else WHITE
    pygame.draw.rect(window, cor_borda, rect, 3)
    # Cor do texto baseada na luminancia da cor secundaria
    lum = (cor2[0] * 0.299 + cor2[1] * 0.587 + cor2[2] * 0.114)
    cor_texto = BLACK if lum > 150 else WHITE
    texto = assets['font_pequena'].render(nome, True, cor_texto)
    texto_rect = texto.get_rect(center=(rect.centerx, rect.centery))
    window.blit(texto, texto_rect)