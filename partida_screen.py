"""
Tela da partida — alternancia entre cobrar e defender.
"""
import pygame
import random
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, GRAY, GREEN, RED, YELLOW,
    MENU, FIM_PARTIDA, QUIT
)
from assets import load_assets
from sprites import Mira, Bola, Goleiro, Partida, Batedor, AlvoDefesa


def partida_screen(window, time_jogador="Brasil",
                   time_adversario="Argentina",
                   fase_torneio="quartas",
                   cor_jogador=None,
                   cor_adversario=None):
    """
    Roda uma partida completa entre jogador e adversario.

    fase_torneio determina a dificuldade do CPU:
    - quartas: facil (35% defesa)
    - semi: medio (45% defesa)
    - final: dificil (55% defesa)
    """
    clock = pygame.time.Clock()
    assets = load_assets()

    partida = Partida(time_jogador, time_adversario)

    sprites_cobranca = None
    sprites_defesa = None

    iniciar_fase_cobranca = True
    iniciar_fase_defesa = False
    chute_cpu_disparado = False
    resultado_atual = ""
    frames_mostra_resultado = 0

    running = True
    next_state = MENU

    while running:
        clock.tick(FPS)

        # ===== Inicializa fase de cobranca quando precisar =====
        if iniciar_fase_cobranca:
            mira = Mira()
            bola = Bola()
            goleiro = Goleiro(cor_camisa=cor_adversario or YELLOW)
            all_sprites = pygame.sprite.Group()
            all_sprites.add(goleiro, bola, mira)
            sprites_cobranca = (mira, bola, goleiro)
            resultado_atual = ""
            iniciar_fase_cobranca = False

        # ===== Inicializa fase de defesa quando precisar =====
        if iniciar_fase_defesa:
            batedor = Batedor(cor_camisa=cor_adversario or (200, 50, 50))
            bola_cpu = Bola()
            goleiro_jogador = Goleiro()
            alvo = AlvoDefesa()
            all_sprites = pygame.sprite.Group()
            all_sprites.add(batedor, bola_cpu, goleiro_jogador)
            sprites_defesa = (batedor, bola_cpu, goleiro_jogador, alvo)
            chute_cpu_disparado = False
            resultado_atual = ""
            iniciar_fase_defesa = False

        # ===== Eventos =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            # ----- Cobranca: cliques na mira -----
            if partida.fase == 'jogador_cobra' and sprites_cobranca:
                mira, bola, goleiro = sprites_cobranca
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
                        if cpu_vai_defender(alvo_pos, fase_torneio):
                            goleiro.mergulhar_para(alvo_pos[0], alvo_pos[1])
                        else:
                            lado_x = random.choice(
                                [WIDTH // 2 - 200, WIDTH // 2 + 200]
                            )
                            goleiro.mergulhar_para(lado_x, 200)

            # ----- Defesa: jogador clica no alvo -----
            if partida.fase == 'jogador_defende' and sprites_defesa:
                batedor, bola_cpu, goleiro_jogador, alvo_def = sprites_defesa
                if event.type == pygame.MOUSEBUTTONDOWN and not chute_cpu_disparado:
                    if alvo_def.rect.collidepoint(event.pos):
                        # Acertou o alvo — goleiro pula no lugar certo
                        goleiro_jogador.mergulhar_para(
                            alvo_def.alvo_x, alvo_def.alvo_y
                        )
                    else:
                        # Errou — goleiro vai pra onde clicou
                        goleiro_jogador.mergulhar_para(
                            event.pos[0], event.pos[1]
                        )
                    bola_cpu.chutar(alvo_def.alvo_x, alvo_def.alvo_y)
                    if assets.get('chute'):
                        assets['chute'].play()
                    chute_cpu_disparado = True

        # ===== Atualiza tudo =====
        all_sprites.update()

        # Controla o alvo de defesa (some quando batedor termina e dispara se demora)
        if (partida.fase == 'jogador_defende'
                and sprites_defesa
                and not chute_cpu_disparado):
            batedor, bola_cpu, goleiro_j, alvo_def = sprites_defesa

            if batedor.acabou_correr():
                if alvo_def not in all_sprites:
                    all_sprites.add(alvo_def)
                alvo_def.update()
                # Se o tempo expirou e o jogador nao clicou
                if alvo_def.expirou():
                    bola_cpu.chutar(alvo_def.alvo_x, alvo_def.alvo_y)
                    if assets.get('chute'):
                        assets['chute'].play()
                    chute_cpu_disparado = True

        # ===== Verifica resultado =====
        if partida.fase == 'jogador_cobra' and resultado_atual == "":
            mira, bola, goleiro = sprites_cobranca
            if bola.estado == 'parou_no_gol':
                if pygame.sprite.collide_mask(bola, goleiro):
                    resultado_atual = "DEFENDIDA"
                else:
                    resultado_atual = verifica_gol(bola)
                partida.registra_resultado_jogador(resultado_atual)
                tocar_som_resultado(assets, resultado_atual)
                frames_mostra_resultado = FPS * 2

        elif partida.fase == 'jogador_defende' and resultado_atual == "":
            _, bola_cpu, goleiro_j, _ = sprites_defesa
            if bola_cpu.estado == 'parou_no_gol':
                if pygame.sprite.collide_mask(bola_cpu, goleiro_j):
                    resultado_atual = "DEFENDIDA"
                else:
                    resultado_atual = verifica_gol(bola_cpu)
                partida.registra_resultado_adversario(resultado_atual)
                tocar_som_resultado(assets, resultado_atual, eh_defesa=True)
                frames_mostra_resultado = FPS * 2

        # ===== Avanca para proxima fase =====
        if frames_mostra_resultado > 0:
            frames_mostra_resultado -= 1
            if frames_mostra_resultado == 0:
                if partida.fase == 'fim':
                    running = False
                    next_state = FIM_PARTIDA
                elif partida.fase == 'jogador_defende':
                    iniciar_fase_defesa = True
                elif partida.fase == 'jogador_cobra':
                    iniciar_fase_cobranca = True

        # ===== Desenha tudo =====
        desenha_campo(window)
        desenha_gol(window)
        all_sprites.draw(window)
        desenha_titulo_fase(window, assets, fase_torneio)

        if partida.fase == 'jogador_cobra' and sprites_cobranca:
            mira, bola, _ = sprites_cobranca
            desenha_linha_mira(window, mira, bola)

        desenha_placar(window, assets, partida)
        desenha_mensagem(window, assets, partida, resultado_atual,
                         sprites_cobranca, sprites_defesa,
                         chute_cpu_disparado)

        pygame.display.update()

    return next_state, partida


def cpu_vai_defender(alvo_pos, fase_torneio="quartas"):
    """
    Decide se o goleiro CPU vai defender, baseado na fase do torneio.

    Quanto mais avancada a fase, maior a chance de defesa.
    A chance ainda eh reduzida para chutes mais perto dos cantos.
    """
    chances_base = {
        'quartas': 0.35,
        'semi': 0.45,
        'final': 0.55,
    }
    chance_base = chances_base.get(fase_torneio, 0.4)

    x = alvo_pos[0]
    distancia_centro = abs(x - WIDTH // 2)
    chance = chance_base - (distancia_centro / 500)
    return random.random() < max(0.15, chance)


def tocar_som_resultado(assets, resultado, eh_defesa=False):
    """Toca o som correto, considerando se a cobranca foi do jogador ou CPU."""
    if resultado == 'GOL':
        # CPU marcar gol contra voce = som de perdeu
        if eh_defesa:
            if assets.get('perdeu'):
                assets['perdeu'].play()
        else:
            if assets.get('gol'):
                assets['gol'].play()
    elif resultado == 'DEFENDIDA':
        # Voce defendeu = comemora; CPU defendeu = lamenta
        if eh_defesa:
            if assets.get('gol'):
                assets['gol'].play()
        else:
            if assets.get('perdeu'):
                assets['perdeu'].play()
    elif resultado == 'TRAVE':
        if assets.get('trave'):
            assets['trave'].play()


def verifica_gol(bola):
    """Verifica se a bola entrou no gol, na trave ou fora."""
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
    """Desenha o fundo."""
    window.fill(GREEN_GRAMA)
    pygame.draw.line(window, WHITE, (0, HEIGHT - 100),
                    (WIDTH, HEIGHT - 100), 2)


def desenha_gol(window):
    """Desenha o gol completo."""
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
    """Placar com bolinhas de cada cobranca."""
    texto_j = assets['font_pequena'].render(partida.time_jogador, True, WHITE)
    texto_a = assets['font_pequena'].render(partida.time_adversario, True, WHITE)
    window.blit(texto_j, (20, 10))
    window.blit(texto_a, (WIDTH - texto_a.get_width() - 20, 10))

    raio = 8
    espacamento = 22
    for i in range(5):
        x = 20 + i * espacamento
        y = 45
        if i < len(partida.resultados_jogador):
            cor = GREEN if partida.resultados_jogador[i] == 'GOL' else RED
        else:
            cor = (60, 60, 60)
        pygame.draw.circle(window, cor, (x, y), raio)
        pygame.draw.circle(window, WHITE, (x, y), raio, 2)

        x = WIDTH - 20 - i * espacamento - raio
        if i < len(partida.resultados_adversario):
            cor = GREEN if partida.resultados_adversario[i] == 'GOL' else RED
        else:
            cor = (60, 60, 60)
        pygame.draw.circle(window, cor, (x, y), raio)
        pygame.draw.circle(window, WHITE, (x, y), raio, 2)


def desenha_mensagem(window, assets, partida, resultado_atual,
                     sprites_cobranca, sprites_defesa, chute_cpu):
    """Mensagem do rodape conforme a fase."""
    if resultado_atual:
        cor = GREEN if resultado_atual == 'GOL' else RED
        texto = assets['font_media'].render(resultado_atual, True, cor)
        window.blit(texto,
                   (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 60))
        return

    if partida.fase == 'jogador_cobra' and sprites_cobranca:
        mira, _, _ = sprites_cobranca
        if mira.estado == 'oscilando_x':
            msg = "Clique para travar direcao"
            cor = WHITE
        elif mira.estado == 'subindo':
            msg = "Solte para chutar"
            cor = WHITE
        else:
            return
        texto = assets['font_pequena'].render(msg, True, cor)
        window.blit(texto,
                   (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
    elif partida.fase == 'jogador_defende' and not chute_cpu:
        msg = "Clique no alvo para defender!"
        texto = assets['font_pequena'].render(msg, True, YELLOW)
        window.blit(texto,
                   (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
def desenha_titulo_fase(window, assets, fase_torneio):
    """Mostra QUARTAS / SEMIFINAL / FINAL no topo da tela."""
    titulos = {
        'quartas': 'QUARTAS DE FINAL',
        'semi': 'SEMIFINAL',
        'final': 'FINAL',
    }
    titulo_texto = titulos.get(fase_torneio, '')
    if not titulo_texto:
        return
    cor = YELLOW if fase_torneio == 'final' else WHITE
    texto = assets['font_pequena'].render(titulo_texto, True, cor)
    texto_rect = texto.get_rect(center=(WIDTH // 2, 30))
    # Caixa preta semi-transparente atras
    caixa = pygame.Surface(
        (texto.get_width() + 30, texto.get_height() + 6),
        pygame.SRCALPHA
    )
    caixa.fill((0, 0, 0, 180))
    caixa_rect = caixa.get_rect(center=texto_rect.center)
    window.blit(caixa, caixa_rect)
    window.blit(texto, texto_rect)
def desenha_linha_mira(window, mira, bola):
    """Linha pontilhada da bola ate a mira (so durante cobranca)."""
    if mira.estado not in ('oscilando_x', 'subindo'):
        return
    bx, by = bola.rect.center
    mx, my = mira.rect.center
    num_pontos = 15
    for i in range(num_pontos):
        if i % 2 == 0:
            t = i / num_pontos
            x = int(bx + (mx - bx) * t)
            y = int(by + (my - by) * t)
            pygame.draw.circle(window, (255, 255, 255, 100), (x, y), 2)