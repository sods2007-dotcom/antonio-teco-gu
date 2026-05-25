"""
Tela da partida — alternancia entre cobrar e defender.
"""
import pygame
import random
import math
from config import (
    WIDTH, HEIGHT, FPS, WHITE, BLACK, GREEN_GRAMA, GRAY, GREEN, RED, YELLOW,
    MENU, FIM_PARTIDA, QUIT
)
from assets import load_assets
from sprites import Mira, Bola, Goleiro, Partida, Batedor, AlvoDefesa

# Dimensoes do gol (mesmas usadas em sprites.py)
GOL_LARGURA = 500
GOL_ALTURA = 180
GOL_X = (WIDTH - GOL_LARGURA) // 2
GOL_Y = 80


def partida_screen(window, time_jogador="Brasil", time_adversario="Argentina",
                   fase_torneio="quartas", cor_jogador=None,
                   cor_adversario=None):
    """
    Roda uma partida completa entre jogador e adversario.

    fase_torneio determina a dificuldade do CPU.
    cor_jogador e cor_adversario sao as cores das camisas dos times.
    """
    clock = pygame.time.Clock()
    assets = load_assets()

    if cor_adversario is None:
        cor_adversario = YELLOW

    if assets.get('musica_torcida'):
        try:
            pygame.mixer.music.load(assets['musica_torcida'])
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"Erro ao tocar musica: {e}")

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

        # ===== Inicializa fase de cobranca =====
        if iniciar_fase_cobranca:
            mira = Mira()
            bola = Bola()
            goleiro = Goleiro(cor_camisa=cor_adversario)
            all_sprites = pygame.sprite.Group()
            all_sprites.add(goleiro, bola, mira)
            sprites_cobranca = (mira, bola, goleiro)
            resultado_atual = ""
            iniciar_fase_cobranca = False

        # ===== Inicializa fase de defesa =====
        if iniciar_fase_defesa:
            batedor = Batedor(cor_camisa=cor_adversario)
            bola_cpu = Bola()
            goleiro_jogador = Goleiro(cor_camisa=cor_jogador or YELLOW)
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

            # ----- Cobranca: dois cliques (direcao, depois altura) -----
            if partida.fase == 'jogador_cobra' and sprites_cobranca:
                mira, bola, goleiro = sprites_cobranca
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mira.estado == 'oscilando_x':
                        mira.travar_horizontal()
                    elif mira.estado == 'oscilando_y':
                        alvo_pos = mira.disparar()
                        bola.chutar(alvo_pos[0], alvo_pos[1])
                        if assets.get('chute'):
                            assets['chute'].play()
                        all_sprites.remove(mira)
                        if cpu_vai_defender(alvo_pos, fase_torneio):
                            goleiro.mergulhar_para(alvo_pos[0], alvo_pos[1])
                        else:
                            if alvo_pos[0] < WIDTH // 2:
                                lado_errado = WIDTH // 2 + 150
                            else:
                                lado_errado = WIDTH // 2 - 150
                            goleiro.mergulhar_para(lado_errado, 200)

            # ----- Defesa: jogador clica onde acha que a bola vai -----
            if partida.fase == 'jogador_defende' and sprites_defesa:
                batedor, bola_cpu, goleiro_jogador, alvo_def = sprites_defesa
                if event.type == pygame.MOUSEBUTTONDOWN and not chute_cpu_disparado:
                    goleiro_jogador.mergulhar_para(event.pos[0], event.pos[1])
                    bola_cpu.chutar(alvo_def.alvo_x, alvo_def.alvo_y)
                    if assets.get('chute'):
                        assets['chute'].play()
                    chute_cpu_disparado = True

        # ===== Atualiza tudo =====
        all_sprites.update()

        if (partida.fase == 'jogador_defende'
                and sprites_defesa
                and not chute_cpu_disparado):
            batedor, bola_cpu, goleiro_j, alvo_def = sprites_defesa
            if batedor.acabou_correr():
                if alvo_def not in all_sprites:
                    all_sprites.add(alvo_def)
                alvo_def.update()
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
        desenha_placar(window, assets, partida)
        desenha_mensagem(window, assets, partida, resultado_atual,
                         sprites_cobranca, sprites_defesa,
                         chute_cpu_disparado)

        if partida.fase == 'jogador_cobra' and sprites_cobranca:
            mira, bola, _ = sprites_cobranca
            desenha_linha_mira(window, mira, bola)

        if resultado_atual:
            desenha_anim_resultado(window, resultado_atual,
                                   frames_mostra_resultado)

        pygame.display.update()

    pygame.mixer.music.stop()

    return next_state, partida


def cpu_vai_defender(alvo_pos, fase_torneio="quartas"):
    """Decide se o goleiro CPU vai defender, baseado na fase do torneio."""
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
        if eh_defesa:
            if assets.get('perdeu'):
                assets['perdeu'].play()
        else:
            if assets.get('gol'):
                assets['gol'].play()
    elif resultado == 'DEFENDIDA':
        if eh_defesa:
            if assets.get('gol'):
                assets['gol'].play()
        else:
            if assets.get('perdeu'):
                assets['perdeu'].play()
    elif resultado == 'TRAVE':
        if assets.get('trave'):
            assets['trave'].play()


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
    caixa = pygame.Surface(
        (texto.get_width() + 30, texto.get_height() + 6),
        pygame.SRCALPHA
    )
    caixa.fill((0, 0, 0, 180))
    caixa_rect = caixa.get_rect(center=texto_rect.center)
    window.blit(caixa, caixa_rect)
    window.blit(texto, texto_rect)


def desenha_linha_mira(window, mira, bola):
    """Linha pontilhada da bola ate a mira."""
    if mira.estado not in ('oscilando_x', 'oscilando_y'):
        return
    bx, by = bola.rect.center
    mx, my = mira.rect.center
    num_pontos = 15
    for i in range(num_pontos):
        if i % 2 == 0:
            t = i / num_pontos
            x = int(bx + (mx - bx) * t)
            y = int(by + (my - by) * t)
            pygame.draw.circle(window, (255, 255, 255), (x, y), 2)


def desenha_anim_resultado(window, resultado_atual, frame_restante):
    """Texto gigante pulsando quando ha resultado."""
    if not resultado_atual:
        return
    progresso = frame_restante / (FPS * 2)
    fonte_tamanho = int(120 + 20 * abs(progresso - 0.5))
    cores_textos = {
        'GOL': (YELLOW, "GOL!!!"),
        'DEFENDIDA': ((100, 200, 255), "DEFESA!"),
        'TRAVE': ((255, 100, 100), "NA TRAVE!"),
        'FORA': ((180, 180, 180), "FORA!"),
    }
    if resultado_atual not in cores_textos:
        return
    cor, texto = cores_textos[resultado_atual]
    if progresso < 0.2:
        alpha = int(255 * (progresso / 0.2))
    else:
        alpha = 255
    fonte = pygame.font.SysFont(None, fonte_tamanho)
    render = fonte.render(texto, True, cor)
    render.set_alpha(alpha)
    rect = render.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(render, rect)


def verifica_gol(bola):
    """Verifica se a bola entrou no gol, na trave ou fora."""
    bx = bola.rect.centerx
    by = bola.rect.centery
    margem_trave = 10

    if (abs(bx - GOL_X) < margem_trave
            and GOL_Y <= by <= GOL_Y + GOL_ALTURA):
        return 'TRAVE'
    if (abs(bx - (GOL_X + GOL_LARGURA)) < margem_trave
            and GOL_Y <= by <= GOL_Y + GOL_ALTURA):
        return 'TRAVE'
    if (abs(by - GOL_Y) < margem_trave
            and GOL_X <= bx <= GOL_X + GOL_LARGURA):
        return 'TRAVE'

    if (GOL_X - 5 <= bx <= GOL_X + GOL_LARGURA + 5
            and GOL_Y - 5 <= by <= GOL_Y + GOL_ALTURA + 5):
        return 'GOL'

    return 'FORA'


def desenha_campo(window):
    """Desenha o campo com gramado listrado, area e marca do penalti."""
    # Ceu / arquibancada ao fundo (faixa superior escura)
    window.fill((30, 60, 30))
    pygame.draw.rect(window, (45, 45, 70), (0, 0, WIDTH, 70))
    # Pequenos "pontos" simulando torcida na arquibancada
    for i in range(0, WIDTH, 14):
        cor_torcida = [(200, 80, 80), (80, 80, 200), (220, 220, 80),
                       (220, 220, 220)][(i // 14) % 4]
        pygame.draw.circle(window, cor_torcida, (i + 7, 35), 3)

    # Gramado listrado (faixas alternadas de verde)
    topo_grama = 70
    altura_faixa = 40
    n_faixas = (HEIGHT - topo_grama) // altura_faixa + 1
    for i in range(n_faixas):
        y = topo_grama + i * altura_faixa
        cor = (38, 120, 38) if i % 2 == 0 else (48, 140, 48)
        pygame.draw.rect(window, cor, (0, y, WIDTH, altura_faixa))

    # Grande arco da area (semicirculo branco)
    pygame.draw.arc(window, WHITE,
                   (WIDTH // 2 - 180, GOL_Y + GOL_ALTURA - 40, 360, 200),
                   3.3, 6.1, 3)

    # Marca do penalti (ponto branco de onde a bola sai)
    pygame.draw.circle(window, WHITE, (WIDTH // 2, HEIGHT - 80), 5)

    # Linha da pequena area
    area_larg = GOL_LARGURA + 120
    area_x = (WIDTH - area_larg) // 2
    area_y = GOL_Y + GOL_ALTURA
    pygame.draw.rect(window, WHITE,
                    (area_x, GOL_Y, area_larg, area_y - GOL_Y), 3)


def desenha_gol(window):
    """Desenha o gol com traves arredondadas e rede em malha."""
    # Rede (fundo semi-transparente)
    rede = pygame.Surface((GOL_LARGURA, GOL_ALTURA), pygame.SRCALPHA)
    rede.fill((220, 220, 220, 60))
    window.blit(rede, (GOL_X, GOL_Y))

    # Malha da rede (linhas finas em diagonal cruzada)
    cor_rede = (255, 255, 255, 90)
    for x in range(GOL_X, GOL_X + GOL_LARGURA + 1, 20):
        pygame.draw.line(window, (200, 200, 200),
                        (x, GOL_Y), (x, GOL_Y + GOL_ALTURA), 1)
    for y in range(GOL_Y, GOL_Y + GOL_ALTURA + 1, 20):
        pygame.draw.line(window, (200, 200, 200),
                        (GOL_X, y), (GOL_X + GOL_LARGURA, y), 1)

    # Traves grossas brancas (com leve sombra)
    espessura = 8
    # Sombra
    pygame.draw.rect(window, (180, 180, 180),
                    (GOL_X - espessura + 2, GOL_Y + 2,
                     espessura, GOL_ALTURA + espessura))
    # Trave esquerda
    pygame.draw.rect(window, WHITE,
                    (GOL_X - espessura, GOL_Y, espessura,
                     GOL_ALTURA + espessura), border_radius=3)
    # Trave direita
    pygame.draw.rect(window, WHITE,
                    (GOL_X + GOL_LARGURA, GOL_Y, espessura,
                     GOL_ALTURA + espessura), border_radius=3)
    # Travessao
    pygame.draw.rect(window, WHITE,
                    (GOL_X - espessura, GOL_Y - espessura,
                     GOL_LARGURA + espessura * 2, espessura),
                    border_radius=3)


def desenha_placar(window, assets, partida):
    """Placar com nome dos times e bolinhas de cada cobranca."""
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
        return
    if partida.fase == 'jogador_cobra' and sprites_cobranca:
        mira, _, _ = sprites_cobranca
        if mira.estado == 'oscilando_x':
            msg = "Clique para travar a DIRECAO"
            cor = WHITE
        elif mira.estado == 'oscilando_y':
            msg = "Clique para travar a ALTURA e chutar"
            cor = YELLOW
        else:
            return
        texto = assets['font_pequena'].render(msg, True, cor)
        window.blit(texto,
                   (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))
    elif partida.fase == 'jogador_defende' and not chute_cpu:
        msg = "Clique onde a bola vai para defender!"
        texto = assets['font_pequena'].render(msg, True, YELLOW)
        window.blit(texto,
                   (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 40))