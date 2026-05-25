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
from sprites import (
    Mira, Bola, Goleiro, Partida, Batedor, AlvoDefesa,
    GOL_LARGURA, GOL_ALTURA, GOL_X, GOL_Y
)


def partida_screen(window, time_jogador="Brasil", time_adversario="Argentina",
                   fase_torneio="quartas", cor_jogador=None,
                   cor_adversario=None):
    """
    Roda uma partida completa entre jogador e adversario.

    Apos 5 cobrancas, se empatar, entra em morte subita.
    fase_torneio determina a dificuldade do CPU (quartas < semi < final).
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
    delay_inicio = 0
    aviso_fase = ""
    frames_aviso = 0
    pausado = False
    ja_avisou_prorrogacao = False

    running = True
    next_state = MENU

    while running:
        clock.tick(FPS)

        # ===== Inicializa fase de cobranca =====
        if iniciar_fase_cobranca and not pausado:
            mira = Mira()
            bola = Bola()
            goleiro = Goleiro(cor_camisa=cor_adversario)
            all_sprites = pygame.sprite.Group()
            all_sprites.add(goleiro, bola, mira)
            sprites_cobranca = (mira, bola, goleiro)
            resultado_atual = ""
            iniciar_fase_cobranca = False
            delay_inicio = FPS // 2
            # Aviso de prorrogacao na primeira cobranca da morte subita
            if partida.morte_subita and not ja_avisou_prorrogacao:
                aviso_fase = "PRORROGACAO!"
                ja_avisou_prorrogacao = True
            else:
                aviso_fase = "VOCE COBRA!"
            frames_aviso = FPS

        # ===== Inicializa fase de defesa =====
        if iniciar_fase_defesa and not pausado:
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
            delay_inicio = FPS // 2
            aviso_fase = "AGORA VOCE DEFENDE!"
            frames_aviso = FPS

        if delay_inicio > 0:
            delay_inicio -= 1

        # ===== Eventos =====
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_state = QUIT
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_p:
                    pausado = not pausado  # liga/desliga pausa

            if pausado or delay_inicio > 0:
                continue

            # ----- Cobranca: dois cliques -----
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
                        decide_defesa_cpu(goleiro, alvo_pos, fase_torneio)

            # ----- Defesa: jogador clica onde acha que a bola vai -----
            if partida.fase == 'jogador_defende' and sprites_defesa:
                batedor, bola_cpu, goleiro_jogador, alvo_def = sprites_defesa
                if event.type == pygame.MOUSEBUTTONDOWN and not chute_cpu_disparado:
                    goleiro_jogador.mergulhar_para(event.pos[0], event.pos[1])
                    bola_cpu.chutar(alvo_def.alvo_x, alvo_def.alvo_y)
                    if assets.get('chute'):
                        assets['chute'].play()
                    chute_cpu_disparado = True

        # Se pausado, so desenha a tela de pausa e pula o resto
        if pausado:
            desenha_pausa(window, assets)
            pygame.display.update()
            continue

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

        if frames_aviso > 0:
            frames_aviso -= 1

        # ===== Desenha tudo =====
        desenha_campo(window)
        desenha_gol(window)
        desenha_sombras(window, sprites_cobranca, sprites_defesa, partida)
        all_sprites.draw(window)
        desenha_titulo_fase(window, assets, fase_torneio, partida)
        desenha_contador(window, assets, partida)
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

        if frames_aviso > 0 and not resultado_atual:
            desenha_aviso_fase(window, assets, aviso_fase)

        # Dica de pausa no canto
        dica = assets['font_pequena'].render("P = Pausar", True, (200, 200, 200))
        window.blit(dica, (WIDTH - dica.get_width() - 10, HEIGHT - 28))

        pygame.display.update()

    pygame.mixer.music.stop()
    return next_state, partida


def decide_defesa_cpu(goleiro, alvo_pos, fase_torneio):
    """
    Decide para onde o goleiro CPU mergulha.

    Quartas 35% / Semi 55% / Final 75% de chance de ir no alvo certo
    (reduzido nos cantos).
    """
    chances_base = {
        'quartas': 0.35,
        'semi': 0.55,
        'final': 0.75,
    }
    chance_base = chances_base.get(fase_torneio, 0.45)
    distancia_centro = abs(alvo_pos[0] - WIDTH // 2)
    chance = max(0.15, chance_base - (distancia_centro / 600))

    if random.random() < chance:
        goleiro.mergulhar_para(alvo_pos[0], alvo_pos[1])
    else:
        if alvo_pos[0] < WIDTH // 2:
            lado_errado = WIDTH // 2 + 150
        else:
            lado_errado = WIDTH // 2 - 150
        goleiro.mergulhar_para(lado_errado, GOL_Y + GOL_ALTURA // 2)


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


def desenha_titulo_fase(window, assets, fase_torneio, partida):
    """Mostra QUARTAS / SEMIFINAL / FINAL (ou PRORROGACAO) no topo."""
    if partida.morte_subita:
        titulo_texto = "PRORROGACAO"
        cor = (255, 150, 50)
    else:
        titulos = {
            'quartas': 'QUARTAS DE FINAL',
            'semi': 'SEMIFINAL',
            'final': 'FINAL',
        }
        titulo_texto = titulos.get(fase_torneio, '')
        cor = YELLOW if fase_torneio == 'final' else WHITE
    if not titulo_texto:
        return
    texto = assets['font_pequena'].render(titulo_texto, True, cor)
    texto_rect = texto.get_rect(center=(WIDTH // 2, 28))
    caixa = pygame.Surface(
        (texto.get_width() + 30, texto.get_height() + 6), pygame.SRCALPHA
    )
    caixa.fill((0, 0, 0, 180))
    window.blit(caixa, caixa.get_rect(center=texto_rect.center))
    window.blit(texto, texto_rect)


def desenha_contador(window, assets, partida):
    """Mostra 'COBRANCA X' ou 'DEFESA X' (sem 'de 5' na prorrogacao)."""
    if partida.fase == 'jogador_cobra':
        num = len(partida.resultados_jogador) + 1
        if partida.morte_subita:
            texto_str = f"COBRANCA {num}"
        else:
            texto_str = f"COBRANCA {min(num, 5)} DE 5"
        cor = (255, 255, 255)
    elif partida.fase == 'jogador_defende':
        num = len(partida.resultados_adversario) + 1
        if partida.morte_subita:
            texto_str = f"DEFESA {num}"
        else:
            texto_str = f"DEFESA {min(num, 5)} DE 5"
        cor = (100, 200, 255)
    else:
        return
    texto = assets['font_pequena'].render(texto_str, True, cor)
    texto_rect = texto.get_rect(center=(WIDTH // 2, 60))
    caixa = pygame.Surface(
        (texto.get_width() + 20, texto.get_height() + 4), pygame.SRCALPHA
    )
    caixa.fill((0, 0, 0, 140))
    window.blit(caixa, caixa.get_rect(center=texto_rect.center))
    window.blit(texto, texto_rect)


def desenha_aviso_fase(window, assets, aviso_fase):
    """Mostra aviso grande no centro ao trocar de fase."""
    if not aviso_fase:
        return
    fonte = pygame.font.SysFont(None, 70)
    cor = (255, 150, 50) if aviso_fase == "PRORROGACAO!" else YELLOW
    render = fonte.render(aviso_fase, True, cor)
    rect = render.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    caixa = pygame.Surface(
        (render.get_width() + 40, render.get_height() + 20), pygame.SRCALPHA
    )
    caixa.fill((0, 0, 0, 160))
    window.blit(caixa, caixa.get_rect(center=rect.center))
    window.blit(render, rect)


def desenha_pausa(window, assets):
    """Desenha a tela de pausa por cima de tudo."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    window.blit(overlay, (0, 0))
    fonte = pygame.font.SysFont(None, 90)
    texto = fonte.render("PAUSADO", True, WHITE)
    window.blit(texto, texto.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
    dica = assets['font_pequena'].render(
        "Aperte P para continuar", True, (220, 220, 220)
    )
    window.blit(dica, dica.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))


def desenha_sombras(window, sprites_cobranca, sprites_defesa, partida):
    """Desenha sombras elipticas embaixo da bola e do goleiro."""
    def sombra(cx, cy, largura):
        s = pygame.Surface((largura, largura // 3), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, 80), (0, 0, largura, largura // 3))
        window.blit(s, (cx - largura // 2, cy - (largura // 3) // 2))

    if partida.fase == 'jogador_cobra' and sprites_cobranca:
        mira, bola, goleiro = sprites_cobranca
        if bola.estado in ('parada', 'voando'):
            sombra(bola.rect.centerx, bola.rect.bottom + 6,
                   max(18, bola.rect.width))
        sombra(goleiro.rect.centerx, goleiro.rect.bottom + 2, 62)
    elif partida.fase == 'jogador_defende' and sprites_defesa:
        batedor, bola_cpu, goleiro_j, alvo = sprites_defesa
        sombra(goleiro_j.rect.centerx, goleiro_j.rect.bottom + 2, 62)
        sombra(batedor.rect.centerx, batedor.rect.bottom + 2, 42)


def desenha_linha_mira(window, mira, bola):
    """Linha pontilhada da bola ate a mira."""
    if mira.estado not in ('oscilando_x', 'oscilando_y'):
        return
    bx, by = bola.rect.center
    mx, my = mira.rect.center
    for i in range(15):
        if i % 2 == 0:
            t = i / 15
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
    alpha = int(255 * (progresso / 0.2)) if progresso < 0.2 else 255
    fonte = pygame.font.SysFont(None, fonte_tamanho)
    render = fonte.render(texto, True, cor)
    render.set_alpha(alpha)
    window.blit(render, render.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


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
    """Desenha o campo: arquibancada, gramado listrado e marcacoes."""
    window.fill((30, 60, 30))

    # Arquibancada no topo
    pygame.draw.rect(window, (45, 45, 70), (0, 0, WIDTH, GOL_Y - 10))
    for i in range(0, WIDTH, 14):
        cor_t = [(200, 80, 80), (80, 80, 200), (220, 220, 80),
                 (220, 220, 220)][(i // 14) % 4]
        pygame.draw.circle(window, cor_t, (i + 7, (GOL_Y - 10) // 2), 3)

    # Gramado listrado
    topo_grama = GOL_Y - 10
    altura_faixa = 40
    n_faixas = (HEIGHT - topo_grama) // altura_faixa + 1
    for i in range(n_faixas):
        y = topo_grama + i * altura_faixa
        cor = (38, 120, 38) if i % 2 == 0 else (48, 140, 48)
        pygame.draw.rect(window, cor, (0, y, WIDTH, altura_faixa))

    # Marca do penalti (bolinha branca)
    marca_y = HEIGHT - 150
    pygame.draw.circle(window, WHITE, (WIDTH // 2, marca_y), 6)

    # Meia-lua acima da marca do penalti
    pygame.draw.arc(window, WHITE,
                   (WIDTH // 2 - 80, marca_y - 75, 160, 120),
                   3.5, 5.95, 3)


def desenha_gol(window):
    """Desenha o gol com rede em malha e traves arredondadas."""
    rede = pygame.Surface((GOL_LARGURA, GOL_ALTURA), pygame.SRCALPHA)
    rede.fill((230, 230, 230, 50))
    window.blit(rede, (GOL_X, GOL_Y))

    for x in range(GOL_X, GOL_X + GOL_LARGURA + 1, 18):
        pygame.draw.line(window, (210, 210, 210),
                        (x, GOL_Y), (x, GOL_Y + GOL_ALTURA), 1)
    for y in range(GOL_Y, GOL_Y + GOL_ALTURA + 1, 18):
        pygame.draw.line(window, (210, 210, 210),
                        (GOL_X, y), (GOL_X + GOL_LARGURA, y), 1)

    esp = 9
    pygame.draw.rect(window, (170, 170, 170),
                    (GOL_X - esp + 2, GOL_Y + 2, esp, GOL_ALTURA + esp))
    pygame.draw.rect(window, WHITE,
                    (GOL_X - esp, GOL_Y, esp, GOL_ALTURA + esp),
                    border_radius=4)
    pygame.draw.rect(window, WHITE,
                    (GOL_X + GOL_LARGURA, GOL_Y, esp, GOL_ALTURA + esp),
                    border_radius=4)
    pygame.draw.rect(window, WHITE,
                    (GOL_X - esp, GOL_Y - esp,
                     GOL_LARGURA + esp * 2, esp), border_radius=4)


def desenha_placar(window, assets, partida):
    """Placar: nome dos times, numeros ao vivo e bolinhas das cobrancas."""
    texto_j = assets['font_pequena'].render(partida.time_jogador, True, WHITE)
    texto_a = assets['font_pequena'].render(partida.time_adversario, True, WHITE)
    window.blit(texto_j, (20, 8))
    window.blit(texto_a, (WIDTH - texto_a.get_width() - 20, 8))

    # Placar numerico ao vivo no topo central
    placar_str = f"{partida.gols_jogador()} x {partida.gols_adversario()}"
    placar_txt = assets['font_media'].render(placar_str, True, WHITE)
    caixa = pygame.Surface(
        (placar_txt.get_width() + 24, placar_txt.get_height() + 6),
        pygame.SRCALPHA
    )
    caixa.fill((0, 0, 0, 130))
    cx_rect = caixa.get_rect(center=(WIDTH // 2, 96))
    window.blit(caixa, cx_rect)
    window.blit(placar_txt, placar_txt.get_rect(center=(WIDTH // 2, 96)))

    # Bolinhas (so mostra ate 5, pra nao estourar na prorrogacao)
    raio = 8
    espacamento = 22
    for i in range(5):
        x = 20 + i * espacamento
        y = 40
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
            msg, cor = "Clique para travar a DIRECAO", WHITE
        elif mira.estado == 'oscilando_y':
            msg, cor = "Clique para travar a ALTURA e chutar", YELLOW
        else:
            return
        texto = assets['font_pequena'].render(msg, True, cor)
        window.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 38))
    elif partida.fase == 'jogador_defende' and not chute_cpu:
        msg = "Clique onde a bola vai para defender!"
        texto = assets['font_pequena'].render(msg, True, YELLOW)
        window.blit(texto, (WIDTH // 2 - texto.get_width() // 2, HEIGHT - 38))