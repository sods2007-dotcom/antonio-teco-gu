"""
Configurações globais do jogo Penalty Shooter.
Este arquivo centraliza todas as constantes para fácil ajuste.
"""
from os import path
# ===== Pastas =====
IMG_DIR = path.join(path.dirname(__file__), 'assets', 'img')
SND_DIR = path.join(path.dirname(__file__), 'assets', 'snd')
FNT_DIR = path.join(path.dirname(__file__), 'assets', 'font')
# ===== Dimensoes da janela =====
WIDTH = 800   # Largura
HEIGHT = 600  # Altura
FPS = 30      # Frames por segundo (igual jogo_v6 do handout)
# ===== Cores (RGB) =====
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 200)
YELLOW = (255, 220, 0)
GRAY = (128, 128, 128)
GREEN_GRAMA = (40, 130, 40)  # Verde do gramado
# ===== Estados do jogo (maquina de estados) =====
MENU = 0
SELECAO = 1
PARTIDA = 2
FIM_PARTIDA = 3
CAMPEAO = 4
QUIT = 5
# ===== Times disponiveis =====
# Cada time: (nome, cor_primaria_RGB, cor_secundaria_RGB)
TIMES = [
    ("Brasil",     (255, 215, 0),    (0, 100, 0)),
    ("Argentina",  (135, 206, 235),  (255, 255, 255)),
    ("Alemanha",   (255, 255, 255),  (0, 0, 0)),
    ("Italia",     (0, 70, 180),     (255, 255, 255)),
    ("Espanha",    (200, 30, 30),    (255, 215, 0)),
    ("Franca",     (0, 50, 150),     (255, 255, 255)),
    ("Portugal",   (200, 30, 30),    (0, 100, 0)),
    ("Inglaterra", (255, 255, 255),  (200, 30, 30)),
]