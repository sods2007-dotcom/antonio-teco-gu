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

    # ----- Sons (efeitos curtos) -----
    sons_para_carregar = {
        'chute': 'chute.wav',
        'gol': 'gol.mp3',
        'perdeu': 'perdeu.mp3',
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

    # ----- Musica ambiente -----
    # Usamos pygame.mixer.music (otimizado para streaming/loop)
    caminho_musica = None
    for ext in ['ogg', 'wav', 'mp3']:
        c = os.path.join(SND_DIR, f'torcida.{ext}')
        if os.path.exists(c):
            caminho_musica = c
            break

    assets['musica_torcida'] = caminho_musica  # so guarda o caminho

    return assets