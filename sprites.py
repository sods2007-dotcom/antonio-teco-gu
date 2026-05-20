"""
Classes (sprites) usadas no jogo Penalty Shooter.
Todas as classes estendem pygame.sprite.Sprite para se beneficiar do
sistema de grupos e desenho automatico do pygame.
"""
import pygame
import random
from config import WIDTH, HEIGHT, RED, YELLOW, WHITE
class Mira(pygame.sprite.Sprite):
 """
 Mira de cobranca: alvo vermelho que oscila horizontalmente em frente ao gol.
 O jogador clica para travar a direcao horizontal. Enquanto segura o mouse,
 a mira sobe (controlando a altura do chute). Quando solta, dispara.
 """
 def __init__(self):
 pygame.sprite.Sprite.__init__(self)
 # Cria uma superficie pequena com mira em formato de cruz
 self.tamanho = 30
 self.image = pygame.Surface(
 (self.tamanho, self.tamanho), pygame.SRCALPHA
 )
 pygame.draw.circle(
 self.image, RED,
 (self.tamanho // 2, self.tamanho // 2),
 self.tamanho // 2,
 3 # so contorno
 )
 # Linhas em cruz no meio (parece com mira)
 pygame.draw.line(self.image, RED,
 (0, self.tamanho // 2),
 (self.tamanho, self.tamanho // 2), 2)
 pygame.draw.line(self.image, RED,
 (self.tamanho // 2, 0),
 (self.tamanho // 2, self.tamanho), 2)
 self.rect = self.image.get_rect()
 self.rect.centerx = WIDTH // 2
 self.rect.centery = HEIGHT - 200
 self.speedx = 6 # velocidade de oscilacao horizontal
 # Limites de oscilacao
 self.x_min = (WIDTH - 500) // 2 - 40
 self.x_max = self.x_min + 500 + 80
 # Estado: 'oscilando_x', 'subindo', 'disparada'
 self.estado = 'oscilando_x'
 def update(self):
 """Atualiza a posicao da mira conforme seu estado."""
 if self.estado == 'oscilando_x':
 # Oscila horizontalmente, batendo nas bordas
 self.rect.x += self.speedx
 if self.rect.right > self.x_max or self.rect.left < self.x_min:
 self.speedx = -self.speedx
 elif self.estado == 'subindo':
 # Sobe (controla altura do chute)
 self.rect.y -= 4
 if self.rect.top < 50:
 self.rect.top = 50
 def travar_horizontal(self):
 """Para a oscilacao horizontal e comeca a subir."""
 self.estado = 'subindo'
 def disparar(self):
 """Finaliza o ajuste e dispara. Retorna a posicao alvo."""
 self.estado = 'disparada'
 return (self.rect.centerx, self.rect.centery)
class Bola(pygame.sprite.Sprite):
 """
 Bola de futebol. Inicialmente parada no centro inferior da tela,
 depois eh chutada em direcao a uma posicao alvo.
 Diminui de tamanho conforme se aproxima do gol (simula profundidade).
 """
 POSICAO_INICIAL_X = WIDTH // 2
 POSICAO_INICIAL_Y = HEIGHT - 80
 def __init__(self):
 pygame.sprite.Sprite.__init__(self)
 # Cria imagem: circulo branco com borda preta
 self.raio = 15
 diametro = self.raio * 2
 self.image = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
 pygame.draw.circle(self.image, WHITE,
 (self.raio, self.raio), self.raio)
 pygame.draw.circle(self.image, (0, 0, 0),
 (self.raio, self.raio), self.raio, 2)
 self.image_original = self.image.copy()
 self.rect = self.image.get_rect()
 self.rect.center = (self.POSICAO_INICIAL_X, self.POSICAO_INICIAL_Y)
 self.speedx = 0
 self.speedy = 0
 self.escala = 1.0
 # Estado: 'parada', 'voando', 'parou_no_gol'
 self.estado = 'parada'
 def chutar(self, alvo_x, alvo_y):
 """
 Calcula a velocidade necessaria para a bola chegar ao alvo.
 A bola eh chutada com numero fixo de frames ate chegar,
 para que o movimento seja previsivel.
 """
 FRAMES_ATE_GOL = 25
 dx = alvo_x - self.rect.centerx
 dy = alvo_y - self.rect.centery
 self.speedx = dx / FRAMES_ATE_GOL
 self.speedy = dy / FRAMES_ATE_GOL
 self.estado = 'voando'
 def update(self):
 """Atualiza a posicao e tamanho aparente da bola."""
 if self.estado != 'voando':
 return
 self.rect.x += self.speedx
 self.rect.y += self.speedy
 # Diminui escala conforme se aproxima do gol (profundidade)
 progresso = 1 - (self.rect.centery - 200) / (self.POSICAO_INICIAL_Y - 200)
 progresso = max(0, min(1, progresso))
 self.escala = 1 - progresso * 0.6
 # Redimensiona a imagem
 novo_tamanho = max(4, int(self.raio * 2 * self.escala))
 self.image = pygame.transform.scale(
 self.image_original, (novo_tamanho, novo_tamanho)
 )
 center = self.rect.center
 self.rect = self.image.get_rect()
 self.rect.center = center
 # Verifica se chegou no gol
 if self.rect.centery <= 260:
 self.estado = 'parou_no_gol'
 def resetar(self):
 """Volta a bola para a posicao inicial."""
 self.speedx = 0
 self.speedy = 0
 self.escala = 1.0
 self.image = self.image_original.copy()
 self.rect = self.image.get_rect()
 self.rect.center = (self.POSICAO_INICIAL_X, self.POSICAO_INICIAL_Y)
 self.estado = '