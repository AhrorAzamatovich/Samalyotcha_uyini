import pygame
import random
import sys
import os
import json
import math

# ─────────────────────────────────────────────
#  PYGAME INIT
# ─────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ─────────────────────────────────────────────
#  KONSTANTALAR
# ─────────────────────────────────────────────
SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 700
FPS           = 60

# Ranglar
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0  )
RED          = (220, 40,  40 )
DARK_RED     = (150, 20,  20 )
GREEN        = (40,  200, 80 )
DARK_GREEN   = (20,  130, 50 )
BLUE         = (40,  120, 220)
DARK_BLUE    = (20,  60,  160)
YELLOW       = (255, 220, 0  )
ORANGE       = (255, 140, 0  )
CYAN         = (0,   220, 220)
PURPLE       = (160, 40,  200)
GRAY         = (100, 100, 100)
LIGHT_GRAY   = (180, 180, 180)
DARK_GRAY    = (40,  40,  40 )
ROAD_COLOR   = (50,  50,  60 )
ROAD_LINE    = (220, 200, 50 )
BG_TOP       = (10,  10,  30 )
BG_BOT       = (20,  20,  60 )

# O'yin holatlari
STATE_MENU        = "menu"
STATE_DIFFICULTY  = "difficulty"
STATE_PLAYING     = "playing"
STATE_PAUSED      = "paused"
STATE_GAMEOVER    = "gameover"
STATE_LEADERBOARD = "leaderboard"
STATE_SETTINGS    = "settings"

# Power-up turlari
PU_SHIELD = "shield"
PU_DOUBLE = "double_shot"
PU_SLOW   = "slow_enemies"
PU_LIFE   = "extra_life"

HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscores.json")

# ─────────────────────────────────────────────
#  YORDAMCHI FUNKSIYALAR
# ─────────────────────────────────────────────
def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"Easy": 0, "Medium": 0, "Hard": 0}

def save_highscores(hs):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(hs, f)
    except Exception:
        pass

def draw_gradient_rect(surface, color1, color2, rect):
    """Vertikal gradient to'rtburchak chizadi."""
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    for i in range(rect.height):
        t   = i / max(rect.height - 1, 1)
        col = (int(r1 + (r2-r1)*t), int(g1 + (g2-g1)*t), int(b1 + (b2-b1)*t))
        pygame.draw.line(surface, col, (rect.left, rect.top+i), (rect.right, rect.top+i))

def draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)

def pulse(t, speed=3, mn=0.7, mx=1.0):
    """0-1 araliqdagi pulsatsiyalanuvchi qiymat."""
    return mn + (mx - mn) * (0.5 + 0.5 * math.sin(t * speed))

# ─────────────────────────────────────────────
#  OVOZ GENERATORI (faylsiz)
# ─────────────────────────────────────────────
def make_sound(freq, duration_ms, volume=0.3, wave="square", decay=True):
    """Oddiy sintetik ovoz yaratadi."""
    sample_rate = 44100
    n_samples   = int(sample_rate * duration_ms / 1000)
    buf         = bytearray(n_samples * 2)
    for i in range(n_samples):
        t   = i / sample_rate
        f   = freq * (0.5 ** (t / (duration_ms/1000))) if decay else freq
        val = math.sin(2 * math.pi * f * t)
        if wave == "square":
            val = 1.0 if val >= 0 else -1.0
        env = max(0.0, 1.0 - i / n_samples) if decay else 1.0
        s   = int(val * env * volume * 32767)
        s   = max(-32768, min(32767, s))
        buf[i*2]   = s & 0xFF
        buf[i*2+1] = (s >> 8) & 0xFF
    sound = pygame.sndarray.make_sound(
        pygame.sndarray.array(
            pygame.sndarray.make_sound(bytes(buf)).get_raw()
        ).reshape((-1, 1)).repeat(2, axis=1)
    )
    return sound

def make_shoot_sound():
    sr   = 44100
    dur  = 120
    n    = int(sr * dur / 1000)
    buf  = bytearray(n * 2 * 2)
    for i in range(n):
        t   = i / sr
        f   = 800 * (0.3 ** t)
        val = math.sin(2 * math.pi * f * t)
        env = max(0.0, 1.0 - i / n)
        s   = int(val * env * 0.4 * 32767)
        s   = max(-32768, min(32767, s))
        buf[i*4]   = s & 0xFF
        buf[i*4+1] = (s >> 8) & 0xFF
        buf[i*4+2] = s & 0xFF
        buf[i*4+3] = (s >> 8) & 0xFF
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(pygame.mixer.Sound(buffer=bytes(buf)).get_raw()).reshape((-1, 2))
    )

def make_explosion_sound():
    sr  = 44100
    dur = 400
    n   = int(sr * dur / 1000)
    buf = bytearray(n * 4)
    for i in range(n):
        noise = random.randint(-32768, 32767)
        env   = max(0.0, 1.0 - i / n) ** 2
        s     = int(noise * env * 0.6)
        s     = max(-32768, min(32767, s))
        buf[i*4]   = s & 0xFF
        buf[i*4+1] = (s >> 8) & 0xFF
        buf[i*4+2] = s & 0xFF
        buf[i*4+3] = (s >> 8) & 0xFF
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(pygame.mixer.Sound(buffer=bytes(buf)).get_raw()).reshape((-1, 2))
    )

def make_powerup_sound():
    sr  = 44100
    dur = 300
    n   = int(sr * dur / 1000)
    buf = bytearray(n * 4)
    for i in range(n):
        t   = i / sr
        f   = 400 + 800 * (i / n)
        val = math.sin(2 * math.pi * f * t)
        env = max(0.0, 1.0 - i / n)
        s   = int(val * env * 0.5 * 32767)
        s   = max(-32768, min(32767, s))
        buf[i*4]   = s & 0xFF
        buf[i*4+1] = (s >> 8) & 0xFF
        buf[i*4+2] = s & 0xFF
        buf[i*4+3] = (s >> 8) & 0xFF
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(pygame.mixer.Sound(buffer=bytes(buf)).get_raw()).reshape((-1, 2))
    )

def make_hit_sound():
    sr  = 44100
    dur = 200
    n   = int(sr * dur / 1000)
    buf = bytearray(n * 4)
    for i in range(n):
        t   = i / sr
        f   = 200
        val = math.sin(2 * math.pi * f * t)
        env = max(0.0, 1.0 - i / n)
        s   = int(val * env * 0.7 * 32767)
        s   = max(-32768, min(32767, s))
        buf[i*4]   = s & 0xFF
        buf[i*4+1] = (s >> 8) & 0xFF
        buf[i*4+2] = s & 0xFF
        buf[i*4+3] = (s >> 8) & 0xFF
    return pygame.sndarray.make_sound(
        pygame.sndarray.array(pygame.mixer.Sound(buffer=bytes(buf)).get_raw()).reshape((-1, 2))
    )

# ─────────────────────────────────────────────
#  GRAFIK YARATUVCHILAR (faylsiz)
# ─────────────────────────────────────────────
def make_player_surface(w=50, h=70):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    # Gövde
    body = pygame.Rect(w//2-12, 8, 24, h-16)
    draw_gradient_rect(surf, (60,160,255), (10,80,180), body)
    pygame.draw.rect(surf, (100,200,255), body, 2, border_radius=4)
    # Qanotlar
    wing_pts_l = [(0, h-30), (w//2-12, h-50), (w//2-12, h-20)]
    wing_pts_r = [(w, h-30), (w//2+12, h-50), (w//2+12, h-20)]
    pygame.draw.polygon(surf, (30,120,220), wing_pts_l)
    pygame.draw.polygon(surf, (30,120,220), wing_pts_r)
    pygame.draw.polygon(surf, (80,180,255), wing_pts_l, 2)
    pygame.draw.polygon(surf, (80,180,255), wing_pts_r, 2)
    # Kokpit
    cockpit = pygame.Rect(w//2-7, 12, 14, 20)
    draw_gradient_rect(surf, (180,240,255), (80,160,220), cockpit)
    pygame.draw.rect(surf, (220,255,255), cockpit, 1, border_radius=4)
    # Dvigatel alov
    for dx in [-6, 6]:
        pts = [(w//2+dx, h-5), (w//2+dx-4, h+10), (w//2+dx+4, h+10)]
        pygame.draw.polygon(surf, ORANGE, pts)
        pts2 = [(w//2+dx, h-2), (w//2+dx-2, h+6), (w//2+dx+2, h+6)]
        pygame.draw.polygon(surf, YELLOW, pts2)
    return surf

def make_enemy_surface(w=48, h=68, color_top=(220,60,60), color_bot=(140,20,20)):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    body = pygame.Rect(w//2-11, 6, 22, h-12)
    draw_gradient_rect(surf, color_top, color_bot, body)
    pygame.draw.rect(surf, (255,120,120), body, 2, border_radius=4)
    # Qanotlar
    wing_pts_l = [(0, 20), (w//2-11, 35), (w//2-11, 10)]
    wing_pts_r = [(w, 20), (w//2+11, 35), (w//2+11, 10)]
    pygame.draw.polygon(surf, (180,30,30), wing_pts_l)
    pygame.draw.polygon(surf, (180,30,30), wing_pts_r)
    pygame.draw.polygon(surf, (255,100,100), wing_pts_l, 2)
    pygame.draw.polygon(surf, (255,100,100), wing_pts_r, 2)
    # Cockpit
    cockpit = pygame.Rect(w//2-6, 10, 12, 16)
    draw_gradient_rect(surf, (255,200,200), (200,80,80), cockpit)
    pygame.draw.rect(surf, (255,220,220), cockpit, 1, border_radius=3)
    return surf

def make_bullet_surface(w=8, h=20):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_gradient_rect(surf, YELLOW, ORANGE, pygame.Rect(0,0,w,h))
    pygame.draw.rect(surf, WHITE, pygame.Rect(w//2-1,0,2,h//3))
    return surf

def make_enemy_bullet_surface(w=8, h=20):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    draw_gradient_rect(surf, (255,80,80), (180,20,20), pygame.Rect(0,0,w,h))
    return surf

def make_powerup_surface(kind, size=36):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy, r = size//2, size//2, size//2-2
    if kind == PU_SHIELD:
        pygame.draw.circle(surf, (0,180,255,200), (cx,cy), r)
        pygame.draw.circle(surf, (100,220,255), (cx,cy), r, 3)
        font = pygame.font.SysFont(None, 22)
        t = font.render("🛡", True, WHITE)
        surf.blit(t, t.get_rect(center=(cx,cy)))
    elif kind == PU_DOUBLE:
        pygame.draw.circle(surf, (255,200,0,200), (cx,cy), r)
        pygame.draw.circle(surf, YELLOW, (cx,cy), r, 3)
        font = pygame.font.SysFont(None, 22)
        t = font.render("✦✦", True, BLACK)
        surf.blit(t, t.get_rect(center=(cx,cy)))
    elif kind == PU_SLOW:
        pygame.draw.circle(surf, (0,220,120,200), (cx,cy), r)
        pygame.draw.circle(surf, GREEN, (cx,cy), r, 3)
        font = pygame.font.SysFont(None, 22)
        t = font.render("❄", True, WHITE)
        surf.blit(t, t.get_rect(center=(cx,cy)))
    elif kind == PU_LIFE:
        pygame.draw.circle(surf, (255,60,100,200), (cx,cy), r)
        pygame.draw.circle(surf, RED, (cx,cy), r, 3)
        font = pygame.font.SysFont(None, 22)
        t = font.render("♥", True, WHITE)
        surf.blit(t, t.get_rect(center=(cx,cy)))
    return surf

# ─────────────────────────────────────────────
#  PORTLASH ZARRACHALARI
# ─────────────────────────────────────────────
class Particle:
    def __init__(self, x, y):
        angle  = random.uniform(0, 2*math.pi)
        speed  = random.uniform(2, 8)
        self.x = x
        self.y = y
        self.vx     = math.cos(angle) * speed
        self.vy     = math.sin(angle) * speed
        self.life   = random.randint(20, 50)
        self.max_life = self.life
        r = random.choice([ORANGE, YELLOW, RED, WHITE, (255,180,50)])
        self.color  = r
        self.radius = random.randint(2, 6)

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surface):
        alpha  = int(255 * self.life / self.max_life)
        radius = max(1, int(self.radius * self.life / self.max_life))
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (radius, radius), radius)
        surface.blit(s, (int(self.x)-radius, int(self.y)-radius))

# ─────────────────────────────────────────────
#  YULDUZLAR FONI
# ─────────────────────────────────────────────
class Star:
    def __init__(self):
        self.reset(spawn=True)

    def reset(self, spawn=False):
        self.x    = random.randint(0, SCREEN_WIDTH)
        self.y    = random.randint(0, SCREEN_HEIGHT) if spawn else -5
        self.speed= random.uniform(0.5, 3.0)
        self.r    = random.randint(1, 3)
        self.brightness = random.randint(150, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT + 5:
            self.reset()

    def draw(self, surface):
        c = (self.brightness,)*3
        pygame.draw.circle(surface, c, (int(self.x), int(self.y)), self.r)

# ─────────────────────────────────────────────
#  RAQIB SAMALYOT SINFI
# ─────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y, speed, shoot=False, hp=1, zigzag=False):
        self.rect     = pygame.Rect(x, y, 48, 68)
        self.speed    = speed
        self.hp       = hp
        self.max_hp   = hp
        self.shoot    = shoot
        self.zigzag   = zigzag
        self.angle    = random.uniform(0, math.pi*2)
        self.shoot_timer = random.randint(60, 120)
        colors = [
            ((220,60,60),(140,20,20)),
            ((200,80,40),(120,30,10)),
            ((180,60,200),(100,20,140)),
        ]
        ct, cb = random.choice(colors)
        self.surface  = make_enemy_surface(48, 68, ct, cb)
        self.flash    = 0

    def update(self, enemy_bullets):
        if self.zigzag:
            self.angle += 0.07
            self.rect.x += int(math.sin(self.angle) * 2.5)
        self.rect.y += int(self.speed)
        self.rect.x  = max(0, min(SCREEN_WIDTH - self.rect.width, self.rect.x))
        if self.shoot:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot_timer = random.randint(80, 160)
                bx = self.rect.centerx - 4
                by = self.rect.bottom
                enemy_bullets.append(pygame.Rect(bx, by, 8, 20))
        if self.flash > 0:
            self.flash -= 1

    def draw(self, surface):
        if self.flash > 0:
            flash_surf = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, 160))
            surface.blit(self.surface, self.rect.topleft)
            surface.blit(flash_surf, self.rect.topleft)
        else:
            surface.blit(self.surface, self.rect.topleft)
        # HP bar
        if self.hp < self.max_hp:
            bw = self.rect.width
            bh = 5
            bx = self.rect.x
            by = self.rect.y - 8
            pygame.draw.rect(surface, DARK_RED, (bx, by, bw, bh), border_radius=2)
            ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, GREEN, (bx, by, int(bw*ratio), bh), border_radius=2)

# ─────────────────────────────────────────────
#  POWER-UP SINFI
# ─────────────────────────────────────────────
class PowerUp:
    def __init__(self, x, y, kind):
        self.kind    = kind
        self.rect    = pygame.Rect(x, y, 36, 36)
        self.surface = make_powerup_surface(kind)
        self.angle   = 0
        self.speed   = 2

    def update(self):
        self.rect.y += self.speed
        self.angle  += 2

    def draw(self, surface, t):
        r    = self.rect
        sc   = 0.85 + 0.15 * math.sin(t * 0.05)
        size = int(36 * sc)
        scaled = pygame.transform.scale(self.surface, (size, size))
        cx  = r.centerx - size//2
        cy  = r.centery - size//2
        # Glow
        for gr in range(20, 4, -4):
            glow = pygame.Surface((size+gr*2, size+gr*2), pygame.SRCALPHA)
            alpha = 30
            if self.kind == PU_SHIELD:  gcol = (0,180,255,alpha)
            elif self.kind == PU_DOUBLE: gcol = (255,200,0,alpha)
            elif self.kind == PU_SLOW:   gcol = (0,220,120,alpha)
            else:                        gcol = (255,60,100,alpha)
            pygame.draw.circle(glow, gcol, (size//2+gr, size//2+gr), size//2+gr)
            surface.blit(glow, (cx-gr, cy-gr))
        surface.blit(scaled, (cx, cy))

# ─────────────────────────────────────────────
#  TUGMA SINFI
# ─────────────────────────────────────────────
class Button:
    def __init__(self, text, rect, color=BLUE, hover_color=None,
                 text_color=WHITE, font_size=32, radius=14):
        self.text        = text
        self.rect        = pygame.Rect(rect)
        self.color       = color
        self.hover_color = hover_color or tuple(min(255,c+40) for c in color)
        self.text_color  = text_color
        self.font        = pygame.font.SysFont("Arial", font_size, bold=True)
        self.radius      = radius
        self.hovered     = False
        self.scale       = 1.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target = 1.05 if self.hovered else 1.0
        self.scale += (target - self.scale) * 0.15

    def draw(self, surface):
        col  = self.hover_color if self.hovered else self.color
        sc   = self.scale
        w    = int(self.rect.width * sc)
        h    = int(self.rect.height * sc)
        rx   = self.rect.centerx - w//2
        ry   = self.rect.centery - h//2
        r    = pygame.Rect(rx, ry, w, h)
        # Gölge
        shadow_r = pygame.Rect(rx+4, ry+4, w, h)
        draw_rounded_rect(surface, (0,0,0,120), shadow_r, self.radius)
        draw_rounded_rect(surface, col, r, self.radius)
        draw_rounded_rect(surface, WHITE, r, self.radius, 2, WHITE)
        txt  = self.font.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=r.center))

# ─────────────────────────────────────────────
#  ASOSIY O'YIN KLASSI
# ─────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen  = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("✈  Samalyotcha O'yini  |  by Ahrorazamatovich")
        self.clock   = pygame.time.Clock()
        self.state   = STATE_MENU
        self.difficulty = "Medium"
        self.highscores = load_highscores()
        self.stars   = [Star() for _ in range(120)]
        self.particles = []
        self.t       = 0
        self.sound_enabled = True

        # Fontlar
        self.font_huge   = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_big    = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_med    = pygame.font.SysFont("Arial", 32)
        self.font_small  = pygame.font.SysFont("Arial", 24)
        self.font_tiny   = pygame.font.SysFont("Arial", 18)

        # Rasmlar
        try:
            self.player_img = pygame.transform.scale(
                pygame.image.load(os.path.join(os.path.dirname(__file__), "1.png")), (50, 70))
            self.enemy_img  = pygame.transform.scale(
                pygame.image.load(os.path.join(os.path.dirname(__file__), "3.png")), (48, 68))
            self.use_images = True
        except Exception:
            self.player_img = make_player_surface()
            self.enemy_img  = make_enemy_surface()
            self.use_images = False

        self.bullet_surf       = make_bullet_surface()
        self.enemy_bullet_surf = make_enemy_bullet_surface()

        # Ovozlar
        try:
            self.snd_shoot     = make_shoot_sound()
            self.snd_explode   = make_explosion_sound()
            self.snd_powerup   = make_powerup_sound()
            self.snd_hit       = make_hit_sound()
            self.snd_shoot.set_volume(0.4)
            self.snd_explode.set_volume(0.5)
            self.snd_powerup.set_volume(0.6)
            self.snd_hit.set_volume(0.6)
        except Exception:
            self.snd_shoot = self.snd_explode = self.snd_powerup = self.snd_hit = None

        self._build_menus()
        self._reset_game()

    # ─── MENYU TUGMALARI ─────────────────────
    def _build_menus(self):
        cx = SCREEN_WIDTH // 2
        self.menu_buttons = [
            Button("O'YINNI BOSHLASH",  (cx-180, 300, 360, 55), color=(30,130,220)),
            Button("QIYINLIK",          (cx-180, 370, 360, 55), color=(140,40,200)),
            Button("REKORDLAR",         (cx-180, 440, 360, 55), color=(200,130,0)),
            Button("SOZLAMALAR",        (cx-180, 510, 360, 55), color=(50,150,80)),
            Button("CHIQISH",           (cx-180, 580, 360, 55), color=(180,30,30)),
        ]
        self.diff_buttons = [
            Button("OSON",   (cx-180, 320, 360, 60), color=(40,180,80)),
            Button("O'RTA",  (cx-180, 400, 360, 60), color=(200,140,0)),
            Button("QIYIN",  (cx-180, 480, 360, 60), color=(200,40,40)),
            Button("← ORQAGA", (cx-180, 570, 360, 50), color=GRAY, font_size=26),
        ]
        self.gameover_buttons = [
            Button("QAYTA BOSHLASH", (cx-180, 480, 360, 55), color=(30,130,220)),
            Button("BOSH MENYU",     (cx-180, 550, 360, 55), color=GRAY),
        ]
        self.pause_buttons = [
            Button("DAVOM ETISH",  (cx-160, 330, 320, 55), color=(40,180,80)),
            Button("BOSH MENYU",   (cx-160, 400, 320, 55), color=GRAY),
        ]
        self.settings_buttons = [
            Button("OVOZ: YOQ'",   (cx-200, 340, 400, 55), color=(50,150,200)),
            Button("← ORQAGA",     (cx-200, 430, 400, 55), color=GRAY, font_size=26),
        ]
        self.lb_buttons = [
            Button("← ORQAGA", (cx-160, 570, 320, 50), color=GRAY, font_size=26),
        ]

    def _update_settings_button(self):
        if self.sound_enabled:
            label = "OVOZ: YOQILGAN"
        else:
            label = "OVOZ: OCHIRILGAN"
        self.settings_buttons[0].text = label

    # ─── O'YIN BOSHLASH ──────────────────────
    def _reset_game(self):
        DIFF = {
            "Easy":   dict(car_speed=3,  shoot=False, zigzag=False, hp=1, spawn_rate=28, enemy_shoot=False),
            "Medium": dict(car_speed=5,  shoot=True,  zigzag=False, hp=1, spawn_rate=22, enemy_shoot=True),
            "Hard":   dict(car_speed=8,  shoot=True,  zigzag=True,  hp=2, spawn_rate=14, enemy_shoot=True),
        }
        cfg = DIFF.get(self.difficulty, DIFF["Medium"])
        self.cfg       = cfg
        self.score     = 0
        self.lives     = 3
        self.invincible= 0          # invincible frames after hit
        self.enemies   = []
        self.bullets   = []
        self.enemy_bullets = []
        self.powerups  = []
        self.player_x  = SCREEN_WIDTH // 2 - 25
        self.player_y  = SCREEN_HEIGHT - 110
        self.player_speed = 6
        self.last_shot = 0
        self.shot_cd   = 180          # ms
        self.base_enemy_speed = cfg["car_speed"]
        self.enemy_speed = float(self.base_enemy_speed)
        self.spawn_timer = 0
        self.spawn_rate  = cfg["spawn_rate"]

        # Power-up holati
        self.shield_timer = 0
        self.double_timer = 0
        self.slow_timer   = 0

        # UI flash
        self.score_flash  = 0
        self.msg          = ""
        self.msg_timer    = 0

        # Road scroll
        self.road_y       = 0

        # Animatsiya
        self.player_tilt  = 0

    def _play_sound(self, snd):
        if self.sound_enabled and snd:
            try:
                snd.play()
            except Exception:
                pass

    # ─── ASOSIY HALQA ────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.t += 1
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    save_highscores(self.highscores)
                    pygame.quit()
                    sys.exit()

            # Yulduzlarni yangilash (hamma joyda)
            for s in self.stars:
                s.update()

            if   self.state == STATE_MENU:        self._menu(events)
            elif self.state == STATE_DIFFICULTY:  self._difficulty_screen(events)
            elif self.state == STATE_PLAYING:     self._playing(events)
            elif self.state == STATE_PAUSED:      self._paused(events)
            elif self.state == STATE_GAMEOVER:    self._gameover(events)
            elif self.state == STATE_LEADERBOARD: self._leaderboard(events)
            elif self.state == STATE_SETTINGS:    self._settings(events)

            pygame.display.flip()

    # ─── FON ─────────────────────────────────
    def _draw_background(self):
        draw_gradient_rect(self.screen, BG_TOP, BG_BOT,
                           pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        for s in self.stars:
            s.draw(self.screen)

    def _draw_road(self):
        rw = 520
        rx = (SCREEN_WIDTH - rw) // 2
        road_rect = pygame.Rect(rx, 0, rw, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, ROAD_COLOR, road_rect)
        # Chetlar
        pygame.draw.rect(self.screen, (80,80,90), (rx, 0, 6, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (80,80,90), (rx+rw-6, 0, 6, SCREEN_HEIGHT))
        # Yo'l chiziqlari (harakatlanuvchi)
        line_h, gap = 50, 30
        total = line_h + gap
        offset = int(self.road_y) % total
        for yy in range(-total + offset, SCREEN_HEIGHT + total, total):
            for lane in [rx + rw//4, rx + rw//2, rx + 3*rw//4]:
                pygame.draw.rect(self.screen, ROAD_LINE, (lane-2, yy, 4, line_h))

    # ─── MENYU ───────────────────────────────
    def _menu(self, events):
        mouse = pygame.mouse.get_pos()
        self._draw_background()

        # Logo
        title1 = self.font_huge.render("✈ SAMALYOTCHA", True, YELLOW)
        title2 = self.font_big.render("O'YINI", True, CYAN)
        sub    = self.font_small.render("by Ahrorazamatovich", True, LIGHT_GRAY)
        sc     = pulse(self.t, 2, 0.95, 1.05)
        scaled = pygame.transform.scale(title1, (int(title1.get_width()*sc), int(title1.get_height()*sc)))
        cx     = SCREEN_WIDTH // 2
        self.screen.blit(scaled, scaled.get_rect(center=(cx, 130)))
        self.screen.blit(title2, title2.get_rect(center=(cx, 210)))
        self.screen.blit(sub,    sub.get_rect(center=(cx, 258)))

        # Qiyinlik ko'rsatgichi
        diff_col = {
            "Easy": GREEN, "Medium": YELLOW, "Hard": RED
        }.get(self.difficulty, WHITE)
        diff_txt = self.font_small.render(f"Qiyinlik: {self.difficulty}", True, diff_col)
        self.screen.blit(diff_txt, diff_txt.get_rect(center=(cx, 283)))

        # Rekord
        hs    = self.highscores.get(self.difficulty, 0)
        hs_t  = self.font_small.render(f"🏆 Rekord: {hs}", True, YELLOW)
        self.screen.blit(hs_t, hs_t.get_rect(center=(cx, 306)))

        for btn in self.menu_buttons:
            btn.update(mouse)
            btn.draw(self.screen)

        for e in events:
            if self.menu_buttons[0].handle_event(e):
                self._reset_game(); self.state = STATE_PLAYING
            elif self.menu_buttons[1].handle_event(e):
                self.state = STATE_DIFFICULTY
            elif self.menu_buttons[2].handle_event(e):
                self.state = STATE_LEADERBOARD
            elif self.menu_buttons[3].handle_event(e):
                self.state = STATE_SETTINGS
            elif self.menu_buttons[4].handle_event(e):
                save_highscores(self.highscores)
                pygame.quit(); sys.exit()

    # ─── QIYINLIK ────────────────────────────
    def _difficulty_screen(self, events):
        mouse = pygame.mouse.get_pos()
        self._draw_background()
        cx  = SCREEN_WIDTH // 2
        ttl = self.font_big.render("QIYINLIK TANLANG", True, WHITE)
        self.screen.blit(ttl, ttl.get_rect(center=(cx, 220)))

        descs = [
            ("OSON",  "Sekin, o'q yo'q, oddiy dushmanlar",  GREEN),
            ("O'RTA", "O'rtacha tezlik, dushman o'q otadi", YELLOW),
            ("QIYIN", "Tez, zigzag, ko'p HP, ko'p o'q",     RED),
        ]
        for i, (_, desc, col) in enumerate(descs):
            y   = 360 + i * 80 - 5
            txt = self.font_tiny.render(desc, True, col)
            self.screen.blit(txt, txt.get_rect(center=(cx, y)))

        for btn in self.diff_buttons:
            btn.update(mouse)
            btn.draw(self.screen)

        for e in events:
            if self.diff_buttons[0].handle_event(e):
                self.difficulty = "Easy";   self.state = STATE_MENU
            elif self.diff_buttons[1].handle_event(e):
                self.difficulty = "Medium"; self.state = STATE_MENU
            elif self.diff_buttons[2].handle_event(e):
                self.difficulty = "Hard";   self.state = STATE_MENU
            elif self.diff_buttons[3].handle_event(e):
                self.state = STATE_MENU

    # ─── SOZLAMALAR ──────────────────────────
    def _settings(self, events):
        mouse = pygame.mouse.get_pos()
        self._draw_background()
        cx  = SCREEN_WIDTH // 2
        ttl = self.font_big.render("SOZLAMALAR", True, WHITE)
        self.screen.blit(ttl, ttl.get_rect(center=(cx, 220)))

        self._update_settings_button()
        for btn in self.settings_buttons:
            btn.update(mouse)
            btn.draw(self.screen)

        for e in events:
            if self.settings_buttons[0].handle_event(e):
                self.sound_enabled = not self.sound_enabled
            elif self.settings_buttons[1].handle_event(e):
                self.state = STATE_MENU

    # ─── REKORDLAR ───────────────────────────
    def _leaderboard(self, events):
        mouse = pygame.mouse.get_pos()
        self._draw_background()
        cx  = SCREEN_WIDTH // 2
        ttl = self.font_big.render("🏆  REKORDLAR", True, YELLOW)
        self.screen.blit(ttl, ttl.get_rect(center=(cx, 200)))

        rows = [
            ("Oson",   self.highscores.get("Easy",   0), GREEN),
            ("O'rta",  self.highscores.get("Medium", 0), YELLOW),
            ("Qiyin",  self.highscores.get("Hard",   0), RED),
        ]
        for i, (label, val, col) in enumerate(rows):
            bg_r = pygame.Rect(cx-200, 290+i*90, 400, 70)
            draw_rounded_rect(self.screen, (30,30,60), bg_r, 12)
            draw_rounded_rect(self.screen, col, bg_r, 12, 2, col)
            lt   = self.font_med.render(label, True, WHITE)
            vt   = self.font_big.render(str(val), True, col)
            self.screen.blit(lt, (bg_r.x+20, bg_r.y+18))
            self.screen.blit(vt, (bg_r.right-vt.get_width()-20, bg_r.y+12))

        for btn in self.lb_buttons:
            btn.update(mouse)
            btn.draw(self.screen)

        for e in events:
            if self.lb_buttons[0].handle_event(e):
                self.state = STATE_MENU

    # ─── PAUZA ───────────────────────────────
    def _paused(self, events):
        mouse = pygame.mouse.get_pos()
        # Xira fon
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        cx  = SCREEN_WIDTH // 2
        ttl = self.font_big.render("⏸  PAUZA", True, WHITE)
        self.screen.blit(ttl, ttl.get_rect(center=(cx, 260)))

        for btn in self.pause_buttons:
            btn.update(mouse)
            btn.draw(self.screen)

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = STATE_PLAYING
            elif self.pause_buttons[0].handle_event(e):
                self.state = STATE_PLAYING
            elif self.pause_buttons[1].handle_event(e):
                self.state = STATE_MENU

    # ─── GAMEOVER ────────────────────────────
    def _gameover(self, events):
        mouse = pygame.mouse.get_pos()
        self._draw_background()
        cx  = SCREEN_WIDTH // 2

        # Zarrachalar hali ham ko'rinadi
        self._update_particles()
        self._draw_particles()

        panel = pygame.Rect(cx-260, 200, 520, 350)
        draw_rounded_rect(self.screen, (20,20,50), panel, 20)
        draw_rounded_rect(self.screen, RED, panel, 20, 3, RED)

        ttl  = self.font_big.render("💥  GAME OVER", True, RED)
        self.screen.blit(ttl, ttl.get_rect(center=(cx, 240)))

        sc_t = self.font_med.render(f"Ochkolar: {self.score}", True, WHITE)
        self.screen.blit(sc_t, sc_t.get_rect(center=(cx, 310)))

        hs   = self.highscores.get(self.difficulty, 0)
        if self.score >= hs:
            hr_t = self.font_med.render("🏆  YANGI REKORD!", True, YELLOW)
            self.screen.blit(hr_t, hr_t.get_rect(center=(cx, 355)))
        else:
            hr_t = self.font_small.render(f"Rekord: {hs}", True, LIGHT_GRAY)
            self.screen.blit(hr_t, hr_t.get_rect(center=(cx, 355)))

        diff_col = {"Easy": GREEN, "Medium": YELLOW, "Hard": RED}.get(self.difficulty, WHITE)
        df_t = self.font_small.render(f"Qiyinlik: {self.difficulty}", True, diff_col)
        self.screen.blit(df_t, df_t.get_rect(center=(cx, 390)))

        for btn in self.gameover_buttons:
            btn.update(mouse)
            btn.draw(self.screen)

        for e in events:
            if self.gameover_buttons[0].handle_event(e):
                self._reset_game(); self.state = STATE_PLAYING
            elif self.gameover_buttons[1].handle_event(e):
                self.state = STATE_MENU

    # ─── O'YIN ───────────────────────────────
    def _playing(self, events):
        mouse  = pygame.mouse.get_pos()
        keys   = pygame.key.get_pressed()

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.state = STATE_PAUSED
                return

        # Road scroll
        speed_factor = self.enemy_speed / self.base_enemy_speed
        self.road_y += self.enemy_speed * 0.6
        if self.road_y > 80:
            self.road_y -= 80

        # Harakat
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right= keys[pygame.K_RIGHT] or keys[pygame.K_d]
        tilt_target = 0
        if moving_left and self.player_x > 0:
            self.player_x -= self.player_speed
            tilt_target = -15
        if moving_right and self.player_x < SCREEN_WIDTH - 50:
            self.player_x += self.player_speed
            tilt_target = 15
        self.player_tilt += (tilt_target - self.player_tilt) * 0.18

        # O'q otish
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shot_cd:
                self.last_shot = now
                cx = self.player_x + 25 - 4
                if self.double_timer > 0:
                    self.bullets.append(pygame.Rect(cx-12, self.player_y, 8, 20))
                    self.bullets.append(pygame.Rect(cx+12, self.player_y, 8, 20))
                else:
                    self.bullets.append(pygame.Rect(cx, self.player_y, 8, 20))
                self._play_sound(self.snd_shoot)

        # Dushman spawn
        self.spawn_timer += 1
        base_rate = max(6, self.spawn_rate - int(self.score / 500))
        if self.spawn_timer >= base_rate:
            self.spawn_timer = 0
            self._spawn_enemy()

        # Dushmanlarni yangilash
        for en in self.enemies[:]:
            en.update(self.enemy_bullets)
            if en.rect.y > SCREEN_HEIGHT + 10:
                self.enemies.remove(en)

        # O'qlarni yangilash
        for b in self.bullets[:]:
            b.y -= 14
            if b.y < -20:
                self.bullets.remove(b)
                continue
            hit = False
            for en in self.enemies[:]:
                if b.colliderect(en.rect):
                    en.hp   -= 1
                    en.flash = 5
                    hit      = True
                    self.bullets.remove(b)
                    if en.hp <= 0:
                        self._explode(en.rect.centerx, en.rect.centery)
                        self.enemies.remove(en)
                        pts = {"Easy":10,"Medium":15,"Hard":25}.get(self.difficulty,10)
                        self.score     += pts
                        self.score_flash = 8
                        # Tezlik oshishi
                        self.enemy_speed = self.base_enemy_speed + self.score * 0.003
                        # Power-up
                        if random.random() < 0.12:
                            self._spawn_powerup(en.rect.centerx, en.rect.centery)
                    break
            if hit:
                continue

        # Dushman o'qlari
        for eb in self.enemy_bullets[:]:
            eb.y += 8
            if eb.y > SCREEN_HEIGHT + 10:
                self.enemy_bullets.remove(eb)
                continue
            player_rect = pygame.Rect(self.player_x+8, self.player_y+8, 34, 54)
            if eb.colliderect(player_rect) and self.invincible <= 0 and self.shield_timer <= 0:
                self.enemy_bullets.remove(eb)
                self._take_damage()

        # O'yinchi va dushman to'qnashuvi
        player_rect = pygame.Rect(self.player_x+8, self.player_y+8, 34, 54)
        for en in self.enemies[:]:
            if en.rect.colliderect(player_rect) and self.invincible <= 0:
                if self.shield_timer > 0:
                    self._explode(en.rect.centerx, en.rect.centery)
                    self.enemies.remove(en)
                    self.score += 5
                else:
                    self._explode(en.rect.centerx, en.rect.centery)
                    self.enemies.remove(en)
                    self._take_damage()

        # Power-uplar
        for pu in self.powerups[:]:
            pu.update()
            if pu.rect.y > SCREEN_HEIGHT + 10:
                self.powerups.remove(pu)
                continue
            if pu.rect.colliderect(player_rect):
                self._collect_powerup(pu.kind)
                self.powerups.remove(pu)

        # Taymerni kamaytirish
        if self.shield_timer > 0: self.shield_timer -= 1
        if self.double_timer > 0: self.double_timer -= 1
        if self.slow_timer   > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                for en in self.enemies:
                    en.speed = self.enemy_speed
        if self.invincible   > 0: self.invincible   -= 1
        if self.score_flash  > 0: self.score_flash  -= 1
        if self.msg_timer    > 0: self.msg_timer    -= 1

        # Zarrachalar
        self._update_particles()

        # ── CHIZISH ──────────────────────────
        self._draw_background()
        self._draw_road()

        # Power-uplar
        for pu in self.powerups:
            pu.draw(self.screen, self.t)

        # Dushmanlar
        for en in self.enemies:
            en.draw(self.screen)

        # Dushman o'qlari
        for eb in self.enemy_bullets:
            self.screen.blit(self.enemy_bullet_surf, (eb.x, eb.y))

        # O'yinchi
        self._draw_player()

        # O'qlar
        for b in self.bullets:
            self.screen.blit(self.bullet_surf, (b.x, b.y))

        # Zarrachalar
        self._draw_particles()

        # HUD
        self._draw_hud()

    def _take_damage(self):
        self._play_sound(self.snd_hit)
        self.lives    -= 1
        self.invincible = 120
        if self.lives <= 0:
            # Rekord yangilash
            hs = self.highscores.get(self.difficulty, 0)
            if self.score > hs:
                self.highscores[self.difficulty] = self.score
                save_highscores(self.highscores)
            self.state = STATE_GAMEOVER
        else:
            self.msg       = f"❤  {self.lives} jon qoldi!"
            self.msg_timer = 90

    def _spawn_enemy(self):
        x    = random.randint(190, SCREEN_WIDTH - 240)
        en   = Enemy(
            x, -80,
            speed   = self.enemy_speed * (0.8 + random.random()*0.4),
            shoot   = self.cfg["enemy_shoot"] and random.random() < 0.35,
            hp      = self.cfg["hp"] if self.score > 300 else 1,
            zigzag  = self.cfg["zigzag"] and random.random() < 0.3,
        )
        if self.slow_timer > 0:
            en.speed *= 0.4
        self.enemies.append(en)

    def _spawn_powerup(self, x, y):
        kind = random.choice([PU_SHIELD, PU_DOUBLE, PU_SLOW, PU_LIFE])
        self.powerups.append(PowerUp(x-18, y, kind))

    def _collect_powerup(self, kind):
        self._play_sound(self.snd_powerup)
        if kind == PU_SHIELD:
            self.shield_timer = 300
            self.msg       = "🛡  Qalqon faollashdi!"
        elif kind == PU_DOUBLE:
            self.double_timer = 400
            self.msg       = "✦✦  Ikki barobar o'q!"
        elif kind == PU_SLOW:
            self.slow_timer = 300
            for en in self.enemies:
                en.speed *= 0.4
            self.msg       = "❄  Dushmanlar sekinlashdi!"
        elif kind == PU_LIFE:
            self.lives = min(self.lives + 1, 5)
            self.msg   = "❤  Qo'shimcha jon!"
        self.msg_timer = 120

    def _explode(self, x, y):
        self._play_sound(self.snd_explode)
        for _ in range(random.randint(18, 30)):
            self.particles.append(Particle(x, y))

    def _update_particles(self):
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

    def _draw_particles(self):
        for p in self.particles:
            p.draw(self.screen)

    def _draw_player(self):
        img    = self.player_img
        tilted = pygame.transform.rotate(img, self.player_tilt)
        # Shield effect
        if self.shield_timer > 0:
            alpha   = int(180 * pulse(self.t, 5, 0.6, 1.0))
            r_      = max(36, 50 - int(self.shield_timer * 0.05))
            glow    = pygame.Surface((r_*2+10, r_*2+10), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 180, 255, alpha), (r_+5, r_+5), r_)
            cx_     = self.player_x + 25
            cy_     = self.player_y + 35
            self.screen.blit(glow, (cx_ - r_ - 5, cy_ - r_ - 5))
        # Invincible yanib söner
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return
        cx_  = self.player_x + 25 - tilted.get_width()//2
        cy_  = self.player_y + 35 - tilted.get_height()//2
        self.screen.blit(tilted, (cx_, cy_))

    def _draw_hud(self):
        cx = SCREEN_WIDTH // 2

        # Yuqori panel
        panel = pygame.Rect(0, 0, SCREEN_WIDTH, 52)
        overlay = pygame.Surface((SCREEN_WIDTH, 52), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 180))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.line(self.screen, CYAN, (0,52), (SCREEN_WIDTH,52), 2)

        # Ochko
        sc_col = YELLOW if self.score_flash > 0 else WHITE
        sc_t   = self.font_med.render(f"✦ {self.score}", True, sc_col)
        self.screen.blit(sc_t, (20, 10))

        # Tezlik
        spd_t  = self.font_small.render(f"Tezlik: {self.enemy_speed:.1f}", True, LIGHT_GRAY)
        self.screen.blit(spd_t, spd_t.get_rect(center=(cx, 18)))

        # Jonlar
        for i in range(5):
            col    = RED if i < self.lives else DARK_GRAY
            alpha  = 255 if i < self.lives else 80
            s      = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, alpha), (11,11), 10)
            ht     = self.font_small.render("♥", True, (*col, alpha) if alpha == 255 else DARK_GRAY)
            s.blit(ht, ht.get_rect(center=(11,11)))
            self.screen.blit(s, (SCREEN_WIDTH - 30 - i*28, 14))

        # Power-up indikatorlari
        py_  = 60
        indicators = []
        if self.shield_timer > 0:
            indicators.append((f"🛡 {self.shield_timer//60+1}s", CYAN))
        if self.double_timer > 0:
            indicators.append((f"✦✦ {self.double_timer//60+1}s", YELLOW))
        if self.slow_timer > 0:
            indicators.append((f"❄ {self.slow_timer//60+1}s", GREEN))

        for idx, (txt, col) in enumerate(indicators):
            t_s    = self.font_small.render(txt, True, col)
            bg_    = pygame.Rect(10 + idx*120, py_, t_s.get_width()+16, 28)
            draw_rounded_rect(self.screen, (20,20,50), bg_, 6)
            draw_rounded_rect(self.screen, col, bg_, 6, 1, col)
            self.screen.blit(t_s, (bg_.x+8, bg_.y+4))

        # Xabar
        if self.msg_timer > 0:
            alpha_ = min(255, self.msg_timer * 6)
            m_s    = self.font_med.render(self.msg, True, YELLOW)
            bg_r   = m_s.get_rect(center=(cx, SCREEN_HEIGHT - 80))
            bg_r.inflate_ip(20, 10)
            draw_rounded_rect(self.screen, (0,0,0), bg_r, 10)
            self.screen.blit(m_s, m_s.get_rect(center=(cx, SCREEN_HEIGHT - 80)))

        # Qiyinlik belgisi (pastki o'ng)
        diff_col = {"Easy": GREEN, "Medium": YELLOW, "Hard": RED}.get(self.difficulty, WHITE)
        df_t     = self.font_tiny.render(f"[{self.difficulty}]", True, diff_col)
        self.screen.blit(df_t, (SCREEN_WIDTH-70, SCREEN_HEIGHT-24))

        # ESC = pause
        esc_t    = self.font_tiny.render("ESC = Pauza", True, GRAY)
        self.screen.blit(esc_t, (8, SCREEN_HEIGHT-24))

# ─────────────────────────────────────────────
#  ISHGA TUSHIRISH
# ─────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()
