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
            3  # so contorno
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

        self.speedx = 6  # velocidade de oscilacao horizontal

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
        self.estado = 'parada'

class Goleiro(pygame.sprite.Sprite):
    LARGURA = 80
    ALTURA = 100
    def __init__(self, cor_camisa=YELLOW):
        """Goleiro com a cor da camisa especificada."""
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(
            (self.LARGURA, self.ALTURA), pygame.SRCALPHA
        )
        # Corpo - usa a cor recebida (em vez de YELLOW fixo)
        pygame.draw.rect(self.image, cor_camisa,
                        (10, 30, self.LARGURA - 20, self.ALTURA - 30))
        pygame.draw.circle(self.image, (255, 220, 180),
                          (self.LARGURA // 2, 20), 18)
        pygame.draw.rect(self.image, cor_camisa,
                        (0, 35, self.LARGURA, 12))
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = 260
        self.posicao_inicial = self.rect.center
        self.estado = 'parado'
        self.alvo_x = 0
        self.alvo_y = 0
        self.frames_mergulho = 0
        self.mask = pygame.mask.from_surface(self.image)
    def mergulhar_para(self, x, y):
        """Inicia o mergulho do goleiro em direcao a (x, y)."""
        self.alvo_x = x
        self.alvo_y = y
        self.estado = 'mergulhando'
        self.frames_mergulho = 0
    def update(self):
        """Atualiza a animacao do mergulho."""
        if self.estado == 'mergulhando':
            FRAMES_TOTAL = 10
            dx = self.alvo_x - self.posicao_inicial[0]
            dy = self.alvo_y - self.posicao_inicial[1]
            progresso = self.frames_mergulho / FRAMES_TOTAL
            progresso = min(1.0, progresso)
            self.rect.centerx = self.posicao_inicial[0] + int(dx * progresso)
            self.rect.centery = self.posicao_inicial[1] + int(dy * progresso)
            # Rotaciona conforme mergulha
            angulo = 0
            if dx < 0:
                angulo = progresso * 45
            elif dx > 0:
                angulo = -progresso * 45
            center = self.rect.center
            self.image = pygame.transform.rotate(self.image_original, angulo)
            self.rect = self.image.get_rect()
            self.rect.center = center
            # Recalcula mask apos rotacao
            self.mask = pygame.mask.from_surface(self.image)
            self.frames_mergulho += 1
            if self.frames_mergulho >= FRAMES_TOTAL:
                self.estado = 'mergulhou'
    def resetar(self):
        """Volta o goleiro para a posicao inicial."""
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.posicao_inicial
        self.estado = 'parado'
        self.frames_mergulho = 0
        self.mask = pygame.mask.from_surface(self.image)
class Partida:
    """
    Gerencia o estado de uma partida de penaltis.
    Mantem o controle de:
    - Qual eh a cobranca atual (1 a 5 para cada time)
    - Resultado de cada cobranca (GOL/DEFENDIDA/FORA/TRAVE)
    - Qual time esta cobrando agora
    - Quando a partida acabou
    """
    TOTAL_COBRANCAS = 5
    def __init__(self, time_jogador, time_adversario):
        self.time_jogador = time_jogador
        self.time_adversario = time_adversario
        # Listas com resultado de cada cobranca
        self.resultados_jogador = []
        self.resultados_adversario = []
        # Estado: 'jogador_cobra', 'jogador_defende', 'fim'
        self.fase = 'jogador_cobra'
        self.cobranca_atual = 1
    def registra_resultado_jogador(self, resultado):
        """Registra o resultado de uma cobranca do jogador."""
        self.resultados_jogador.append(resultado)
        if not self.partida_decidida():
            self.fase = 'jogador_defende'
        else:
            self.fase = 'fim'
    def registra_resultado_adversario(self, resultado):
        """Registra o resultado de uma cobranca do adversario."""
        self.resultados_adversario.append(resultado)
        if not self.partida_decidida():
            self.fase = 'jogador_cobra'
            self.cobranca_atual += 1
        else:
            self.fase = 'fim'
    def gols_jogador(self):
        """Quantos gols o jogador fez ate agora."""
        return self.resultados_jogador.count('GOL')
    def gols_adversario(self):
        """Quantos gols o adversario fez ate agora."""
        return self.resultados_adversario.count('GOL')
    def partida_decidida(self):
        """
        Retorna True se a partida ja esta matematicamente decidida
        (nao adianta cobrar mais).
        """
        cobr_j = len(self.resultados_jogador)
        cobr_a = len(self.resultados_adversario)
        gols_j = self.gols_jogador()
        gols_a = self.gols_adversario()
        restantes_j = self.TOTAL_COBRANCAS - cobr_j
        restantes_a = self.TOTAL_COBRANCAS - cobr_a
        # Se um time nao tem mais como alcancar o outro
        if gols_j > gols_a + restantes_a:
            return True
        if gols_a > gols_j + restantes_j:
            return True
        # Se completaram todas as cobrancas
        if cobr_j == self.TOTAL_COBRANCAS and cobr_a == self.TOTAL_COBRANCAS:
            return True  # mesmo se empatou, considera fim (simplificacao)
        return False
    def jogador_venceu(self):
        """Retorna True se o jogador venceu a partida."""
        if not self.partida_decidida():
            return False
        return self.gols_jogador() > self.gols_adversario()
class Batedor(pygame.sprite.Sprite):
    def __init__(self, cor_camisa=(200, 50, 50)):
        """Batedor com a cor da camisa do time adversario."""
        pygame.sprite.Sprite.__init__(self)
        self.image_original = pygame.Surface((40, 70), pygame.SRCALPHA)
        # Usa a cor recebida (em vez de (200, 50, 50) fixo)
        pygame.draw.rect(self.image_original, cor_camisa, (5, 20, 30, 40))
        pygame.draw.circle(self.image_original,
                          (255, 220, 180), (20, 10), 10)
        pygame.draw.rect(self.image_original, (50, 50, 100), (8, 55, 8, 15))
        pygame.draw.rect(self.image_original, (50, 50, 100), (24, 55, 8, 15))
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2 - 100, HEIGHT - 30)
        self.posicao_chute = (WIDTH // 2, HEIGHT - 60)
        self.frames_correndo = 30
        self.estado = 'correndo'

    def update(self):
        """Animacao de correr ate a bola."""
        if self.estado == 'correndo':
            # Move suavemente em direcao a bola
            dx = self.posicao_chute[0] - self.rect.centerx
            dy = self.posicao_chute[1] - self.rect.centery

            if abs(dx) > 2:
                self.rect.x += int(dx * 0.1)
            if abs(dy) > 2:
                self.rect.y += int(dy * 0.1)

            # Gira ligeiramente (parece que esta correndo)
            if self.frames_correndo % 6 < 3:
                self.image = pygame.transform.rotate(self.image_original, 5)
            else:
                self.image = pygame.transform.rotate(self.image_original, -5)

            self.frames_correndo -= 1
            if self.frames_correndo <= 0:
                self.estado = 'parado'
                self.image = self.image_original.copy()

    def acabou_correr(self):
        """Retorna True se o batedor ja chegou e parou."""
        return self.estado == 'parado'


class AlvoDefesa(pygame.sprite.Sprite):
    """
    Alvo amarelo que aparece em algum ponto do gol durante a defesa.
    O jogador deve clicar nele rapido para o goleiro mergulhar.
    Tem tempo limitado de visibilidade (~1 segundo).
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Posicao aleatoria dentro do gol
        gol_largura = 500
        gol_altura = 180
        gol_x = (WIDTH - gol_largura) // 2
        gol_y = 80
        margem = 30

        self.alvo_x = random.randint(
            gol_x + margem,
            gol_x + gol_largura - margem
        )
        self.alvo_y = random.randint(
            gol_y + margem,
            gol_y + gol_altura - margem
        )

        # Cria imagem: circulo amarelo com X vermelho dentro
        self.tamanho = 35
        self.image = pygame.Surface(
            (self.tamanho, self.tamanho),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            self.image, YELLOW,
            (self.tamanho // 2, self.tamanho // 2),
            self.tamanho // 2
        )
        pygame.draw.circle(
            self.image, RED,
            (self.tamanho // 2, self.tamanho // 2),
            self.tamanho // 2, 3
        )

        # X no meio
        pygame.draw.line(self.image, RED, (5, 5), (self.tamanho - 5, self.tamanho - 5), 3)
        pygame.draw.line(self.image, RED, (self.tamanho - 5, 5), (5, self.tamanho - 5), 3)

        self.rect = self.image.get_rect()
        self.rect.center = (self.alvo_x, self.alvo_y)
        self.frames_visivel = 30  # ~1 segundo a 30 FPS

    def update(self):
        """Conta os frames de visibilidade."""
        if self.frames_visivel > 0:
            self.frames_visivel -= 1

    def expirou(self):
        """True se o tempo do alvo acabou."""
        return self.frames_visivel <= 0