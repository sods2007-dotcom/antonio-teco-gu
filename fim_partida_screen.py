"""
Tela de fim de partida — mostra o resultado e proximos passos.
"""
import pygame
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, GREEN, RED, YELLOW,
    MENU, PARTIDA, CAMPEAO, QUIT
)
from assets import load_assets
def fim_partida_screen(window, partida, fase_torneio):
    """
    Mostra o resultado de uma partida.
    Se o jogador venceu e ainda nao eh a final, oferece continuar.
    Se venceu a final, vai pra tela CAMPEAO.
    Se perdeu, oferece voltar ao menu.
    """
    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    assets = load_assets()
    venceu = partida.jogador_venceu()
    e_final = fase_torneio == 'final'
    # Determina texto principal e proxima acao
    if venceu and e_final:
        texto_principal = "VOCE EH O CAMPEAO!"
        cor_principal = YELLOW
        proximo_state = CAMPEAO
        texto_botao = "VER CONQUISTA"
    elif venceu:
        if fase_torneio == 'quartas':
            texto_principal = "PASSOU PARA A SEMIFINAL!"
            texto_botao = "JOGAR SEMIFINAL"
        else:
            texto_principal = "PASSOU PARA A FINAL!"
            texto_botao = "JOGAR FINAL"
        cor_principal = GREEN
        proximo_state = PARTIDA
    else:
        texto_principal = "VOCE FOI ELIMINADO"
        cor_principal = RED
        proximo_state = MENU
        texto_botao = "VOLTAR AO MENU"
    # Pre-renderiza textos
    titulo = assets['font_grande'].render(texto_principal, True, cor_principal)
    # Reduz se nao couber
    while titulo.get_width() > WIDTH - 40:
        nova_fonte = pygame.font.SysFont(None,
            int(titulo.get_height() * 0.9))
        titulo = nova_fonte.render(texto_principal, True, cor_principal)
    titulo_rect = titulo.get_rect(center=(WIDTH // 2, 150))
    placar = assets['font_grande'].render(
        f"{partida.gols_jogador()} x {partida.gols_adversario()}",
        True, WHITE
    )
    placar_rect = placar.get_rect(center=(WIDTH // 2, 280))
    times = assets['font_pequena'].render(
        f"{partida.time_jogador}    vs    {partida.time_adversario}",
        True, WHITE
    )
    times_rect = times.get_rect(center=(WIDTH // 2, 340))
    btn_proximo = assets['font_media'].render(texto_botao, True, WHITE)
    btn_proximo_rect = btn_proximo.get_rect(center=(WIDTH // 2, 450))
    btn_proximo_box = btn_proximo_rect.inflate(60, 20)
    btn_menu = assets['font_pequena'].render("Menu Principal", True, WHITE)
    btn_menu_rect = btn_menu.get_rect(center=(WIDTH // 2, 530))
    running = True
    next_state = MENU
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_proximo_box.collidepoint(event.pos):
                    next_state = proximo_state
                    running = False
                elif btn_menu_rect.collidepoint(event.pos):
                    next_state = MENU
                    running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    next_state = proximo_state
                    running = False
                elif event.key == pygame.K_ESCAPE:
                    next_state = MENU
                    running = False
        window.fill(GREEN_GRAMA)
        window.blit(titulo, titulo_rect)
        window.blit(placar, placar_rect)
        window.blit(times, times_rect)
        pygame.draw.rect(window, WHITE, btn_proximo_box, 3)
        window.blit(btn_proximo, btn_proximo_rect)
        window.blit(btn_menu, btn_menu_rect)
        pygame.display.update()
    return next_state