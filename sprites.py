"""
Classes (sprites) usadas no jogo Penalty Shooter.

Todas as classes estendem pygame.sprite.Sprite para se beneficiar do
sistema de grupos e desenho automatico do pygame.
"""
import pygame
import random
import math
from config import WIDTH, HEIGHT, RED, YELLOW, WHITE


# Constantes do gol compartilhadas (usadas por varias classes/funcoes)
GOL_LARGURA = 500
GOL_ALTURA = 180
GOL_X = (WIDTH - GOL_LARGURA) // 2
GOL_Y = 80
# Linha onde a bola "chega" no gol (um pouco dentro, nao na borda)
LINHA_GOL_Y = 200


class Mira(pygame.sprite.Sprite):
    """
    Mira de cobranca: alvo vermelho que oscila horizontalmente em frente ao gol.

    Fluxo: clica para travar a direcao horizontal -> a mira passa a oscilar
    na vertical (altura) -> clica de novo para disparar na altura escolhida.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.tamanho = 30
        self.image = pygame.Surface(
            (self.tamanho, self.tamanho), pygame.SRCALPHA
        )
        pygame.draw.circle(
            self.image, RED,
            (self.tamanho // 2, self.tamanho // 2),
            self.tamanho // 2,
            3
        )
        pygame.draw.line(self.image, RED,
                        (0, self.tamanho // 2),
                        (self.tamanho, self.tamanho // 2), 2)
        pygame.draw.line(self.image, RED,
                        (self.tamanho // 2, 0),
                        (self.tamanho // 2, self.tamanho), 2)

        self.rect = self.image.get_rect()

        # Limites horizontais (dentro do gol)
        self.x_min = GOL_X + 20
        self.x_max = GOL_X + GOL_LARGURA - 20

        # Limites verticais (dentro do gol)
        self.y_min = GOL_Y + 25    # mais alto (perto do travessao)
        self.y_max = GOL_Y + GOL_ALTURA - 25   # mais baixo

        # Posicao inicial DENTRO dos limites (evita "vibrar")
        self.rect.centerx = WIDTH // 2
        self.rect.centery = (self.y_min + self.y_max) // 2

        self.speedx = 7
        self.speedy = 4

        # Estado: 'oscilando_x', 'oscilando_y', 'disparada'
        self.estado = 'oscilando_x'

    def update(self):
        """Atualiza a posicao da mira conforme seu estado."""
        if self.estado == 'oscilando_x':
            self.rect.centerx += self.speedx
            if self.rect.centerx > self.x_max:
                self.rect.centerx = self.x_max
                self.speedx = -self.speedx
            elif self.rect.centerx < self.x_min:
                self.rect.centerx = self.x_min
                self.speedx = -self.speedx
        elif self.estado == 'oscilando_y':
            self.rect.centery += self.speedy
            if self.rect.centery > self.y_max:
                self.rect.centery = self.y_max
                self.speedy = -self.speedy
            elif self.rect.centery < self.y_min:
                self.rect.centery = self.y_min
                self.speedy = -self.speedy

    def travar_horizontal(self):
        """Para a oscilacao horizontal e comeca a oscilar na vertical."""
        self.estado = 'oscilando_y'

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

        self.raio = 15
        diametro = self.raio * 2
        self.image = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
        self._desenha_bola(self.image, self.raio)

        self.image_original = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (self.POSICAO_INICIAL_X, self.POSICAO_INICIAL_Y)

        self.speedx = 0
        self.speedy = 0
        self.escala = 1.0
        self.estado = 'parada'

        # Guarda a posicao alvo para saber quando chegou
        self.alvo_y = LINHA_GOL_Y

    def _desenha_bola(self, surf, raio):
        """Desenha uma bola branca com pentagonos pretos (estilo classico)."""
        centro = (raio, raio)
        pygame.draw.circle(surf, WHITE, centro, raio)
        pygame.draw.circle(surf, (20, 20, 20), centro, raio // 3)
        for ang in range(0, 360, 72):
            rad = math.radians(ang)
            px = int(raio + (raio * 0.65) * math.cos(rad))
            py = int(raio + (raio * 0.65) * math.sin(rad))
            pygame.draw.circle(surf, (20, 20, 20), (px, py), raio // 6)
        pygame.draw.circle(surf, (0, 0, 0), centro, raio, 2)

    def chutar(self, alvo_x, alvo_y):
        """
        Calcula a velocidade necessaria para a bola chegar ao alvo.

        A bola eh chutada com numero fixo de frames ate chegar,
        para que o movimento seja previsivel.
        """
        FRAMES_ATE_GOL = 25

        self.alvo_y = alvo_y

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
        progresso = 1 - (self.rect.centery - LINHA_GOL_Y) / (self.POSICAO_INICIAL_Y - LINHA_GOL_Y)
        progresso = max(0, min(1, progresso))
        self.escala = 1 - progresso * 0.6

        novo_tamanho = max(4, int(self.raio * 2 * self.escala))
        self.image = pygame.transform.scale(
            self.image_original, (novo_tamanho, novo_tamanho)
        )
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

        # Para quando chega na altura do alvo (que esta dentro do gol)
        if self.rect.centery <= self.alvo_y:
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
        self.alvo_y = LINHA_GOL_Y


class Goleiro(pygame.sprite.Sprite):
    """
    Goleiro: fica parado no meio do gol e mergulha para defender.

    O goleiro NUNCA avanca em direcao a bola. Soh se move lateralmente e
    em altura, sempre dentro da area do gol.
    """

    LARGURA = 70
    ALTURA = 110

    Y_MIN_GOL = GOL_Y + 30
    Y_MAX_GOL = GOL_Y + GOL_ALTURA - 10

    def __init__(self, cor_camisa=YELLOW):
        """Inicializa o goleiro com a cor da camisa especificada."""
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface(
            (self.LARGURA, self.ALTURA), pygame.SRCALPHA
        )
        self._desenha_goleiro(self.image, cor_camisa)

        self.image_original = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = (self.Y_MIN_GOL + self.Y_MAX_GOL) // 2
        self.posicao_inicial = self.rect.center

        self.estado = 'parado'
        self.alvo_x = 0
        self.alvo_y = 0
        self.frames_mergulho = 0
        self.mask = pygame.mask.from_surface(self.image)

    def _desenha_goleiro(self, surf, cor_camisa):
        """Desenha um goleiro com cabeca, tronco, bracos e luvas."""
        larg = self.LARGURA
        alt = self.ALTURA
        cx = larg // 2

        # Pernas (shorts escuros)
        pygame.draw.rect(surf, (40, 40, 60), (cx - 18, alt - 35, 14, 30))
        pygame.draw.rect(surf, (40, 40, 60), (cx + 4, alt - 35, 14, 30))
        # Tronco (camisa cor do time)
        pygame.draw.rect(surf, cor_camisa, (cx - 22, 38, 44, alt - 70),
                        border_radius=6)
        # Bracos abertos
        pygame.draw.rect(surf, cor_camisa, (0, 40, larg, 14),
                        border_radius=6)
        # Luvas nas pontas
        pygame.draw.circle(surf, WHITE, (6, 47), 8)
        pygame.draw.circle(surf, WHITE, (larg - 6, 47), 8)
        # Cabeca
        pygame.draw.circle(surf, (255, 220, 180), (cx, 22), 16)
        # Cabelo
        pygame.draw.arc(surf, (60, 40, 20),
                       (cx - 16, 6, 32, 32), 0.2, 3.0, 5)

    def mergulhar_para(self, x, y):
        """
        Inicia o mergulho do goleiro em direcao a (x, y).

        O y eh limitado a area do gol para o goleiro nunca avancar.
        """
        self.alvo_x = x
        self.alvo_y = max(self.Y_MIN_GOL, min(self.Y_MAX_GOL, y))
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

            angulo = 0
            if dx < 0:
                angulo = progresso * 50
            elif dx > 0:
                angulo = -progresso * 50

            center = self.rect.center
            self.image = pygame.transform.rotate(self.image_original, angulo)
            self.rect = self.image.get_rect()
            self.rect.center = center
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

    Mantem o controle dos resultados de cada cobranca, de quem cobra,
    e de quando a partida acabou.
    """

    TOTAL_COBRANCAS = 5

    def __init__(self, time_jogador, time_adversario):
        self.time_jogador = time_jogador
        self.time_adversario = time_adversario
        self.resultados_jogador = []
        self.resultados_adversario = []
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
        """Retorna True se a partida ja esta matematicamente decidida."""
        cobr_j = len(self.resultados_jogador)
        cobr_a = len(self.resultados_adversario)
        gols_j = self.gols_jogador()
        gols_a = self.gols_adversario()
        restantes_j = self.TOTAL_COBRANCAS - cobr_j
        restantes_a = self.TOTAL_COBRANCAS - cobr_a

        if gols_j > gols_a + restantes_a:
            return True
        if gols_a > gols_j + restantes_j:
            return True
        if cobr_j == self.TOTAL_COBRANCAS and cobr_a == self.TOTAL_COBRANCAS:
            return True
        return False

    def jogador_venceu(self):
        """Retorna True se o jogador venceu a partida."""
        if not self.partida_decidida():
            return False
        return self.gols_jogador() > self.gols_adversario()


class Batedor(pygame.sprite.Sprite):
    """
    Batedor adversario. Aparece quando o jogador esta defendendo.
    Faz uma pequena animacao de correr antes de chutar.
    """

    def __init__(self, cor_camisa=(200, 50, 50)):
        """Inicializa o batedor com a cor da camisa do time adversario."""
        pygame.sprite.Sprite.__init__(self)

        self.image_original = pygame.Surface((44, 80), pygame.SRCALPHA)
        self._desenha_batedor(self.image_original, cor_camisa)

        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2 - 100, HEIGHT - 30)
        self.posicao_chute = (WIDTH // 2, HEIGHT - 60)

        self.frames_correndo = 30
        self.estado = 'correndo'

    def _desenha_batedor(self, surf, cor_camisa):
        """Desenha o batedor com cabeca, tronco, bracos e pernas."""
        pygame.draw.rect(surf, (40, 40, 60), (12, 58, 8, 20))
        pygame.draw.rect(surf, (40, 40, 60), (24, 58, 8, 20))
        pygame.draw.rect(surf, cor_camisa, (8, 24, 28, 38), border_radius=5)
        pygame.draw.rect(surf, cor_camisa, (2, 28, 6, 22), border_radius=3)
        pygame.draw.rect(surf, cor_camisa, (36, 28, 6, 22), border_radius=3)
        pygame.draw.circle(surf, (255, 220, 180), (22, 12), 11)
        pygame.draw.arc(surf, (40, 25, 15), (11, 1, 22, 22), 0.2, 3.0, 4)

    def update(self):
        """Animacao de correr ate a bola."""
        if self.estado == 'correndo':
            dx = self.posicao_chute[0] - self.rect.centerx
            dy = self.posicao_chute[1] - self.rect.centery
            if abs(dx) > 2:
                self.rect.x += int(dx * 0.1)
            if abs(dy) > 2:
                self.rect.y += int(dy * 0.1)

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

        margem = 40
        self.alvo_x = random.randint(
            GOL_X + margem, GOL_X + GOL_LARGURA - margem
        )
        # Alvo dentro da area que o goleiro consegue alcancar
        self.alvo_y = random.randint(GOL_Y + 40, GOL_Y + GOL_ALTURA - 30)

        self.tamanho = 38
        self.image = pygame.Surface(
            (self.tamanho, self.tamanho), pygame.SRCALPHA
        )
        pygame.draw.circle(self.image, YELLOW,
                          (self.tamanho // 2, self.tamanho // 2),
                          self.tamanho // 2)
        pygame.draw.circle(self.image, RED,
                          (self.tamanho // 2, self.tamanho // 2),
                          self.tamanho // 2, 3)
        pygame.draw.line(self.image, RED, (6, 6),
                        (self.tamanho - 6, self.tamanho - 6), 3)
        pygame.draw.line(self.image, RED, (self.tamanho - 6, 6),
                        (6, self.tamanho - 6), 3)

        self.rect = self.image.get_rect()
        self.rect.center = (self.alvo_x, self.alvo_y)
        self.frames_visivel = 35

    def update(self):
        """Conta os frames de visibilidade."""
        if self.frames_visivel > 0:
            self.frames_visivel -= 1

    def expirou(self):
        """True se o tempo do alvo acabou."""
        return self.frames_visivel <= 0