"""
Carrega todos os assets (imagens, sons, fontes) usados pelo jogo.

Tudo eh carregado uma unica vez no inicio para evitar carregamento
repetido durante o jogo. Os assets sao retornados em um dicionario.
"""
import pygame
import os
from config import IMG_DIR, SND_DIR, FNT_DIR


def load_assets():
    """
    Carrega todos os assets do jogo e retorna um dicionario.

    Sons sao carregados com try/except porque podem nao existir ainda
    nos primeiros commits.
    """
    assets = {}

    # ----- Fontes -----
    assets['font_grande'] = pygame.font.SysFont(None, 80)
    assets['font_media'] = pygame.font.SysFont(None, 50)
    assets['font_pequena'] = pygame.font.SysFont(None, 28)

    # ----- Sons (serao adicionados no Commit #12) -----
    sons_para_carregar = {
        'chute': 'chute.wav',
        'gol': 'gol.wav',
        'perdeu': 'perdeu.wav',
        'trave': 'trave.wav',
    }

    for nome, arquivo in sons_para_carregar.items():
        caminho = os.path.join(SND_DIR, arquivo)
        if os.path.exists(caminho):
            try:
                assets[nome] = pygame.mixer.Sound(caminho)
                assets[nome].set_volume(0.5)
            except pygame.error as e:
                print(f"Aviso: nao foi possivel carregar som {arquivo}: {e}")
                assets[nome] = None
        else:
            assets[nome] = None

    return assets