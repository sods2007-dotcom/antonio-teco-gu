"""
Tela da partida — onde as cobrancas e defesas acontecem.
"""
import pygame
from config import (
 WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, GRAY, MENU, QUIT
)
from assets import load_assets
from sprites import Mira, Bola
def partida_screen(window):
 """Roda uma partida. Por enquanto, soh uma cobranca."""
 clock = pygame.time.Clock()
 assets = load_assets()
 mira = Mira()
 bola = Bola()
 all_sprites = pygame.sprite.Group()
 all_sprites.add(bola)
 all_sprites.add(mira)
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
 if event.key == pygame.K_r:
 # Tecla R reseta para nova cobranca
 mira = Mira()
 bola.resetar()
 all_sprites.empty()
 all_sprites.add(bola)
 all_sprites.add(mira)
 if event.type == pygame.MOUSEBUTTONDOWN:
 if mira.estado == 'oscilando_x':
 mira.travar_horizontal()
 if event.type == pygame.MOUSEBUTTONUP:
 if mira.estado == 'subindo':
 alvo = mira.disparar()
 bola.chutar(alvo[0], alvo[1])
 all_sprites.remove(mira)
 all_sprites.update()
 # Desenha tudo
 desenha_campo(window)
 desenha_gol(window)
 all_sprites.draw(window)
 # Mensagem de instrucao
 if mira.estado == 'oscilando_x':
 msg = "Clique para travar direcao"
 elif mira.estado == 'subindo':
 msg = "Solte para chutar"
 elif bola.estado == 'voando':
 msg = "..."
 else:
 msg = "Aperte R para nova cobranca, ESC para voltar"
 texto = assets['font_pequena'].render(msg, True, WHITE)
 window.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
 pygame.display.update()
 return next_state
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
