"""
Classes (sprites) usadas no jogo Penalty Shooter.

Todas as classes estendem pygame.sprite.Sprite para se beneficiar do
sistema de grupos e desenho automatico do pygame.
"""
import pygame
import random
import math
from config import WIDTH, HEIGHT, RED, YELLOW, WHITE


# Constantes do gol compartilhadas
GOL_LARGURA = 460
GOL_ALTURA = 170
GOL_X = (WIDTH - GOL_LARGURA) // 2
GOL_Y = 90
LINHA_GOL_Y = 195


class Mira(pygame.sprite.Sprite):
    """
    Mira de cobranca: alvo vermelho que oscila em frente ao gol.

    Fluxo: clica para travar a direcao horizontal -> a mira oscila na
    vertical (altura) -> clica de novo para disparar na altura escolhida.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.tamanho = 34
        self.image = pygame.Surface(
            (self.tamanho, self.tamanho), pygame.SRCALPHA
        )
        c = self.tamanho // 2
        pygame.draw.circle(self.image, RED, (c, c), c, 3)
        pygame.draw.circle(self.image, (255, 255, 255), (c, c), 5)
        pygame.draw.circle(self.image, RED, (c, c), 5, 2)
        pygame.draw.line(self.image, RED, (0, c), (self.tamanho, c), 2)
        pygame.draw.line(self.image, RED, (c, 0), (c, self.tamanho), 2)

        self.rect = self.image.get_rect()
        self.x_min = GOL_X + 25
        self.x_max = GOL_X + GOL_LARGURA - 25
        self.y_min = GOL_Y + 25
        self.y_max = GOL_Y + GOL_ALTURA - 25
        self.rect.centerx = WIDTH // 2
        self.rect.centery = (self.y_min + self.y_max) // 2
        self.speedx = 7
        self.speedy = 4
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
    Bola de futebol. Parada no centro inferior, depois chutada para um alvo.
    Diminui de tamanho conforme se aproxima do gol (profundidade).
    """

    POSICAO_INICIAL_X = WIDTH // 2
    POSICAO_INICIAL_Y = HEIGHT - 75

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.raio = 18
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
        self.alvo_y = LINHA_GOL_Y

    def _desenha_bola(self, surf, raio):
        """Desenha uma bola branca com pentagonos pretos (estilo classico)."""
        centro = (raio, raio)
        pygame.draw.circle(surf, (235, 235, 235), centro, raio)
        pygame.draw.circle(surf, WHITE, (raio - 3, raio - 3), raio - 4)
        pygame.draw.circle(surf, (25, 25, 25), centro, raio // 3)
        for ang in range(0, 360, 72):
            rad = math.radians(ang - 90)
            px = int(raio + (raio * 0.62) * math.cos(rad))
            py = int(raio + (raio * 0.62) * math.sin(rad))
            pygame.draw.circle(surf, (25, 25, 25), (px, py), raio // 5)
        pygame.draw.circle(surf, (0, 0, 0), centro, raio, 2)

    def chutar(self, alvo_x, alvo_y):
        """Calcula a velocidade para a bola chegar ao alvo em 25 frames."""
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
        progresso = 1 - (self.rect.centery - LINHA_GOL_Y) / (self.POSICAO_INICIAL_Y - LINHA_GOL_Y)
        progresso = max(0, min(1, progresso))
        self.escala = 1 - progresso * 0.45
        novo_tamanho = max(8, int(self.raio * 2 * self.escala))
        self.image = pygame.transform.scale(
            self.image_original, (novo_tamanho, novo_tamanho)
        )
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
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
    Goleiro: fica no meio do gol e mergulha para defender.
    Nunca avanca em direcao a bola (Y limitado a area do gol).
    """

    LARGURA = 76
    ALTURA = 118
    Y_MIN_GOL = GOL_Y + 30
    Y_MAX_GOL = GOL_Y + GOL_ALTURA - 5

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
        """Desenha um goleiro com cabeca, tronco, bracos, luvas e meioes."""
        larg = self.LARGURA
        alt = self.ALTURA
        cx = larg // 2
        pygame.draw.rect(surf, (235, 235, 235), (cx - 17, alt - 40, 13, 22))
        pygame.draw.rect(surf, (235, 235, 235), (cx + 4, alt - 40, 13, 22))
        pygame.draw.rect(surf, (30, 30, 50), (cx - 17, alt - 18, 13, 14))
        pygame.draw.rect(surf, (30, 30, 50), (cx + 4, alt - 18, 13, 14))
        pygame.draw.rect(surf, (40, 40, 60), (cx - 20, alt - 48, 40, 14),
                        border_radius=3)
        pygame.draw.rect(surf, cor_camisa, (cx - 23, 42, 46, alt - 92),
                        border_radius=8)
        fonte = pygame.font.SysFont(None, 22)
        num = fonte.render("1", True, (255, 255, 255))
        surf.blit(num, (cx - num.get_width() // 2, 56))
        pygame.draw.rect(surf, cor_camisa, (0, 44, larg, 14), border_radius=7)
        pygame.draw.circle(surf, WHITE, (7, 51), 10)
        pygame.draw.circle(surf, (200, 200, 200), (7, 51), 10, 2)
        pygame.draw.circle(surf, WHITE, (larg - 7, 51), 10)
        pygame.draw.circle(surf, (200, 200, 200), (larg - 7, 51), 10, 2)
        pygame.draw.circle(surf, (255, 220, 180), (cx, 26), 18)
        pygame.draw.arc(surf, (60, 40, 20), (cx - 18, 8, 36, 36), 0.2, 3.0, 7)

    def mergulhar_para(self, x, y):
        """Inicia o mergulho em direcao a (x, y), limitando o Y ao gol."""
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
            progresso = min(1.0, self.frames_mergulho / FRAMES_TOTAL)
            self.rect.centerx = self.posicao_inicial[0] + int(dx * progresso)
            self.rect.centery = self.posicao_inicial[1] + int(dy * progresso)
            angulo = 0
            if dx < 0:
                angulo = progresso * 55
            elif dx > 0:
                angulo = -progresso * 55
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

    Apos 5 cobrancas para cada lado, se houver empate, entra em MORTE
    SUBITA: cada um cobra 1 vez por rodada, e quem fizer a diferenca numa
    rodada completa vence.
    """

    TOTAL_COBRANCAS = 5

    def __init__(self, time_jogador, time_adversario):
        self.time_jogador = time_jogador
        self.time_adversario = time_adversario
        self.resultados_jogador = []
        self.resultados_adversario = []
        self.fase = 'jogador_cobra'
        self.cobranca_atual = 1
        self.morte_subita = False  # vira True quando empata apos as 5

    def registra_resultado_jogador(self, resultado):
        """Registra o resultado de uma cobranca do jogador."""
        self.resultados_jogador.append(resultado)
        self._atualiza_morte_subita()
        if not self.partida_decidida():
            self.fase = 'jogador_defende'
        else:
            self.fase = 'fim'

    def registra_resultado_adversario(self, resultado):
        """Registra o resultado de uma cobranca do adversario."""
        self.resultados_adversario.append(resultado)
        self._atualiza_morte_subita()
        if not self.partida_decidida():
            self.fase = 'jogador_cobra'
            self.cobranca_atual += 1
        else:
            self.fase = 'fim'

    def _atualiza_morte_subita(self):
        """Liga a morte subita se as 5 cobrancas acabaram empatadas."""
        cobr_j = len(self.resultados_jogador)
        cobr_a = len(self.resultados_adversario)
        if (cobr_j >= self.TOTAL_COBRANCAS
                and cobr_a >= self.TOTAL_COBRANCAS
                and self.gols_jogador() == self.gols_adversario()):
            self.morte_subita = True

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

        # Durante as 5 cobrancas normais
        if cobr_j < self.TOTAL_COBRANCAS or cobr_a < self.TOTAL_COBRANCAS:
            restantes_j = self.TOTAL_COBRANCAS - cobr_j
            restantes_a = self.TOTAL_COBRANCAS - cobr_a
            if gols_j > gols_a + restantes_a:
                return True
            if gols_a > gols_j + restantes_j:
                return True
            return False

        # Apos as 5 cobrancas: so acaba se nao estiver empatado E
        # ambos tiverem cobrado o mesmo numero de vezes (rodada completa)
        if cobr_j == cobr_a and gols_j != gols_a:
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
    Faz uma animacao de correr antes de chutar.
    """

    def __init__(self, cor_camisa=(200, 50, 50)):
        """Inicializa o batedor com a cor da camisa do time adversario."""
        pygame.sprite.Sprite.__init__(self)
        self.image_original = pygame.Surface((48, 88), pygame.SRCALPHA)
        self._desenha_batedor(self.image_original, cor_camisa)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2 - 110, HEIGHT - 30)
        self.posicao_chute = (WIDTH // 2, HEIGHT - 60)
        self.frames_correndo = 30
        self.estado = 'correndo'

    def _desenha_batedor(self, surf, cor_camisa):
        """Desenha o batedor com cabeca, tronco, bracos e pernas."""
        pygame.draw.rect(surf, (235, 235, 235), (14, 60, 9, 18))
        pygame.draw.rect(surf, (235, 235, 235), (26, 60, 9, 18))
        pygame.draw.rect(surf, (30, 30, 50), (14, 76, 9, 10))
        pygame.draw.rect(surf, (30, 30, 50), (26, 76, 9, 10))
        pygame.draw.rect(surf, (40, 40, 60), (12, 54, 25, 10))
        pygame.draw.rect(surf, cor_camisa, (10, 26, 28, 32), border_radius=5)
        pygame.draw.rect(surf, cor_camisa, (3, 30, 7, 22), border_radius=3)
        pygame.draw.rect(surf, cor_camisa, (38, 30, 7, 22), border_radius=3)
        pygame.draw.circle(surf, (255, 220, 180), (24, 14), 12)
        pygame.draw.arc(surf, (40, 25, 15), (12, 2, 24, 24), 0.2, 3.0, 5)

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
                self.image = pygame.transform.rotate(self.image_original, 6)
            else:
                self.image = pygame.transform.rotate(self.image_original, -6)
            self.frames_correndo -= 1
            if self.frames_correndo <= 0:
                self.estado = 'parado'
                self.image = self.image_original.copy()

    def acabou_correr(self):
        """Retorna True se o batedor ja chegou e parou."""
        return self.estado == 'parado'


class AlvoDefesa(pygame.sprite.Sprite):
    """
    Alvo amarelo que aparece num ponto do gol durante a defesa.
    O jogador clica nele para o goleiro mergulhar. Some apos ~1 segundo.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        margem = 45
        self.alvo_x = random.randint(
            GOL_X + margem, GOL_X + GOL_LARGURA - margem
        )
        self.alvo_y = random.randint(GOL_Y + 40, GOL_Y + GOL_ALTURA - 25)
        self.tamanho = 40
        self.image = pygame.Surface(
            (self.tamanho, self.tamanho), pygame.SRCALPHA
        )
        c = self.tamanho // 2
        pygame.draw.circle(self.image, YELLOW, (c, c), c)
        pygame.draw.circle(self.image, RED, (c, c), c, 3)
        pygame.draw.line(self.image, RED, (7, 7),
                        (self.tamanho - 7, self.tamanho - 7), 3)
        pygame.draw.line(self.image, RED, (self.tamanho - 7, 7),
                        (7, self.tamanho - 7), 3)
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