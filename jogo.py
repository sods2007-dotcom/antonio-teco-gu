"""
Penalty Shooter - Ponto de entrada do jogo.
"""
import pygame
import random
from config import (
    WIDTH, HEIGHT, MENU, SELECAO, PARTIDA, FIM_PARTIDA, CAMPEAO, QUIT,
    TIMES
)
from menu_screen import menu_screen
from selecao_screen import selecao_screen
from partida_screen import partida_screen
from fim_partida_screen import fim_partida_screen
def sorteia_adversario(time_jogador, ja_enfrentados):
    """Sorteia um adversario diferente do jogador e dos ja enfrentados."""
    candidatos = [
        t for t in TIMES
        if t[0] != time_jogador[0] and t[0] not in ja_enfrentados
    ]
    if not candidatos:
        candidatos = [t for t in TIMES if t[0] != time_jogador[0]]
    return random.choice(candidatos)
# ===== Inicializacao =====
pygame.init()
pygame.mixer.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Penalty Shooter')
# ===== Contexto compartilhado do torneio =====
contexto = {
    'time_jogador': None,
    'time_adversario': None,
    'fase_torneio': 'quartas',
    'ja_enfrentados': [],
    'ultima_partida': None,
}
def resetar_torneio():
    """Reseta o contexto para um novo torneio."""
    contexto['time_jogador'] = None
    contexto['time_adversario'] = None
    contexto['fase_torneio'] = 'quartas'
    contexto['ja_enfrentados'] = []
    contexto['ultima_partida'] = None
# ===== Loop principal de telas =====
state = MENU
while state != QUIT:
    if state == MENU:
        state = menu_screen(window)
        resetar_torneio()
    elif state == SELECAO:
        state, time_escolhido = selecao_screen(window)
        if time_escolhido:
            contexto['time_jogador'] = time_escolhido
            contexto['time_adversario'] = sorteia_adversario(
                time_escolhido, contexto['ja_enfrentados']
            )
    elif state == PARTIDA:
        state, partida_concluida = partida_screen(
            window,
            time_jogador=contexto['time_jogador'][0],
            time_adversario=contexto['time_adversario'][0],
            fase_torneio=contexto['fase_torneio']
        )
        contexto['ultima_partida'] = partida_concluida
        if partida_concluida:
            contexto['ja_enfrentados'].append(contexto['time_adversario'][0])
    elif state == FIM_PARTIDA:
        state = fim_partida_screen(
            window,
            contexto['ultima_partida'],
            contexto['fase_torneio']
        )
        # Se venceu, avanca a fase
        if (contexto['ultima_partida']
                and contexto['ultima_partida'].jogador_venceu()):
            if contexto['fase_torneio'] == 'quartas':
                contexto['fase_torneio'] = 'semi'
            elif contexto['fase_torneio'] == 'semi':
                contexto['fase_torneio'] = 'final'
            # Se vai jogar de novo, sorteia adversario novo
            if state == PARTIDA:
                contexto['time_adversario'] = sorteia_adversario(
                    contexto['time_jogador'],
                    contexto['ja_enfrentados']
                )
    elif state == CAMPEAO:
        # Sera implementado no Commit #18
        from config import WHITE
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 80)
        text = font.render("CAMPEAO!", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        esperando = True
        while esperando:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    state = QUIT
                    esperando = False
                if event.type == pygame.KEYDOWN:
                    esperando = False
                    state = MENU
            window.fill((0, 0, 0))
            window.blit(text, text_rect)
            pygame.display.update()
    else:
        state = QUIT
pygame.quit()