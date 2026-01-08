import pgzrun
from pgzero.actor import Actor
from pygame import Rect

# ================= CONFIGURAÇÃO INICIAL =================
WIDTH = 800
HEIGHT = 600
TILE_SIZE = 32

# ================= FUNDO =================
background = Actor("fundo")

def draw_background():
    for y in range(0, HEIGHT, background.height):
        for x in range(0, WIDTH, background.width):
            background.topleft = (x, y)
            background.draw()

# ================= MAPA =================
# Reconhecimento de tiles através de símbolos
game_map = [
    "................................",
    "................................",
    "................................",
    "................................",  
    "................................",
    "................................",
    "................................",  
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "...####...........####..........",
    "................................",
    "................................",
    "################################",
    "################################",
]

ROWS = len(game_map)
COLS = len(game_map[0])

def draw_map():
    for r in range(ROWS):
        for c in range(COLS):
            if game_map[r][c] == "#":
                screen.draw.filled_rect(
                    Rect(
                        c * TILE_SIZE,
                        r * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE
                    ),
                    (120, 72, 40)
                )

# ================= DETECÇÃO DE COLISÕES =================
def has_ground_below(x, y, w, h):
    y_bottom = y + h / 2
    c1 = int((x - w / 2) // TILE_SIZE)
    c2 = int((x + w / 2 - 1) // TILE_SIZE)
    r = int(y_bottom // TILE_SIZE)

    for c in (c1, c2):
        if 0 <= r < ROWS and 0 <= c < COLS:
            if game_map[r][c] == "#":
                return True
    return False

def has_wall(x, y, w, h, direction):
    x_side = x + w / 2 if direction > 0 else x - w / 2
    c = int(x_side // TILE_SIZE)
    r1 = int((y - h / 2) // TILE_SIZE)
    r2 = int((y + h / 2 - 1) // TILE_SIZE)

    for r in (r1, r2):
        if 0 <= r < ROWS and 0 <= c < COLS:
            if game_map[r][c] == "#":
                return True
    return False

# ================= CLASSES =================
# Classe de animação base
class AnimatedSprite(Actor):
    def __init__(self, pos, frames):
        super().__init__(frames[0], pos)
        self.frames = frames
        self.index = 0
        self.speed = 0.2
        self.anchor = ("center", "center")

    def animate(self):
        self.index += self.speed
        self.image = self.frames[int(self.index) % len(self.frames)]

# Classe do herói
class Hero(AnimatedSprite):
    def __init__(self):
        super().__init__((100, 100), ["heroi_parado_0", "heroi_parado_1"])
        self.vel = 4
        self.vy = 0
        self.gravity = 0.6
        self.jump_power = -12
        self.on_ground = False
        self.alive = True
        self.w = 26
        self.h = 42

    def hitbox(self):
        return Rect(
            self.x - self.w / 2,
            self.y - self.h / 2,
            self.w,
            self.h
        )

    def update(self):
        if not self.alive:
            return

        moving = False

        if keyboard.left or keyboard.a:
            if self.x > self.w / 2 and not has_wall(self.x - self.vel, self.y, self.w, self.h, -1):
                self.x -= self.vel
            moving = True

        if keyboard.right or keyboard.d:
            if self.x < WIDTH - self.w / 2 and not has_wall(self.x + self.vel, self.y, self.w, self.h, 1):
                self.x += self.vel
            moving = True

        if keyboard.space and self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

        self.vy += self.gravity
        new_y = self.y + self.vy

        if self.vy >= 0 and has_ground_below(self.x, new_y, self.w, self.h):
            row = int((new_y + self.h / 2) // TILE_SIZE)
            self.y = row * TILE_SIZE - self.h / 2
            self.vy = 0
            self.on_ground = True
        else:
            self.y = new_y
            self.on_ground = False

        if moving:
            self.animate()

# Classe inimigo
class Enemy(Actor):
    def __init__(self, pos):
        super().__init__("inimigo_0", pos)
        self.anchor = ("center", "center")
        self.vel = 2
        self.direction = -1
        self.w = 26
        self.h = 26

    def hitbox(self):
        return Rect(
            self.x - self.w / 2,
            self.y - self.h / 2,
            self.w,
            self.h
        )

    def update(self):
        new_x = self.x + self.vel * self.direction
        if has_wall(new_x, self.y, self.w, self.h, self.direction) or not has_ground_below(new_x, self.y + 1, self.w, self.h):
            self.direction *= -1
        else:
            self.x = new_x

# Classe moeda
class Coin(Actor):
    def __init__(self, pos):
        super().__init__("moeda_0", pos)
        self.anchor = ("center", "center")
        self.collected = False
        self.w = 20
        self.h = 20

    def hitbox(self):
        return Rect(
            self.x - self.w / 2,
            self.y - self.h / 2,
            self.w,
            self.h
        )

# ================= ESTADOS DO JOGO =================
STATE = "menu"  # menu, playing, victory, defeat
music_on = True

# ================= MENU =================
def draw_menu():
    screen.fill((0, 0, 0))
    screen.draw.text("Capture as bandeiras", center=(400, 150), fontsize=60, color="white")
    
    # Botões
    start_btn = Rect(300, 250, 200, 50)
    music_btn = Rect(300, 320, 200, 50)
    exit_btn = Rect(300, 390, 200, 50)
    
    screen.draw.filled_rect(start_btn, (50, 50, 200))
    screen.draw.text("START GAME", center=start_btn.center, fontsize=30, color="white")
    
    screen.draw.filled_rect(music_btn, (50, 200, 50))
    music_text = "MUSIC: ON" if music_on else "MUSIC: OFF"
    screen.draw.text(music_text, center=music_btn.center, fontsize=30, color="white")
    
    screen.draw.filled_rect(exit_btn, (200, 50, 50))
    screen.draw.text("EXIT", center=exit_btn.center, fontsize=30, color="white")
    
    return start_btn, music_btn, exit_btn

# ================= REINICIAR JOGO =================
def restart_game():
    global hero, enemies, coins, STATE
    hero = Hero()
    enemies = [
        Enemy((300, 530)),
        Enemy((500, 530)),
        Enemy((650, 530)),
    ]
    coins = [
        Coin((250, 530)), #2
        Coin((450, 420)), #3
        Coin((650, 440)), #4
        Coin((100, 530)),  #1
        Coin((150, 400)),
        Coin((400, 420)),
        Coin((600, 530)),
        Coin((550, 500))
    ]
    if music_on:
        music.play("musica_fundo")
        music.set_volume(0.5)
    STATE = "playing"

# ================= UPDATE =================
def update():
    global STATE, music_on
    
    if STATE == "playing":
        hero.update()
        for e in enemies:
            e.update()
            if hero.hitbox().colliderect(e.hitbox()):
                STATE = "derrota"
                hero.alive = False
        for c in coins:
            if not c.collected and hero.hitbox().colliderect(c.hitbox()):
                c.collected = True
        if all(c.collected for c in coins):
            STATE = "vitoria"

# ================= DRAW =================
def draw():
    global STATE
    if STATE == "menu":
        draw_menu()
        return
    
    draw_background()
    draw_map()
    
    if hero.alive:
        hero.draw()
    
    for e in enemies:
        e.draw()
    
    for c in coins:
        if not c.collected:
            c.draw()
    
    if STATE in ("vitoria", "derrota"):
        screen.draw.filled_rect(Rect(200, 180, 400, 200), (0, 0, 0))
        text = "Voce ganhou!" if STATE == "vitoria" else "Derrota"
        screen.draw.text(text, center=(400, 240), fontsize=50, color="white")
        screen.draw.text("Jogar novamente", center=(400, 310), fontsize=30, color="yellow")

# ================= MOUSE CLICK =================
def on_mouse_down(pos):
    global STATE, music_on
    if STATE == "menu":
        start_btn, music_btn, exit_btn = draw_menu()
        if start_btn.collidepoint(pos):
            restart_game()
        elif music_btn.collidepoint(pos):
            music_on = not music_on
            if music_on:
                music.play("musica_fundo")
            else:
                music.stop()
        elif exit_btn.collidepoint(pos):
            exit()
    elif STATE in ("vitoria", "derrota"):
        btn = Rect(250, 280, 300, 60)
        if btn.collidepoint(pos):
            restart_game()

pgzrun.go()
