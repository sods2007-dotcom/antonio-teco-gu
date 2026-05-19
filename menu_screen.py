"""
Tela do menu principal do jogo Penalty Shooter.
"""
import pygame
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, RED, YELLOW,
    SELECAO, QUIT
)
def menu_screen(window):
    """
    Mostra o menu principal e aguarda escolha do usuario.
    Retorna o proximo estado do jogo (SELECAO ou QUIT).
    """
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    font_titulo = pygame.font.SysFont(None, 90)
    font_botao = pygame.font.SysFont(None, 50)
    font_dica = pygame.font.SysFont(None, 28)
    # Pre-renderiza os textos uma vez (otimizacao)
    titulo = font_titulo.render("PENALTY SHOOTER", True, WHITE)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 130))
    subtitulo = font_dica.render(
        "Projeto Design de Software - Insper 2026",
        True, WHITE
    )
    subtitulo_rect = subtitulo.get_rect(center=(WIDTH // 2, 180))
    btn_jogar = font_botao.render("JOGAR", True, WHITE)
    btn_jogar_rect = btn_jogar.get_rect(center=(WIDTH // 2, 350))
    btn_jogar_box = btn_jogar_rect.inflate(60, 25)
    btn_sair = font_botao.render("SAIR", True, WHITE)
    btn_sair_rect = btn_sair.get_rect(center=(WIDTH // 2, 430))
    btn_sair_box = btn_sair_rect.inflate(60, 25)
    dica = font_dica.render(
        "Clique para escolher", True, (200, 200, 200)
    )
    dica_rect = dica.get_rect(center=(WIDTH // 2, 530))
    running = True
    next_state = QUIT
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        # ----- Trata eventos ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_jogar_box.collidepoint(mouse_pos):
                    next_state = SELECAO
                    running = False
                elif btn_sair_box.collidepoint(mouse_pos):
                    next_state = QUIT
                    running = False
        # ----- Gera saidas ----
        desenha_fundo_campo(window)
        window.blit(titulo, titulo_rect)
        window.blit(subtitulo, subtitulo_rect)
        # Botao Jogar - destaca se mouse esta em cima (hover)
        cor_borda = YELLOW if btn_jogar_box.collidepoint(mouse_pos) else WHITE
        pygame.draw.rect(window, cor_borda, btn_jogar_box, 3)
        window.blit(btn_jogar, btn_jogar_rect)
        # Botao Sair
        cor_borda = YELLOW if btn_sair_box.collidepoint(mouse_pos) else WHITE
        pygame.draw.rect(window, cor_borda, btn_sair_box, 3)
        window.blit(btn_sair, btn_sair_rect)
        window.blit(dica, dica_rect)
        pygame.display.update()
    return next_state
def desenha_fundo_campo(window):
    """Desenha um campo de futebol estilizado como fundo do menu."""
    window.fill(GREEN_GRAMA)
    # Faixas alternadas de cor (efeito gramado cortado)
    for i in range(0, HEIGHT, 50):
        if (i // 50) % 2 == 0:
            cor = (35, 115, 35)
        else:
            cor = (45, 140, 45)
        pygame.draw.rect(window, cor, (0, i, WIDTH, 50))
    # Linha do meio campo
    pygame.draw.line(window, WHITE,
                    (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 4)
    # Circulo central
    pygame.draw.circle(window, WHITE,
                       (WIDTH // 2, HEIGHT // 2), 70, 4)
    # Ponto central
    pygame.draw.circle(window, WHITE,
                       (WIDTH // 2, HEIGHT // 2), 6)