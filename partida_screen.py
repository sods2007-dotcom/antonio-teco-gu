"""
Tela da partida — com goleiro CPU e placar.
"""

import pygame
import random
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, GRAY, GREEN, RED, YELLOW,
    MENU, FIM_PARTIDA, QUIT
)
from assets import load_assets
from sprites import Mira, Bola, Goleiro, Partida
def partida_screen(window, time_jogador="Brasil", time_adversario="Argentina"):
    """Roda uma partida de penaltis (apenas fase do jogador cobrar, por ora)."""
    clock = pygame.time.Clock()
    assets = load_assets()
    partida = Partida(time_jogador, time_adversario)
    mira = Mira()
    bola = Bola()
    goleiro = Goleiro()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(goleiro, bola, mira)
    resultado_atual = ""
    frames_mostra_resultado = 0
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if mira.estado == 'oscilando_x':
                    mira.travar_horizontal()
            if event.type == pygame.MOUSEBUTTONUP:
                if mira.estado == 'subindo':
                    alvo_pos = mira.disparar()
                    bola.chutar(alvo_pos[0], alvo_pos[1])
                    if assets.get('chute'):
                        assets['chute'].play()
                    all_sprites.remove(mira)
                    # CPU decide se vai defender
                    if cpu_vai_defender(alvo_pos):
                        goleiro.mergulhar_para(alvo_pos[0], alvo_pos[1])
                    else:
                        # Mergulha pra um lado aleatorio (vai perder)
                        lado_x = random.choice(
                            [WIDTH // 2 - 200, WIDTH // 2 + 200]
                        )
                        goleiro.mergulhar_para(lado_x, 200)
        all_sprites.update()
        # Verifica resultado quando a bola chega no gol
        if bola.estado == 'parou_no_gol' and resultado_atual == "":
            # Usa colisao por mask para precisao
            if pygame.sprite.collide_mask(bola, goleiro):
                resultado_atual = "DEFENDIDA"
            else:
                resultado_atual = verifica_gol(bola)
            partida.registra_resultado_jogador(resultado_atual)
            tocar_som_resultado(assets, resultado_atual)
            frames_mostra_resultado = FPS * 2  # mostra por 2 segundos
        # Avanca para proxima cobranca apos 2 segundos
        if frames_mostra_resultado > 0:
            frames_mostra_resultado -= 1
            if frames_mostra_resultado == 0:
                if partida.fase == 'fim':
                    running = False
                    next_state = FIM_PARTIDA
                else:
                    # Reseta para proxima cobranca
                    mira = Mira()
                    bola.resetar()
                    goleiro.resetar()
                    all_sprites.empty()
                    all_sprites.add(goleiro, bola, mira)
                    resultado_atual = ""
        # Desenha tudo
        desenha_campo(window)
        desenha_gol(window)
        all_sprites.draw(window)
        desenha_placar(window, assets, partida)
        # Mensagem da fase
        if resultado_atual:
            cor = GREEN if resultado_atual == 'GOL' else RED
            texto = assets['font_media'].render(resultado_atual, True, cor)
            window.blit(texto,
                       (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 60))
        elif mira.estado == 'oscilando_x':
            msg = "Clique para travar direcao"
            texto = assets['font_pequena'].render(msg, True, WHITE)
            window.blit(texto,
                       (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
        elif mira.estado == 'subindo':
            msg = "Solte para chutar"
            texto = assets['font_pequena'].render(msg, True, WHITE)
            window.blit(texto,
                       (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
        pygame.display.update()
    return next_state
def cpu_vai_defender(alvo_pos):
    """
    Decide se o goleiro CPU vai defender o chute.
    Chance base de 40%, reduzida quando o alvo eh mais perto dos cantos.
    Tem um minimo de 15% para nao ser impossivel.
    """
    x = alvo_pos[0]
    distancia_centro = abs(x - WIDTH // 2)
    chance_base = 0.4
    chance = chance_base - (distancia_centro / 500)
    return random.random() < max(0.15, chance)
def verifica_gol(bola):
    """Verifica se a bola entrou no gol, bateu na trave ou saiu fora."""
    gol_largura = 500
    gol_altura = 180
    gol_x = (WIDTH - gol_largura) // 2
    gol_y = 80
    bx = bola.rect.centerx
    by = bola.rect.centery
    margem_trave = 8
    if (abs(bx - gol_x) < margem_trave
            and gol_y <= by <= gol_y + gol_altura):
        return 'TRAVE'
    if (abs(bx - (gol_x + gol_largura)) < margem_trave
            and gol_y <= by <= gol_y + gol_altura):
        return 'TRAVE'
    if (abs(by - gol_y) < margem_trave
            and gol_x <= bx <= gol_x + gol_largura):
        return 'TRAVE'
    if (gol_x < bx < gol_x + gol_largura
            and gol_y < by < gol_y + gol_altura):
        return 'GOL'
    return 'FORA'
def desenha_campo(window):
    """Desenha o fundo do campo."""
    window.fill(GREEN_GRAMA)
    pygame.draw.line(window, WHITE, (0, HEIGHT - 100),
                    (WIDTH, HEIGHT - 100), 2)
def desenha_gol(window):
    """Desenha o gol."""
    gol_largura = 500
    gol_altura = 180
    gol_x = (WIDTH - gol_largura) // 2
    gol_y = 80
    pygame.draw.rect(window, GRAY, (gol_x, gol_y, gol_largura, gol_altura))
    for i in range(1, 10):
        x = gol_x + i * (gol_largura // 10)
        pygame.draw.line(window, (100, 100, 100),
                         (x, gol_y), (x, gol_y + gol_altura), 1)
    for i in range(1, 5):
        y = gol_y + i * (gol_altura // 5)
        pygame.draw.line(window, (100, 100, 100),
                         (gol_x, y), (gol_x + gol_largura, y), 1)
    pygame.draw.rect(window, WHITE, (gol_x - 5, gol_y, 5, gol_altura + 5))
    pygame.draw.rect(window, WHITE,
                    (gol_x + gol_largura, gol_y, 5, gol_altura + 5))
    pygame.draw.rect(window, WHITE,
                    (gol_x - 5, gol_y - 5, gol_largura + 10, 5))
def desenha_placar(window, assets, partida):
    """Desenha o placar com nome dos times e bolinhas de cada cobranca."""
    # Nome dos times
    texto_j = assets['font_pequena'].render(partida.time_jogador, True, WHITE)
    texto_a = assets['font_pequena'].render(partida.time_adversario, True, WHITE)
    window.blit(texto_j, (20, 10))
    window.blit(texto_a, (WIDTH - texto_a.get_width() - 20, 10))
    # Bolinhas: verde=gol, vermelho=errou/defendido, cinza=ainda nao cobrou
    raio = 8
    espacamento = 22
    for i in range(5):
        # Bolinhas do jogador (esquerda)
        x = 20 + i * espacamento
        y = 45
        if i < len(partida.resultados_jogador):
            cor = GREEN if partida.resultados_jogador[i] == 'GOL' else RED
        else:
            cor = (60, 60, 60)
        pygame.draw.circle(window, cor, (x, y), raio)
        pygame.draw.circle(window, WHITE, (x, y), raio, 2)
        # Bolinhas do adversario (direita)
        x = WIDTH - 20 - i * espacamento - raio
        if i < len(partida.resultados_adversario):
            cor = GREEN if partida.resultados_adversario[i] == 'GOL' else RED
        else:
            cor = (60, 60, 60)
        pygame.draw.circle(window, cor, (x, y), raio)
        pygame.draw.circle(window, WHITE, (x, y), raio, 2)
def tocar_som_resultado(assets, resultado):
    """Toca o som apropriado para cada resultado."""
    if resultado == 'GOL' and assets.get('gol'):
        assets['gol'].play()
    elif resultado == 'TRAVE' and assets.get('trave'):
        assets['trave'].play()
    elif resultado in ('DEFENDIDA', 'FORA') and assets.get('perdeu'):
        assets['perdeu'].play()