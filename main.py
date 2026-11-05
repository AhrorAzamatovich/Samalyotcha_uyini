"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          SAMALYOTCHA O'YINI  —  Ultimate Professional Edition v3.0          ║
║                        by  Ahrorazamatovich                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  • 1 yoki 2 o'yinchi rejimi                                                 ║
║  • Player 1: Klaviatura  (WASD / Strelkalar + SPACE)                        ║
║  • Player 2: Sichqoncha  (Harakatlanish + LMB)                              ║
║  • Boss Battle tizimi (3 faza, 5 otish naqshi)                              ║
║  • 7 ta Power-up, Combo tizimi, Screen Shake                                ║
║  • Protsessual grafika va sintetik ovozlar                                  ║
║  • Standalone EXE  (python build.py  yoki  build.bat)                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations
import sys, os, json, math, random, struct, array

# ─── PyInstaller bundle resource path ────────────────────────────────────────
if getattr(sys, "frozen", False):
    _BASE = sys._MEIPASS  # type: ignore[attr-defined]
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_BASE)
sys.path.insert(0, _BASE)

import pygame

# ════════════════════════════════════════════════════════════════════════════
#  KONSTANTALAR
# ════════════════════════════════════════════════════════════════════════════

SW, SH, FPS = 1280, 760, 60

# Ranglar
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0  )
RED        = (220, 40,  40 )
DARK_RED   = (150, 20,  20 )
GREEN      = (40,  200, 80 )
DARK_GREEN = (20,  130, 50 )
BLUE       = (40,  120, 220)
YELLOW     = (255, 220, 0  )
ORANGE     = (255, 140, 0  )
CYAN       = (0,   220, 220)
PURPLE     = (160, 40,  200)
MAGENTA    = (255, 60,  200)
GRAY       = (100, 100, 100)
LGRAY      = (180, 180, 180)
DGRAY      = (40,  40,  40 )
ROAD_COL   = (42,  44,  56 )
ROAD_LINE  = (220, 200, 50 )
ROAD_EDGE  = (70,  72,  88 )
BG_TOP     = (8,   8,   24 )
BG_BOT     = (18,  18,  52 )
P1_COLOR   = (60,  160, 255)   # Ko'k — Player 1
P2_COLOR   = (255, 120, 40 )   # To'q sariq — Player 2

# Holat mashinalari
ST_SPLASH     = "splash"
ST_MENU       = "menu"
ST_MODE_SEL   = "mode_sel"
ST_DIFFICULTY = "difficulty"
ST_PLAYING    = "playing"
ST_PAUSED     = "paused"
ST_GAMEOVER   = "gameover"
ST_LEADERBOARD= "leaderboard"
ST_SETTINGS   = "settings"

# Power-up turlari
PU_SHIELD = "shield"
PU_DOUBLE = "double"
PU_SLOW   = "slow"
PU_LIFE   = "life"
PU_NUKE   = "nuke"
PU_SPEED  = "speed"
PU_LASER  = "laser"
PU_ALL    = [PU_SHIELD, PU_DOUBLE, PU_SLOW, PU_LIFE, PU_NUKE, PU_SPEED, PU_LASER]
PU_WEIGHTS= [18,        16,        16,      12,       8,        14,       10     ]

# Data fayllar
_DATA_DIR    = os.path.join(_BASE, "data")
HS_FILE      = os.path.join(_DATA_DIR, "highscores.json")
SETT_FILE    = os.path.join(_DATA_DIR, "settings.json")


# ════════════════════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ════════════════════════════════════════════════════════════════════════════

def lerp(a, b, t):         return a + (b - a) * t
def clamp(v, lo, hi):      return max(lo, min(hi, v))
def pulse(t, spd=3, mn=0.7, mx=1.0): return mn + (mx-mn)*(0.5 + 0.5*math.sin(t*spd))

def draw_grad(surf, c1, c2, rect, horiz=False):
    r1,g1,b1 = c1[:3]; r2,g2,b2 = c2[:3]
    n = rect.width if horiz else rect.height
    for i in range(n):
        t = i/max(n-1,1)
        col = (int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))
        if horiz: pygame.draw.line(surf, col, (rect.x+i, rect.y), (rect.x+i, rect.bottom))
        else:     pygame.draw.line(surf, col, (rect.x, rect.y+i), (rect.right, rect.y+i))

def draw_rrect(surf, col, rect, r=12, bw=0, bc=None):
    if len(col)==4 and col[3]<255:
        tmp = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(tmp, col, (0,0,*rect.size), border_radius=r)
        surf.blit(tmp, rect.topleft)
    else:
        pygame.draw.rect(surf, col, rect, border_radius=r)
    if bw and bc:
        pygame.draw.rect(surf, bc, rect, bw, border_radius=r)

def draw_glow(surf, col, cx, cy, r, layers=5, base_alpha=40):
    for i in range(layers, 0, -1):
        rr = r + i*5
        a  = base_alpha*i//layers
        tmp = pygame.Surface((rr*2, rr*2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*col[:3], a), (rr,rr), rr)
        surf.blit(tmp, (cx-rr, cy-rr))

def draw_hp_bar(surf, x, y, w, h, ratio, bg=(50,10,10), fc=None, bc=(180,180,180), r=4):
    if fc is None:
        fc = GREEN if ratio>0.6 else (YELLOW if ratio>0.3 else RED)
    pygame.draw.rect(surf, bg, (x,y,w,h), border_radius=r)
    fw = max(0, int(w*ratio))
    if fw: pygame.draw.rect(surf, fc, (x,y,fw,h), border_radius=r)
    pygame.draw.rect(surf, bc, (x,y,w,h), 1, border_radius=r)

def os_makedirs():
    os.makedirs(_DATA_DIR, exist_ok=True)

def load_hs():
    os_makedirs()
    d = {"Easy":0,"Medium":0,"Hard":0,"coop":0,"sessions":0}
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE) as f: data = json.load(f)
            for k,v in d.items(): data.setdefault(k,v)
            return data
        except: pass
    return d

def save_hs(d):
    os_makedirs()
    try:
        with open(HS_FILE,"w") as f: json.dump(d, f, indent=2)
    except: pass

def load_settings():
    os_makedirs()
    d = {"sfx":0.7,"music":0.4,"sound_on":True,"music_on":True,"fps_show":False,"scanlines":False,"fullscreen":False}
    if os.path.exists(SETT_FILE):
        try:
            with open(SETT_FILE) as f: data = json.load(f)
            for k,v in d.items(): data.setdefault(k,v)
            return data
        except: pass
    return d

def save_settings(d):
    os_makedirs()
    try:
        with open(SETT_FILE,"w") as f: json.dump(d, f, indent=2)
    except: pass


# ════════════════════════════════════════════════════════════════════════════
#  SINTETIK OVOZ GENERATORI
# ════════════════════════════════════════════════════════════════════════════

def _stereo(mono_list):
    """16-bit mono list → pygame.mixer.Sound (stereo)"""
    buf = array.array("h")
    for s in mono_list:
        v = max(-32768, min(32767, int(s)))
        buf.append(v); buf.append(v)
    try:
        return pygame.sndarray.make_sound(
            pygame.sndarray.array(
                pygame.mixer.Sound(buffer=buf.tobytes()).get_raw()
            ).reshape((-1,2))
        )
    except:
        return None

def gen_shoot():
    sr,dur=44100,0.10; n=int(sr*dur)
    return _stereo([math.sin(2*math.pi*(900*(0.25**(i/sr/dur)))*i/sr)*max(0,(1-i/n)**0.5)*0.35*32767 for i in range(n)])

def gen_shoot2():
    sr,dur=44100,0.08; n=int(sr*dur)
    return _stereo([(1.0 if math.sin(2*math.pi*(600+400*i/n)*i/sr)>=0 else -1.0)*max(0,1-i/n)*0.25*32767 for i in range(n)])

def gen_laser():
    sr,dur=44100,0.22; n=int(sr*dur)
    return _stereo([(math.sin(2*math.pi*(1200-700*i/n)*i/sr)*0.8+random.gauss(0,0.1)*0.2)*max(0,1-i/n)**0.3*0.45*32767 for i in range(n)])

def gen_explode():
    sr,dur=44100,0.45; n=int(sr*dur)
    return _stereo([random.randint(-32767,32767)*max(0,1-i/n)**1.5*0.55 for i in range(n)])

def gen_explode_big():
    sr,dur=44100,0.9; n=int(sr*dur)
    return _stereo([(random.randint(-32767,32767)/32767*0.7+math.sin(2*math.pi*60*i/sr)*0.3)*max(0,1-i/n)**1.2*0.65*32767 for i in range(n)])

def gen_powerup():
    sr,dur=44100,0.35; n=int(sr*dur)
    return _stereo([math.sin(2*math.pi*(400+1200*(i/n)**0.7)*i/sr)*max(0,1-i/n)**0.4*0.50*32767 for i in range(n)])

def gen_hit():
    sr,dur=44100,0.25; n=int(sr*dur)
    return _stereo([(math.sin(2*math.pi*180*i/sr)*0.6+random.gauss(0,0.3)*0.4)*max(0,1-i/n)**0.8*0.65*32767 for i in range(n)])

def gen_boss_roar():
    sr,dur=44100,1.2; n=int(sr*dur)
    buf=[]
    for i in range(n):
        t=i/sr
        f=80+40*math.sin(2*math.pi*3*t)
        env=min(1.0,i/(sr*0.15))*max(0,1-(t/dur)**1.5)
        buf.append((math.sin(2*math.pi*f*t)+math.sin(2*math.pi*f*2.01*t)*0.4+random.gauss(0,0.15))*env*0.55*32767)
    return _stereo(buf)

def gen_shield():
    sr,dur=44100,0.4; n=int(sr*dur)
    return _stereo([math.sin(2*math.pi*(800+400*math.sin(2*math.pi*8*i/sr))*i/sr)*max(0,1-(i/n)**2)*0.4*32767 for i in range(n)])

def gen_nuke():
    sr,dur=44100,1.5; n=int(sr*dur)
    return _stereo([(random.randint(-32767,32767)/32767*0.7+math.sin(2*math.pi*40*i/sr)*0.4)*max(0,1-(i/sr/dur)**0.8)*0.7*32767 for i in range(n)])

def gen_levelup():
    sr,dur=44100,0.6; n=int(sr*dur); notes=[523,659,784,1047]
    return _stereo([math.sin(2*math.pi*notes[min(int(i/sr/(dur/len(notes))),len(notes)-1)]*i/sr)*0.4*32767 for i in range(n)])

def gen_tick():
    sr,dur=44100,0.05; n=int(sr*dur)
    return _stereo([math.sin(2*math.pi*1200*i/sr)*max(0,1-i/n)*0.2*32767 for i in range(n)])

def gen_combo():
    sr,dur=44100,0.3; n=int(sr*dur)
    return _stereo([(math.sin(2*math.pi*(600+800*i/n)*i/sr)*0.7+math.sin(2*math.pi*(600+800*i/n)*1.5*i/sr)*0.3)*max(0,1-(i/n)**0.5)*0.45*32767 for i in range(n)])

def gen_victory():
    sr,dur=44100,1.0; n=int(sr*dur); notes=[523,659,784,880,1047,1047]
    buf=[]
    for i in range(n):
        ni = min(int(i/sr/(dur/len(notes))), len(notes)-1)
        buf.append(math.sin(2*math.pi*notes[ni]*i/sr)*0.45*32767)
    return _stereo(buf)

def gen_bg_music():
    """Ambient lo-fi background musiqa (12 soniya loop)"""
    sr=44100; dur=12.0; n=int(sr*dur)
    import array as _a
    buf = _a.array("h", [0]*n*2)
    pad_freqs = [130.8, 174.6, 261.6]
    for freq in pad_freqs:
        for i in range(n):
            t=i/sr
            v = (math.sin(2*math.pi*freq*t)*0.07
                 + math.sin(2*math.pi*freq*2.001*t)*0.035
                 + math.sin(2*math.pi*freq*3.002*t)*0.018)
            v *= 0.8+0.2*math.sin(2*math.pi*0.4*t)
            s = max(-32768, min(32767, int(v*32767)))
            buf[i*2]   = max(-32768,min(32767, buf[i*2]+s))
            buf[i*2+1] = max(-32768,min(32767, buf[i*2+1]+s))
    kick_int = int(sr*0.5)
    for ks in range(0, n, kick_int):
        for j in range(min(int(sr*0.08), n-ks)):
            f_k=80*(0.01**(j/sr/0.08))
            env=max(0.0,1.0-j/(sr*0.08))**2
            s=max(-32768,min(32767,int(math.sin(2*math.pi*f_k*j/sr)*env*0.12*32767)))
            idx=ks+j
            if idx<n:
                buf[idx*2]=max(-32768,min(32767,buf[idx*2]+s))
                buf[idx*2+1]=max(-32768,min(32767,buf[idx*2+1]+s))
    hat_int = int(sr*0.25)
    for hs in range(hat_int//2, n, hat_int):
        for j in range(min(int(sr*0.02), n-hs)):
            noise=random.randint(-800,800)
            env=max(0.0,1.0-j/(sr*0.02))
            s=max(-32768,min(32767,int(noise*env)))
            idx=hs+j
            if idx<n:
                buf[idx*2]=max(-32768,min(32767,buf[idx*2]+s))
                buf[idx*2+1]=max(-32768,min(32767,buf[idx*2+1]+s))
    try:
        snd = pygame.sndarray.make_sound(
            pygame.sndarray.array(pygame.mixer.Sound(buffer=buf.tobytes()).get_raw()).reshape((-1,2))
        )
        return snd
    except:
        return None


# ════════════════════════════════════════════════════════════════════════════
#  GRAFIK ASSET GENERATORI
# ════════════════════════════════════════════════════════════════════════════

def make_player_surf(w=56, h=76, col=(60,160,255)):
    s = pygame.Surface((w,h), pygame.SRCALPHA)
    body = pygame.Rect(w//2-13, 10, 26, h-18)
    draw_grad(s, tuple(min(255,c+60) for c in col[:3]), col, body)
    pygame.draw.rect(s, (200,230,255), body, 2, border_radius=6)
    for pts in [[(0,h-26),(w//2-13,h-46),(w//2-13,h-18)],
                [(w,h-26),(w//2+13,h-46),(w//2+13,h-18)]]:
        pygame.draw.polygon(s, tuple(max(0,c-50) for c in col[:3]), pts)
        pygame.draw.polygon(s, tuple(min(255,c+40) for c in col[:3]), pts, 2)
    for pts in [[(w//2-22,22),(w//2-13,15),(w//2-13,30)],
                [(w//2+22,22),(w//2+13,15),(w//2+13,30)]]:
        pygame.draw.polygon(s, tuple(max(0,c-30) for c in col[:3]), pts)
    cpit = pygame.Rect(w//2-8,12,16,22)
    draw_grad(s, (200,240,255), (100,180,240), cpit)
    pygame.draw.rect(s, (220,255,255), cpit, 1, border_radius=5)
    for dx in [-7,7]:
        ex,ey = w//2+dx, h-8
        pygame.draw.ellipse(s, (50,50,70), (ex-4,ey-5,8,10))
        pygame.draw.polygon(s, ORANGE, [(ex,ey),(ex-5,ey+14),(ex+5,ey+14)])
        pygame.draw.polygon(s, YELLOW, [(ex,ey+2),(ex-3,ey+9),(ex+3,ey+9)])
    return s

def make_enemy_surf(w=52, h=72, ct=(220,60,60), cb=(140,20,20)):
    s = pygame.Surface((w,h), pygame.SRCALPHA)
    body = pygame.Rect(w//2-12, 8, 24, h-14)
    draw_grad(s, ct, cb, body)
    pygame.draw.rect(s, tuple(min(255,c+60) for c in ct), body, 2, border_radius=5)
    for pts in [[(0,22),(w//2-12,38),(w//2-12,14)],
                [(w,22),(w//2+12,38),(w//2+12,14)]]:
        pygame.draw.polygon(s, tuple(max(0,c-40) for c in ct), pts)
        pygame.draw.polygon(s, tuple(min(255,c+40) for c in ct), pts, 2)
    cpit = pygame.Rect(w//2-7,12,14,18)
    draw_grad(s, (255,200,200), (200,80,80), cpit)
    pygame.draw.rect(s, (255,220,220), cpit, 1, border_radius=4)
    return s

def make_boss_surf(w=180, h=140):
    s = pygame.Surface((w,h), pygame.SRCALPHA)
    body = pygame.Rect(w//2-38,10,76,h-20)
    draw_grad(s, (200,0,240), (90,0,130), body)
    pygame.draw.rect(s, (255,100,255), body, 3, border_radius=12)
    for pts in [[(0,50),(w//2-38,72),(w//2-38,28),(18,18)],
                [(w,50),(w//2+38,72),(w//2+38,28),(w-18,18)]]:
        pygame.draw.polygon(s, (130,0,190), pts)
        pygame.draw.polygon(s, (210,80,255), pts, 2)
    cx,cy=w//2,22
    pygame.draw.ellipse(s,(80,200,255),(cx-20,cy,40,32))
    pygame.draw.ellipse(s,(180,240,255),(cx-20,cy,40,32),2)
    for dx in [-30,0,30]:
        pygame.draw.circle(s,(255,60,60),(w//2+dx,h-14),9)
        pygame.draw.circle(s,(255,150,150),(w//2+dx,h-14),9,2)
    pygame.draw.line(s,(255,100,255),(w//2-38,56),(w//2+38,56),2)
    pygame.draw.line(s,(255,100,255),(w//2-38,78),(w//2+38,78),1)
    return s

def make_bullet_surf(w=8,h=22,col1=YELLOW,col2=ORANGE):
    s = pygame.Surface((w,h),pygame.SRCALPHA)
    draw_grad(s, col1, col2, pygame.Rect(1,0,w-2,h))
    pygame.draw.rect(s, WHITE, pygame.Rect(w//2-1,0,2,h//3))
    pygame.draw.polygon(s, WHITE, [(w//2,0),(1,4),(w-1,4)])
    return s

def make_enemy_bullet_surf():
    return make_bullet_surf(8,20,(255,80,80),(180,20,20))

def make_boss_bullet_surf():
    s = pygame.Surface((14,32), pygame.SRCALPHA)
    draw_grad(s,(255,100,255),(160,0,210),pygame.Rect(0,0,14,32))
    pygame.draw.rect(s,(255,200,255),pygame.Rect(5,0,4,8))
    pygame.draw.ellipse(s,(255,80,255),pygame.Rect(0,0,14,10))
    return s

def make_powerup_surf(kind, sz=40):
    s = pygame.Surface((sz,sz),pygame.SRCALPHA)
    cx,cy,r = sz//2,sz//2,sz//2-3
    cm = {PU_SHIELD:((0,180,255,220),(100,220,255)),
          PU_DOUBLE:((255,200,0,220),(255,240,100)),
          PU_SLOW:  ((0,220,120,220),(100,255,180)),
          PU_LIFE:  ((255,60,100,220),(255,140,160)),
          PU_NUKE:  ((255,120,0,220),(255,200,80)),
          PU_SPEED: ((80,255,80,220),(180,255,180)),
          PU_LASER: ((255,80,200,220),(255,180,240))}
    fill,border = cm.get(kind,((200,200,200,200),(255,255,255)))
    pygame.draw.circle(s,fill,(cx,cy),r)
    pygame.draw.circle(s,border,(cx,cy),r,3)
    pygame.draw.circle(s,(255,255,255,60),(cx-r//3,cy-r//3),r//3)
    icons = {PU_SHIELD:"S",PU_DOUBLE:"2x",PU_SLOW:"ICE",PU_LIFE:"+HP",PU_NUKE:"NUK",PU_SPEED:">>>",PU_LASER:"LZR"}
    f = pygame.font.SysFont("Arial",13,bold=True)
    t = f.render(icons.get(kind,"?"),True,WHITE)
    s.blit(t,t.get_rect(center=(cx,cy+1)))
    return s

ENEMY_VARIANTS = [
    ((220,60,60),(140,20,20)),
    ((200,80,40),(120,30,10)),
    ((180,60,200),(100,20,140)),
    ((60,180,220),(20,100,160)),
    ((220,200,40),(140,120,0)),
]


# ════════════════════════════════════════════════════════════════════════════
#  ZARRACHALAR
# ════════════════════════════════════════════════════════════════════════════

class Particle:
    __slots__ = ("x","y","vx","vy","life","ml","col","r","trail")
    PAL = [YELLOW,(255,180,50),ORANGE,RED,WHITE,(255,220,80)]

    def __init__(self, x, y, power=1.0):
        a = random.uniform(0,math.tau); sp = random.uniform(1.5,9.0)*power
        self.x=x; self.y=y
        self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp-random.uniform(0,2)
        self.life=random.randint(18,55); self.ml=self.life
        self.col=random.choice(self.PAL); self.r=random.uniform(1.5,5.5)*power
        self.trail=[]

    def update(self):
        self.trail.append((self.x,self.y))
        if len(self.trail)>4: self.trail.pop(0)
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.18; self.vx*=0.98; self.life-=1

    def draw(self, surf):
        ratio=self.life/self.ml; alpha=int(255*ratio); r=max(1,int(self.r*ratio))
        for i,(tx,ty) in enumerate(self.trail):
            tr=max(1,int(r*(i+1)/len(self.trail)*0.5)); ta=int(alpha*(i+1)/len(self.trail)*0.4)
            if tr>0:
                tmp=pygame.Surface((tr*2,tr*2),pygame.SRCALPHA)
                pygame.draw.circle(tmp,(*self.col,ta),(tr,tr),tr)
                surf.blit(tmp,(int(tx)-tr,int(ty)-tr))
        if r>0:
            tmp=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
            pygame.draw.circle(tmp,(*self.col,alpha),(r,r),r)
            surf.blit(tmp,(int(self.x)-r,int(self.y)-r))

class DebrisPart:
    __slots__=("x","y","vx","vy","life","ml","col","w","h","ang","av")
    def __init__(self,x,y):
        a=random.uniform(0,math.tau); sp=random.uniform(1,6)
        self.x=x;self.y=y;self.vx=math.cos(a)*sp;self.vy=math.sin(a)*sp-random.uniform(0,3)
        self.life=random.randint(25,60);self.ml=self.life
        self.col=random.choice([(180,180,180),(120,120,130),(200,160,80)])
        self.w=random.randint(3,9);self.h=random.randint(2,5)
        self.ang=random.uniform(0,360);self.av=random.uniform(-8,8)
    def update(self):
        self.x+=self.vx;self.y+=self.vy;self.vy+=0.25;self.vx*=0.97;self.ang+=self.av;self.life-=1
    def draw(self,surf):
        ratio=self.life/self.ml;alpha=int(200*ratio)
        tmp=pygame.Surface((self.w+2,self.h+2),pygame.SRCALPHA)
        pygame.draw.rect(tmp,(*self.col,alpha),(0,0,self.w,self.h))
        rot=pygame.transform.rotate(tmp,self.ang)
        surf.blit(rot,(int(self.x)-rot.get_width()//2,int(self.y)-rot.get_height()//2))

class SmokePart:
    __slots__=("x","y","vx","vy","life","ml","r","col")
    def __init__(self,x,y):
        self.x=x+random.uniform(-3,3);self.y=y
        self.vx=random.uniform(-0.3,0.3);self.vy=random.uniform(1.5,3.5)
        self.life=random.randint(10,25);self.ml=self.life
        b=random.randint(80,130);self.col=(b,b,b);self.r=random.uniform(2,5)
    def update(self):
        self.x+=self.vx;self.y+=self.vy;self.r+=0.15;self.life-=1
    def draw(self,surf):
        ratio=self.life/self.ml;alpha=int(80*ratio);r=int(self.r)
        if r<=0: return
        tmp=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(tmp,(*self.col,alpha),(r,r),r)
        surf.blit(tmp,(int(self.x)-r,int(self.y)-r))

class Star:
    __slots__=("x","y","spd","r","br","tw")
    def __init__(self,initial=False):
        self.reset(initial)
    def reset(self,initial=False):
        self.x=random.randint(0,SW)
        self.y=random.randint(0,SH) if initial else -5
        layer=random.randint(1,3)
        self.spd=[0.3,1.0,2.5][layer-1]; self.r=layer
        self.br=random.randint(120,255); self.tw=random.uniform(0,math.tau)
    def update(self,mult=1.0):
        self.y+=self.spd*mult
        if self.y>SH+5: self.reset()
    def draw(self,surf,t):
        b=int(self.br*(0.7+0.3*math.sin(t*0.05+self.tw)))
        pygame.draw.circle(surf,(b,b,b),(int(self.x),int(self.y)),self.r)


class ParticleMgr:
    def __init__(self): self._p=[]
    def explode(self,x,y,power=1.0,mult=1.0):
        n=int(random.randint(18,30)*mult)
        for _ in range(n): self._p.append(Particle(x,y,power))
        for _ in range(int(n*0.4)): self._p.append(DebrisPart(x,y))
    def smoke(self,x,y):
        if random.random()<0.4: self._p.append(SmokePart(x,y))
    def update(self): self._p=[p for p in self._p if p.life>0]; [p.update() for p in self._p]
    def draw(self,surf): [p.draw(surf) for p in self._p]
    def clear(self): self._p.clear()


# ════════════════════════════════════════════════════════════════════════════
#  TUGMA
# ════════════════════════════════════════════════════════════════════════════

class Button:
    def __init__(self,text,rect,col=(40,120,220),hcol=None,tcol=WHITE,fsz=28,rad=14,icon=""):
        self.text=text; self.icon=icon
        self.rect=pygame.Rect(rect); self.col=col
        self.hcol=hcol or tuple(min(255,c+50) for c in col)
        self.tcol=tcol; self.rad=rad; self._sc=1.0; self._hov=False
        self._rip_r=0; self._rip_a=0; self._rip_cx=0; self._rip_cy=0
        self._font=pygame.font.SysFont("Arial",fsz,bold=True)

    def event(self,e):
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if self.rect.collidepoint(e.pos):
                self._rip_r=4; self._rip_a=180; self._rip_cx,self._rip_cy=e.pos; return True
        return False

    def update(self,mp):
        self._hov=self.rect.collidepoint(mp)
        self._sc=lerp(self._sc,1.06 if self._hov else 1.0,0.18)
        if self._rip_r>0: self._rip_r+=7; self._rip_a=max(0,self._rip_a-14)
        if not self._rip_a: self._rip_r=0

    def draw(self,surf):
        sc=self._sc; w=int(self.rect.width*sc); h=int(self.rect.height*sc)
        rx=self.rect.centerx-w//2; ry=self.rect.centery-h//2; r=pygame.Rect(rx,ry,w,h)
        # Shadow
        tmp=pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.rect(tmp,(0,0,0,70),(0,0,w,h),border_radius=self.rad)
        surf.blit(tmp,(rx+5,ry+5))
        # Gradient bg
        col=self.hcol if self._hov else self.col
        bg=pygame.Surface((w,h),pygame.SRCALPHA)
        for i in range(h):
            t=i/max(h-1,1); c=(*tuple(int(col[k]*(1-t*0.3)) for k in range(3)),235)
            pygame.draw.line(bg,c,(0,i),(w,i))
        mask=pygame.Surface((w,h),pygame.SRCALPHA)
        pygame.draw.rect(mask,WHITE,(0,0,w,h),border_radius=self.rad)
        bg.blit(mask,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(bg,r.topleft)
        # Highlight + border
        hi=pygame.Surface((w-4,h//3),pygame.SRCALPHA); hi.fill((255,255,255,40)); surf.blit(hi,(rx+2,ry+2))
        pygame.draw.rect(surf,(255,255,255,100),r,1,border_radius=self.rad)
        # Ripple
        if self._rip_r>0:
            tmp=pygame.Surface((self._rip_r*2,self._rip_r*2),pygame.SRCALPHA)
            pygame.draw.circle(tmp,(255,255,255,self._rip_a),(self._rip_r,self._rip_r),self._rip_r)
            surf.blit(tmp,(self._rip_cx-self._rip_r,self._rip_cy-self._rip_r))
        # Text
        lbl=f"{self.icon}  {self.text}" if self.icon else self.text
        t=self._font.render(lbl,True,self.tcol); surf.blit(t,t.get_rect(center=r.center))


# ════════════════════════════════════════════════════════════════════════════
#  O'YIN OB'EKTLARI
# ════════════════════════════════════════════════════════════════════════════

class Bullet:
    __slots__=("rect","spd","surf","vx","vy")
    def __init__(self,x,y,surf,spd=16,vx=0.0,vy=None):
        w,h=surf.get_size()
        self.rect=pygame.Rect(x-w//2,y,w,h); self.surf=surf; self.spd=spd
        self.vx=vx; self.vy=vy if vy is not None else -spd
    def update(self): self.rect.x+=int(self.vx); self.rect.y+=int(self.vy)
    @property
    def alive(self): return -40<self.rect.bottom and 0<self.rect.right and self.rect.left<SW
    def draw(self,s): s.blit(self.surf,self.rect.topleft)

class LaserBeam:
    __slots__=("x","y","life","ml","width","col")
    def __init__(self,x,y,width=8,col=YELLOW):
        self.x=x;self.y=y;self.life=8;self.ml=8;self.width=width;self.col=col
    def update(self): self.life-=1
    @property
    def alive(self): return self.life>0
    def draw(self,surf):
        ratio=self.life/self.ml; a=int(200*ratio); w=max(2,int(self.width*ratio))
        for gw in [w+8,w+4,w]:
            ga=a//3 if gw>w else a
            c2=WHITE if gw==w else self.col
            tmp=pygame.Surface((gw,SH-self.y),pygame.SRCALPHA); tmp.fill((*c2[:3],ga))
            surf.blit(tmp,(self.x-gw//2,self.y))

class EnemyBullet:
    __slots__=("rect","surf","vx","vy")
    def __init__(self,x,y,surf,vx=0.0,vy=9.0):
        w,h=surf.get_size()
        self.rect=pygame.Rect(x-w//2,y,w,h); self.surf=surf; self.vx=vx; self.vy=vy
    def update(self): self.rect.x+=int(self.vx); self.rect.y+=int(self.vy)
    @property
    def alive(self): return self.rect.top<SH+20 and 0<self.rect.right and self.rect.left<SW
    def draw(self,s): s.blit(self.surf,self.rect.topleft)

class Enemy:
    MOVES=["straight","zigzag","dive","swoop"]
    def __init__(self,x,y,surf,spd,hp=1,shoot=False,move="straight"):
        w,h=surf.get_size()
        self.rect=pygame.Rect(x,y,w,h); self._surf=surf; self.spd=spd
        self.hp=hp; self.max_hp=hp; self.shoot=shoot; self.move=move
        self._ang=random.uniform(0,math.tau); self._asp=random.uniform(0.04,0.09)
        self._stimer=random.randint(70,140); self._flash=0; self._alive=True
        self._sdir=random.choice([-1,1])
    @property
    def hitbox(self):
        m=7; return pygame.Rect(self.rect.x+m,self.rect.y+m,self.rect.w-m*2,self.rect.h-m*2)
    def update(self,ebullets,ebsurf):
        if self.move=="zigzag": self._ang+=self._asp; self.rect.x+=int(math.sin(self._ang)*3.0)
        elif self.move=="swoop": self._ang+=0.05; self.rect.x+=int(math.cos(self._ang)*2.5*self._sdir); self.rect.y+=int(self.spd)
        elif self.move=="dive": self.rect.y+=int(self.spd*1.3)
        else: self.rect.y+=int(self.spd)
        self.rect.x=max(10,min(SW-self.rect.w-10,self.rect.x))
        if self.shoot:
            self._stimer-=1
            if self._stimer<=0:
                self._stimer=random.randint(80,170)
                ebullets.append(EnemyBullet(self.rect.centerx,self.rect.bottom,ebsurf,vy=9))
        if self._flash>0: self._flash-=1
    def hit(self,dmg=1):
        self.hp-=dmg; self._flash=6
        if self.hp<=0: self._alive=False; return True
        return False
    @property
    def alive(self): return self._alive and self.rect.top<SH+10
    def draw(self,surf):
        if self._flash>0:
            surf.blit(self._surf,self.rect.topleft)
            fl=pygame.Surface(self._surf.get_size(),pygame.SRCALPHA)
            fl.fill((255,255,255,170)); surf.blit(fl,self.rect.topleft)
        else: surf.blit(self._surf,self.rect.topleft)
        if self.hp<self.max_hp:
            draw_hp_bar(surf,self.rect.x,self.rect.y-9,self.rect.w,5,self.hp/self.max_hp)

class BossEnemy:
    PHASE_ENTER="enter"; PHASE1="p1"; PHASE2="p2"; PHASE3="p3"; RAGE="rage"
    PATTERNS=["spread","triple","aimed","wave","spiral"]
    def __init__(self,surf,hp=120):
        w,h=surf.get_size()
        self.rect=pygame.Rect(SW//2-w//2,-h-20,w,h)
        self._surf=surf; self.max_hp=hp; self.hp=hp
        self.phase=self.PHASE_ENTER; self._ty=80; self._mx=2.0; self._md=1
        self._stimer=0; self._pidx=0; self._flash=0; self._alive=True; self._done=False
        self._ang=0.0
    @property
    def hitbox(self):
        m=14; return pygame.Rect(self.rect.x+m,self.rect.y+m,self.rect.w-m*2,self.rect.h-m*2)
    @property
    def hp_ratio(self): return max(0.0,self.hp/self.max_hp)
    def _check_phase(self):
        r=self.hp_ratio
        if self.phase==self.PHASE_ENTER: return
        if r>0.66: p=self.PHASE1
        elif r>0.33: p=self.PHASE2
        else: p=self.PHASE3
        if p!=self.phase and p!=self.PHASE_ENTER:
            self.phase=p
            if p==self.PHASE2: self._ty=140; self._mx=3.5
            elif p==self.PHASE3: self._ty=200; self._mx=5.0; self.phase=self.RAGE
    def update(self,ebullets,bsurf,t,pcx_list):
        if self.phase==self.PHASE_ENTER:
            if self.rect.y<self._ty: self.rect.y+=3
            else: self.phase=self.PHASE1; self._done=True
        self.rect.x+=int(self._mx*self._md)
        if self.rect.right>=SW-20: self._md=-1
        elif self.rect.left<=20: self._md=1
        self._ang+=0.02
        self.rect.y=int(self._ty+math.sin(self._ang*2)*22)
        self._check_phase()
        if self._done:
            cd=60 if self.phase!=self.RAGE else 32
            self._stimer-=1
            if self._stimer<=0:
                self._stimer=cd
                self._fire(ebullets,bsurf,pcx_list)
                self._pidx=(self._pidx+1)%len(self.PATTERNS)
        if self._flash>0: self._flash-=1
    def _fire(self,ebullets,surf,pcx_list):
        cx,cy=self.rect.centerx,self.rect.bottom
        pat=self.PATTERNS[self._pidx]
        pcx=pcx_list[0] if pcx_list else SW//2
        if pat=="spread":
            for ad in range(-60,61,30):
                rad=math.radians(ad+90); spd=6
                ebullets.append(EnemyBullet(cx,cy,surf,vx=math.cos(rad)*spd,vy=math.sin(rad)*spd))
        elif pat=="triple":
            for dx in [-60,0,60]: ebullets.append(EnemyBullet(cx+dx,cy,surf,vy=8))
        elif pat=="aimed":
            dx_=pcx-cx; dy_=SH-cy; dist=max(1,math.hypot(dx_,dy_)); spd=9
            vx=dx_/dist*spd; vy=dy_/dist*spd
            for ddx in [-20,0,20]: ebullets.append(EnemyBullet(cx+ddx,cy,surf,vx=vx*(0.8 if ddx else 1),vy=vy))
        elif pat=="wave":
            for i in range(5): ebullets.append(EnemyBullet(cx+i*25-50,cy,surf,vx=math.sin(i)*2,vy=7+i*0.5))
        elif pat=="spiral":
            for i in range(8):
                rad=math.radians(i*45); spd=7
                ebullets.append(EnemyBullet(cx,cy,surf,vx=math.cos(rad)*spd,vy=math.sin(rad)*spd+2))
    def hit(self,dmg=1):
        self.hp-=dmg; self._flash=5
        if self.hp<=0: self._alive=False; return True
        return False
    @property
    def alive(self): return self._alive
    def draw(self,surf,t):
        img=self._surf
        if self._flash>0:
            tmp=img.copy()
            fl=pygame.Surface(img.get_size(),pygame.SRCALPHA); fl.fill((255,255,255,200))
            tmp.blit(fl,(0,0)); surf.blit(tmp,self.rect.topleft)
        elif self.phase==self.RAGE:
            tmp=img.copy()
            ti=pygame.Surface(img.get_size(),pygame.SRCALPHA)
            ti.fill((255,0,0,int(80*pulse(t,5,0.3,1.0)))); tmp.blit(ti,(0,0)); surf.blit(tmp,self.rect.topleft)
        else: surf.blit(img,self.rect.topleft)
        bw=self.rect.w+40; bx=self.rect.centerx-bw//2; by_=self.rect.y-16
        draw_hp_bar(surf,bx,by_,bw,10,self.hp_ratio,bg=(60,10,10),bc=(200,100,255))
        f=pygame.font.SysFont("Arial",16,bold=True)
        lbl={self.PHASE1:"BOSS",self.PHASE2:"BOSS ⚡ FAZA-2",self.PHASE3:"BOSS 🔥 FAZA-3",self.RAGE:"BOSS 💢 QUTTIRIB"}.get(self.phase,"BOSS")
        t_=f.render(lbl,True,(255,100,255)); surf.blit(t_,t_.get_rect(center=(self.rect.centerx,by_-16)))

class PowerUp:
    def __init__(self,x,y,kind,surf):
        self.kind=kind; self._surf=surf
        sz=surf.get_width(); self.rect=pygame.Rect(x-sz//2,y,sz,sz)
        self._t=0
    def update(self): self.rect.y+=2; self._t+=1
    @property
    def alive(self): return self.rect.top<SH+10
    def draw(self,surf):
        sc=0.88+0.12*math.sin(self._t*0.08); sz=self._surf.get_width()
        nsz=max(8,int(sz*sc)); scaled=pygame.transform.smoothscale(self._surf,(nsz,nsz))
        cx=self.rect.centerx-nsz//2; cy=self.rect.centery-nsz//2
        CM={PU_SHIELD:(0,180,255),PU_DOUBLE:(255,220,0),PU_SLOW:(0,220,120),
            PU_LIFE:(255,60,100),PU_NUKE:(255,140,0),PU_SPEED:(80,255,80),PU_LASER:(255,80,200)}
        gc=CM.get(self.kind,(200,200,200))
        for gr in range(16,3,-4):
            gs=pygame.Surface((nsz+gr*2,nsz+gr*2),pygame.SRCALPHA)
            pygame.draw.circle(gs,(*gc,30),(nsz//2+gr,nsz//2+gr),nsz//2+gr)
            surf.blit(gs,(cx-gr,cy-gr))
        surf.blit(scaled,(cx,cy))


# ════════════════════════════════════════════════════════════════════════════
#  O'YINCHI (1-chi yoki 2-chi)
# ════════════════════════════════════════════════════════════════════════════

class Player:
    """
    control_mode: "keyboard" yoki "mouse"
    idx: 0 = P1 (ko'k, chapda), 1 = P2 (sariq, o'ngda)
    """
    def __init__(self, surf, idx=0, control_mode="keyboard"):
        self._surf      = surf
        self.idx        = idx
        self.ctrl       = control_mode
        w,h             = surf.get_size()
        # Boshlang'ich pozitsiya: 2 o'yinchi bo'lsa ular alohida joylarda
        self.rect       = pygame.Rect(SW//2 - w//2, SH-130, w, h)
        self.spd        = 6
        self.lives      = 3
        self.max_lives  = 5
        self.inv        = 0    # invincibility frames
        self.tilt       = 0.0
        self.last_shot  = 0
        self.shot_cd    = 150  # ms
        # Power-up timers (frames @ 60fps)
        self.shield_t = self.double_t = self.slow_t = self.speed_t = self.laser_t = 0
        self._smoke_t = 0
        self._ft = 0  # flame anim timer
        self._is_alive = True

    @property
    def hitbox(self):
        m=10; return pygame.Rect(self.rect.x+m,self.rect.y+m,self.rect.w-m*2,self.rect.h-m*2)

    @property
    def dead(self): return self.lives<=0

    def set_start_pos(self, lane_x):
        """Lane markaziga o'rnatish."""
        self.rect.centerx = lane_x
        self.rect.bottom  = SH - 80

    def update(self, keys, mouse_pos=None, mouse_buttons=None, zone_left=0, zone_right=SW):
        dx=0
        if self.ctrl=="keyboard":
            if self.idx==0:
                if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx=-1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx=1
            else:
                if keys[pygame.K_KP4]: dx=-1
                if keys[pygame.K_KP6]: dx=1
        elif self.ctrl=="mouse" and mouse_pos:
            # Sichqoncha holatiga yaqinlashish
            target_x = mouse_pos[0] - self.rect.width//2
            cur = self.rect.x
            diff = target_x - cur
            step = min(abs(diff), self.spd*(1.4 if self.speed_t>0 else 1.0))
            if abs(diff)>2:
                dx = 1 if diff>0 else -1
                self.rect.x += int(step * (1 if diff>0 else -1))
            dx = 0  # tilt hesoblash uchun

        if self.ctrl=="keyboard":
            spd = self.spd*(1.4 if self.speed_t>0 else 1.0)
            self.rect.x += int(dx*spd)

        self.rect.x = max(zone_left, min(zone_right - self.rect.w, self.rect.x))

        # Tilt
        if self.ctrl=="mouse" and mouse_pos:
            diff = mouse_pos[0] - self.rect.centerx
            tilt_t = clamp(diff/40,-1,1)*20
        else:
            tilt_t = dx*20.0
        self.tilt += (tilt_t - self.tilt)*0.15

        # Timers
        for attr in ("inv","shield_t","double_t","slow_t","speed_t","laser_t"):
            v=getattr(self,attr)
            if v>0: setattr(self,attr,v-1)
        self._ft+=1; self._smoke_t+=1

    def try_shoot(self, now_ms, bsurf):
        if now_ms - self.last_shot < self.shot_cd: return []
        self.last_shot=now_ms
        cx=self.rect.centerx; y=self.rect.top+8
        if self.laser_t>0: return [LaserBeam(cx,y,col=P1_COLOR if self.idx==0 else P2_COLOR)]
        if self.double_t>0:
            return [Bullet(cx-14,y,bsurf), Bullet(cx+14,y,bsurf)]
        return [Bullet(cx,y,bsurf)]

    def take_damage(self):
        if self.inv>0 or self.shield_t>0: return False
        self.lives-=1; self.inv=110; return True

    def apply_pu(self, kind):
        msgs = {
            PU_SHIELD:("🛡  Qalqon!",     lambda: setattr(self,"shield_t",360)),
            PU_DOUBLE:("⚡  Ikki o'q!",   lambda: setattr(self,"double_t",420)),
            PU_SLOW:  ("❄  Muzlatish!",  lambda: setattr(self,"slow_t",300)),
            PU_LIFE:  ("❤  +1 Jon!",     lambda: setattr(self,"lives",min(self.lives+1,self.max_lives))),
            PU_SPEED: ("🚀  Tez!",        lambda: setattr(self,"speed_t",300)),
            PU_LASER: ("🔥  LASER!",      lambda: setattr(self,"laser_t",240)),
        }
        item=msgs.get(kind)
        if item: item[1](); return item[0]
        return ""

    def draw(self, surf, t):
        if self.inv>0 and (self.inv//5)%2==0: return
        # Dvigatel alovi
        for dx_ in [-7,7]:
            fx=self.rect.centerx+dx_; fy=self.rect.bottom-4
            sz=int(14+6*abs(math.sin(t*0.3+dx_)))
            tmp=pygame.Surface((10,sz+2),pygame.SRCALPHA)
            pygame.draw.polygon(tmp,(*ORANGE,200),[(5,0),(0,sz+1),(10,sz+1)])
            pygame.draw.polygon(tmp,(*YELLOW,200),[(5,3),(2,sz*2//3+1),(8,sz*2//3+1)])
            surf.blit(tmp,(fx-5,fy))
        # Shield glow
        if self.shield_t>0:
            a=int(160*pulse(t,4,0.5,1.0)); r=self.rect.w//2+14
            cx_,cy_=self.rect.center
            tmp=pygame.Surface((r*2+10,r*2+10),pygame.SRCALPHA)
            pygame.draw.circle(tmp,(0,180,255,a),(r+5,r+5),r,3)
            pygame.draw.circle(tmp,(0,220,255,a//3),(r+5,r+5),r)
            surf.blit(tmp,(cx_-r-5,cy_-r-5))
        # Laser aura
        if self.laser_t>0:
            a=int(120*pulse(t,6,0.5,1.0)); cx_,cy_=self.rect.center
            tmp=pygame.Surface((80,80),pygame.SRCALPHA)
            pygame.draw.circle(tmp,(255,80,200,a),(40,40),36,2)
            surf.blit(tmp,(cx_-40,cy_-40))
        # Asosiy rasm (tilt)
        img=pygame.transform.rotate(self._surf,self.tilt)
        surf.blit(img,img.get_rect(center=self.rect.center))

    @property
    def should_smoke(self): return self._smoke_t%3==0
    def smoke_pos(self): return [(self.rect.centerx-9,self.rect.bottom-2),(self.rect.centerx+9,self.rect.bottom-2)]


# ════════════════════════════════════════════════════════════════════════════
#  SOUND ENGINE (Singleton)
# ════════════════════════════════════════════════════════════════════════════

class SoundEngine:
    _inst=None
    def __new__(cls):
        if not cls._inst: cls._inst=super().__new__(cls); cls._inst._ok=False
        return cls._inst

    def init(self,snds,sett):
        self._s=snds; self.sfx_vol=sett.get("sfx",0.7); self.mus_vol=sett.get("music",0.4)
        self.snd_on=sett.get("sound_on",True); self.mus_on=sett.get("music_on",True)
        self._set_vols(); self._bgch=None; self._ok=True; self._start_bg()

    def _set_vols(self):
        for n,s in self._s.items():
            if s: s.set_volume(self.sfx_vol*(0.5 if n in("shoot","shoot2","tick") else 0.8 if n in("explode","hit") else 0.95 if "big" in n or "boss" in n else 0.75))

    def play(self,name,vm=1.0):
        if not self.snd_on or not self._ok: return
        s=self._s.get(name)
        if s:
            try:
                ch=s.play()
                if ch and vm!=1.0: ch.set_volume(s.get_volume()*vm)
            except: pass

    def _start_bg(self):
        snd=gen_bg_music()
        if snd:
            snd.set_volume(self.mus_vol if self.mus_on else 0.0)
            try: self._bgch=snd.play(-1)
            except: pass

    def toggle_snd(self): self.snd_on=not self.snd_on
    def toggle_mus(self):
        self.mus_on=not self.mus_on
        if self._bgch:
            try: self._bgch.set_volume(self.mus_vol if self.mus_on else 0.0)
            except: pass
    def set_sfx(self,v): self.sfx_vol=clamp(v,0,1); self._set_vols()
    def set_mus(self,v):
        self.mus_vol=clamp(v,0,1)
        if self._bgch:
            try: self._bgch.set_volume(v if self.mus_on else 0.0)
            except: pass


# ════════════════════════════════════════════════════════════════════════════
#  ASOSIY O'YIN KLASSI
# ════════════════════════════════════════════════════════════════════════════

DIFF_CFGS={
    "Easy":   dict(bspd=2.5,shoot=False,zigzag=False,bhp=1,srate=32,smult=1.0,boss_hm=0.6),
    "Medium": dict(bspd=4.5,shoot=True, zigzag=False,bhp=1,srate=22,smult=1.5,boss_hm=1.0),
    "Hard":   dict(bspd=7.0,shoot=True, zigzag=True, bhp=2,srate=14,smult=2.0,boss_hm=1.5),
}
BOSS_INTERVAL=1000

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(44100,-16,2,512)

        self._settings=load_settings()
        self._hs=load_hs()
        self._difficulty="Medium"
        self._mode="1p"  # "1p" yoki "2p"

        flags=pygame.DOUBLEBUF|pygame.HWSURFACE
        if self._settings.get("fullscreen",False): flags|=pygame.FULLSCREEN
        self._screen=pygame.display.set_mode((SW,SH),flags)
        pygame.display.set_caption("✈  Samalyotcha O'yini  |  Ultimate Edition v3.0  |  by Ahrorazamatovich")

        # Icon
        try:
            ico=pygame.Surface((32,32),pygame.SRCALPHA)
            pygame.draw.polygon(ico,(60,160,255),[(16,2),(4,30),(16,24),(28,30)])
            pygame.display.set_icon(ico)
        except: pass

        self._clock=pygame.time.Clock()
        self._t=0

        # Assets
        self._build_assets()

        # Sound
        snd=SoundEngine()
        snd.init(self._sounds, self._settings)
        self._snd=snd

        # Fontlar
        self._fhuge=pygame.font.SysFont("Arial Black",80,bold=True)
        self._fbig =pygame.font.SysFont("Arial",48,bold=True)
        self._fmed =pygame.font.SysFont("Arial",30)
        self._fsml =pygame.font.SysFont("Arial",22)
        self._ftny =pygame.font.SysFont("Arial",16)
        self._fwave=pygame.font.SysFont("Arial Black",76,bold=True)

        # Yulduzlar
        self._stars=[Star(initial=True) for _ in range(160)]

        # Holat
        self._state=ST_SPLASH
        self._splash_t=0

        # O'yin o'zgaruvchilari
        self._players:list[Player]=[]
        self._enemies:list[Enemy]=[]
        self._bullets:list=[]
        self._ebullets:list=[]
        self._pups:list[PowerUp]=[]
        self._pm=ParticleMgr()
        self._smokes=[]
        self._boss:BossEnemy|None=None
        self._score=0
        self._p_scores=[0,0]
        self._wave=1
        self._wave_t=0
        self._espd=4.5
        self._spawn_t=0
        self._spawn_rate=22
        self._combo=0
        self._combo_t=0
        self._combo_max=0
        self._boss_active=False
        self._next_boss=BOSS_INTERVAL
        self._shake_t=0; self._shake_int=0
        self._road_y=0.0
        self._cfg=DIFF_CFGS["Medium"]
        self._msgs:list[dict]=[]

        # UI tugmalari (menyular uchun)
        self._build_menus()

    # ── ASSETS ────────────────────────────────────────────────────────────────

    def _build_assets(self):
        # Grafika
        self._p1_img = make_player_surf(col=P1_COLOR)
        self._p2_img = make_player_surf(col=P2_COLOR)
        self._envariant_surfs=[make_enemy_surf(*ct) for ct in ENEMY_VARIANTS]
        self._boss_surf=make_boss_surf()
        self._bsurf=make_bullet_surf()
        self._ebsurf=make_enemy_bullet_surf()
        self._bbsurf=make_boss_bullet_surf()
        self._pu_surfs={k:make_powerup_surf(k) for k in PU_ALL}

        # Ovozlar
        recipes={"shoot":gen_shoot,"shoot2":gen_shoot2,"laser":gen_laser,
                 "explode":gen_explode,"explode_big":gen_explode_big,
                 "powerup":gen_powerup,"hit":gen_hit,"boss_roar":gen_boss_roar,
                 "shield":gen_shield,"nuke":gen_nuke,"levelup":gen_levelup,
                 "tick":gen_tick,"combo":gen_combo,"victory":gen_victory}
        self._sounds={}
        for name,fn in recipes.items():
            try: self._sounds[name]=fn()
            except: self._sounds[name]=None

    # ── MENYULAR ────────────────────────────────────────────────────────────

    def _build_menus(self):
        cx=SW//2
        # Asosiy menyu
        self._mbts=[
            Button("O'YINNI BOSHLASH",(cx-210,310,420,56),col=(25,130,230),icon="▶"),
            Button("O'YINCHI SONI",   (cx-210,380,420,56),col=(130,30,200),icon="👥"),
            Button("QIYINLIK",        (cx-210,450,420,56),col=(190,120,0), icon="⚙"),
            Button("REKORDLAR",       (cx-210,520,420,56),col=(160,90,0),  icon="🏆"),
            Button("SOZLAMALAR",      (cx-210,590,420,56),col=(40,140,70), icon="🔧"),
            Button("CHIQISH",         (cx-210,660,420,56),col=(170,25,25), icon="✖"),
        ]
        # Rejim tanlash
        self._mode_bts=[
            Button("1 O'YINCHI   (Klaviatura)", (cx-250,320,500,65),col=(30,160,80)),
            Button("2 O'YINCHI   (P1:Klaviatura  P2:Sichqoncha)", (cx-250,402,500,65),col=(140,80,0)),
            Button("← ORQAGA",  (cx-180,500,360,50),col=GRAY,fsz=24),
        ]
        # Qiyinlik
        self._dbts=[
            Button("OSON",     (cx-220,310,440,65),col=(30,160,70)),
            Button("O'RTA",    (cx-220,392,440,65),col=(190,130,0)),
            Button("QIYIN",    (cx-220,474,440,65),col=(190,30,30)),
            Button("← ORQAGA",(cx-160,575,320,50),col=GRAY,fsz=24),
        ]
        # Pause
        self._pbts=[
            Button("▶ DAVOM ETISH",   (cx-200,310,400,56),col=(30,160,80)),
            Button("🔄 QAYTA BOSHLASH",(cx-200,380,400,56),col=(50,130,200)),
            Button("⬅ BOSH MENYU",    (cx-200,450,400,56),col=GRAY),
        ]
        # Gameover
        self._gobts=[
            Button("🔄 QAYTA BOSHLASH",(cx-200,490,400,56),col=(30,130,220)),
            Button("⬅ BOSH MENYU",    (cx-200,562,400,56),col=GRAY),
        ]
        # Rekordlar
        self._lbbts=[Button("← BOSH MENYU",(cx-180,610,360,50),col=GRAY,fsz=24)]
        # Sozlamalar
        self._sbts=[Button("← BOSH MENYU",(cx-180,630,360,50),col=GRAY,fsz=24)]
        # Sett toggle tugmalari
        self._sett_t_bts=[
            Button("SFX",    (cx+80,282,110,42),col=(40,130,200),fsz=22),
            Button("MUSIQA", (cx+80,348,130,42),col=(40,130,200),fsz=22),
            Button("FPS",    (cx+80,414,110,42),col=(40,130,200),fsz=22),
            Button("SCAN",   (cx+80,480,110,42),col=(40,130,200),fsz=22),
        ]
        self._dragging_sfx=False; self._dragging_mus=False

    # ── GAME RESET ────────────────────────────────────────────────────────────

    def _reset_game(self):
        cfg=DIFF_CFGS[self._difficulty]
        self._cfg=cfg
        self._score=0; self._p_scores=[0,0]
        self._enemies=[]; self._bullets=[]; self._ebullets=[]; self._pups=[]
        self._pm.clear(); self._smokes=[]; self._boss=None
        self._wave=1; self._wave_t=90; self._espd=cfg["bspd"]
        self._spawn_t=0; self._spawn_rate=cfg["srate"]
        self._combo=0; self._combo_t=0; self._combo_max=0
        self._boss_active=False; self._next_boss=BOSS_INTERVAL
        self._shake_t=0; self._shake_int=0; self._road_y=0.0
        self._msgs=[]

        # O'yinchilarni yaratish
        self._players=[]
        if self._mode=="1p":
            p=Player(self._p1_img, idx=0, control_mode="keyboard")
            p.set_start_pos(SW//2)
            self._players=[p]
        else:
            # 2 o'yinchi: chapda P1, o'ngda P2
            p1=Player(self._p1_img, idx=0, control_mode="keyboard")
            p2=Player(self._p2_img, idx=1, control_mode="mouse")
            # Har birining uchun yon zona
            p1.set_start_pos(SW//4)
            p2.set_start_pos(3*SW//4)
            self._players=[p1,p2]

        self._hs["sessions"]=self._hs.get("sessions",0)+1

    # ── SHAKE ─────────────────────────────────────────────────────────────────

    def _shake(self,i=8,d=12): self._shake_int=i; self._shake_t=d
    def _get_offset(self):
        if self._shake_t>0:
            s=int(self._shake_int*(self._shake_t/12))
            return (random.randint(-s,s),random.randint(-s,s))
        return (0,0)

    # ── XABAR ────────────────────────────────────────────────────────────────

    def _push_msg(self,text,col=YELLOW,dur=110):
        self._msgs.append({"text":text,"col":col,"t":dur,"mt":dur,"yo":0.0})
        if len(self._msgs)>4: self._msgs.pop(0)

    # ── SPAWN ─────────────────────────────────────────────────────────────────

    def _spawn_enemy(self):
        if self._boss_active: return
        cfg=self._cfg
        x=random.randint(180,SW-230)
        moves=["straight"]
        if cfg["zigzag"]: moves+=["zigzag","swoop"]
        if self._wave>3: moves.append("dive")
        move=random.choice(moves)
        hp=cfg["bhp"] if self._score>300 else 1
        if self._wave>5 and random.random()<0.2: hp+=1
        surf=random.choice(self._envariant_surfs)
        en=Enemy(x,-90,surf,self._espd*(0.75+random.random()*0.5),hp,
                 shoot=cfg["shoot"] and random.random()<0.35,move=move)
        self._enemies.append(en)

    def _maybe_pu(self,x,y):
        if random.random()<0.14:
            k=random.choices(PU_ALL,weights=PU_WEIGHTS)[0]
            self._pups.append(PowerUp(x,y,k,self._pu_surfs[k]))

    def _maybe_boss(self):
        if self._score>=self._next_boss and not self._boss_active:
            self._next_boss+=BOSS_INTERVAL
            self._boss_active=True; self._enemies.clear()
            hp=int(100*self._cfg["boss_hm"]*(1+self._wave*0.1))
            self._boss=BossEnemy(self._boss_surf,hp=hp)
            self._shake(12,22); self._snd.play("boss_roar")
            self._push_msg("💥  BOSS KELDI!",RED,200)
            self._wave_t=120

    # ── O'YIN MANTIQ ─────────────────────────────────────────────────────────

    def _update_game(self, events):
        keys=pygame.key.get_pressed()
        mp=pygame.mouse.get_pos()
        mb=pygame.mouse.get_pressed()

        # O'yinchilar
        for i,pl in enumerate(self._players):
            if pl.ctrl=="mouse":
                zone_l=SW//2 if self._mode=="2p" else 0
                zone_r=SW
                pl.update(keys,mouse_pos=mp,mouse_buttons=mb,zone_left=zone_l,zone_right=zone_r)
            else:
                zone_l=0
                zone_r=SW//2 if self._mode=="2p" else SW
                pl.update(keys,zone_left=zone_l,zone_right=zone_r)

        # Tutun
        for pl in self._players:
            if pl.should_smoke:
                for sx,sy in pl.smoke_pos():
                    self._smokes.append(SmokePart(sx,sy))

        # Otish
        now=pygame.time.get_ticks()
        for i,pl in enumerate(self._players):
            should_shoot=False
            if pl.ctrl=="keyboard":
                if pl.idx==0: should_shoot=keys[pygame.K_SPACE]
                else:          should_shoot=keys[pygame.K_KP0]
            else:
                should_shoot=mb[0]  # LMB
            if should_shoot:
                nbs=pl.try_shoot(now,self._bsurf)
                if nbs:
                    self._bullets.extend(nbs)
                    if isinstance(nbs[0],LaserBeam): self._snd.play("laser")
                    else: self._snd.play("shoot2" if pl.double_t>0 else "shoot")

        # O'qlar
        for b in self._bullets[:]:
            b.update()
            if not b.alive: self._bullets.remove(b)

        # Spawn
        if not self._boss_active:
            self._spawn_t+=1
            rate=max(6,self._spawn_rate-self._score//400)
            if self._spawn_t>=rate: self._spawn_t=0; self._spawn_enemy()

        # Dushmanlar
        for en in self._enemies[:]:
            en.update(self._ebullets,self._ebsurf)
            if not en.alive: self._enemies.remove(en)

        # Boss
        if self._boss:
            pcx=[p.rect.centerx for p in self._players]
            self._boss.update(self._ebullets,self._bbsurf,self._t,pcx)
            if not self._boss.alive:
                self._pm.explode(self._boss.rect.centerx,self._boss.rect.centery,power=2.5,mult=4)
                self._shake(22,35); pts=int(600*self._cfg["smult"])
                self._score+=pts
                self._push_msg(f"🏆  BOSS YUTILDI!  +{pts}",YELLOW,200)
                self._snd.play("explode_big"); self._snd.play("victory")
                for _ in range(4):
                    self._maybe_pu(self._boss.rect.centerx+random.randint(-70,70),self._boss.rect.centery)
                self._boss=None; self._boss_active=False; self._advance_wave()

        # Dushman o'qlari
        for eb in self._ebullets[:]:
            eb.update()
            if not eb.alive: self._ebullets.remove(eb); continue
            for pl in self._players:
                if pl.hitbox.colliderect(eb.rect):
                    try: self._ebullets.remove(eb)
                    except: pass
                    self._on_hit(pl); break

        # O'q vs dushman/boss to'qnashuvi
        for b in self._bullets[:]:
            if not b.alive: continue
            if isinstance(b,LaserBeam):
                lrect=pygame.Rect(b.x-b.width//2,b.y,b.width,SH)
                for en in self._enemies[:]:
                    if lrect.colliderect(en.hitbox): killed=en.hit(1); killed and self._on_kill(en)
                if self._boss and lrect.colliderect(self._boss.hitbox): self._boss.hit(2)
            else:
                hit=False
                for en in self._enemies[:]:
                    if b.rect.colliderect(en.hitbox):
                        if b in self._bullets: self._bullets.remove(b)
                        killed=en.hit(1); hit=True
                        killed and self._on_kill(en); break
                if not hit and self._boss and b in self._bullets:
                    if b.rect.colliderect(self._boss.hitbox):
                        self._bullets.remove(b); self._boss.hit(1)

        # Player vs enemy
        for pl in self._players:
            for en in self._enemies[:]:
                if en.hitbox.colliderect(pl.hitbox):
                    if pl.shield_t>0:
                        self._pm.explode(en.rect.centerx,en.rect.centery)
                        self._snd.play("explode"); self._enemies.remove(en); self._score+=5
                    else:
                        self._pm.explode(en.rect.centerx,en.rect.centery)
                        self._snd.play("explode"); self._enemies.remove(en); self._on_hit(pl)

        # Power-uplar
        for pu in self._pups[:]:
            pu.update()
            if not pu.alive: self._pups.remove(pu); continue
            for pl in self._players:
                if pu.rect.colliderect(pl.hitbox):
                    if pu.kind==PU_NUKE: self._nuke()
                    else:
                        msg=pl.apply_pu(pu.kind)
                        col=P1_COLOR if pl.idx==0 else P2_COLOR
                        self._push_msg(f"P{pl.idx+1}: {msg}",col,130)
                    try: self._pups.remove(pu)
                    except: pass
                    self._snd.play("powerup")
                    if pu.kind==PU_SHIELD: self._snd.play("shield")
                    break

        # Combo timer
        self._combo_t-=1
        if self._combo_t<=0:
            if self._combo>3: self._push_msg(f"Combo tugadi — x{self._combo}",ORANGE,70)
            self._combo=0

        # Wave progress
        if self._score>=self._wave*650 and not self._boss_active: self._advance_wave()
        self._maybe_boss()

        # Zarrachalar
        self._pm.update()
        self._smokes=[s for s in self._smokes if s.life>0]
        for s in self._smokes: s.update()

        if self._shake_t>0: self._shake_t-=1
        self._road_y+=self._espd*0.55
        if self._road_y>80: self._road_y-=80
        if self._wave_t>0: self._wave_t-=1

        # Xabarlar
        for msg in self._msgs:
            msg["t"]-=1; msg["yo"]-=0.4
        self._msgs=[m for m in self._msgs if m["t"]>0]

        # O'yinchi o'lgan?
        alive_players=[p for p in self._players if not p.dead]
        if not alive_players:
            return "gameover"
        return None

    def _on_kill(self,en:Enemy):
        self._pm.explode(en.rect.centerx,en.rect.centery)
        self._snd.play("explode"); self._shake(4,6)
        pts=int({"Easy":10,"Medium":15,"Hard":25}.get(self._difficulty,10)*self._cfg["smult"])
        self._combo+=1; self._combo_t=90
        if self._combo>2:
            pts=int(pts*(1+self._combo*0.1)); self._snd.play("combo")
            if self._combo>self._combo_max: self._combo_max=self._combo
        self._score+=pts; self._espd=DIFF_CFGS[self._difficulty]["bspd"]+self._score*0.002
        if self._enemies and en in self._enemies: self._enemies.remove(en)
        self._maybe_pu(en.rect.centerx,en.rect.centery)

    def _on_hit(self,pl:Player):
        hit=pl.take_damage()
        if hit:
            self._snd.play("hit"); self._shake(12,18)
            if not pl.dead:
                col=P1_COLOR if pl.idx==0 else P2_COLOR
                self._push_msg(f"P{pl.idx+1}: ❤ {pl.lives} jon qoldi!",col,90)

    def _nuke(self):
        pts=0
        for en in self._enemies[:]: self._pm.explode(en.rect.centerx,en.rect.centery); pts+=int(10*self._cfg["smult"])
        self._enemies.clear(); self._ebullets.clear()
        self._score+=pts; self._shake(28,38); self._snd.play("nuke")
        self._push_msg("💣  NUKE — BARCHA DUSHMANLAR YO'Q!",ORANGE,180)

    def _advance_wave(self):
        self._wave+=1; self._wave_t=120
        self._spawn_rate=max(6,self._cfg["srate"]-self._wave*2)
        self._espd+=0.4; self._snd.play("levelup")
        self._push_msg(f"🌊  TO'LQIN #{self._wave}",CYAN,140)

    # ── DRAW ─────────────────────────────────────────────────────────────────

    def _draw_game(self,surf):
        ox,oy=self._get_offset()
        draw_grad(surf,BG_TOP,BG_BOT,pygame.Rect(0,0,SW,SH))
        for s in self._stars: s.update(self._espd/5.0); s.draw(surf,self._t)

        # Yo'l
        self._draw_road(surf,ox,oy)

        # 2p rejimda divider
        if self._mode=="2p":
            div_x=SW//2+ox
            pygame.draw.line(surf,(80,80,100),(div_x,0),(div_x,SH),2)
            p1_lbl=self._fsml.render("P1  ← Klaviatura",True,P1_COLOR)
            p2_lbl=self._fsml.render("Sichqoncha →  P2",True,P2_COLOR)
            surf.blit(p1_lbl,(20,64)); surf.blit(p2_lbl,(SW-p2_lbl.get_width()-20,64))

        # Tutun
        for sm in self._smokes: sm.draw(surf)

        # Power-uplar
        for pu in self._pups: pu.draw(surf)

        # Dushmanlar
        for en in self._enemies: en.draw(surf)

        # Dushman o'qlari
        for eb in self._ebullets: eb.draw(surf)

        # Boss
        if self._boss: self._boss.draw(surf,self._t)

        # O'yinchilar
        for pl in self._players: pl.draw(surf,self._t)

        # O'yinchi o'qlari
        for b in self._bullets: b.draw(surf)

        # Zarrachalar
        self._pm.draw(surf)

        # Scanlines
        if self._settings.get("scanlines",False):
            sc_surf=pygame.Surface((SW,SH),pygame.SRCALPHA)
            for y in range(0,SH,3): pygame.draw.line(sc_surf,(0,0,0,18),(0,y),(SW,y))
            surf.blit(sc_surf,(0,0))

        # Wave announce
        if self._wave_t>0: self._draw_wave_banner(surf)

        # HUD
        self._draw_hud(surf)

    def _draw_road(self,surf,ox,oy):
        rw=580
        if self._mode=="2p": rw=SW-80
        rx=(SW-rw)//2+ox
        pygame.draw.rect(surf,ROAD_COL,(rx,oy,rw,SH))
        pygame.draw.rect(surf,ROAD_EDGE,(rx,oy,8,SH))
        pygame.draw.rect(surf,ROAD_EDGE,(rx+rw-8,oy,8,SH))
        lh,gap=52,28; total=lh+gap
        offset=int(self._road_y)%total
        lane_count=4 if self._mode=="2p" else 3
        for i in range(1,lane_count):
            lx=rx+rw*i//lane_count
            for y in range(-total+offset,SH+total,total):
                pygame.draw.rect(surf,ROAD_LINE,(lx-2+ox,y+oy,4,lh))

    def _draw_wave_banner(self,surf):
        ratio=self._wave_t/120; alpha=int(255*min(1,ratio*2)*min(1,(1-ratio)*4+0.5))
        sc=0.6+0.4*(1-abs(ratio-0.5)*2)
        cx=SW//2
        if self._boss_active: txt=self._fwave.render("⚠  BOSS!",True,RED)
        else: txt=self._fwave.render(f"TO'LQIN  #{self._wave}",True,CYAN)
        w=max(1,int(txt.get_width()*sc)); h=max(1,int(txt.get_height()*sc))
        sc_t=pygame.transform.smoothscale(txt,(w,h)); sc_t.set_alpha(alpha)
        surf.blit(sc_t,sc_t.get_rect(center=(cx,SH//2)))

    def _draw_hud(self,surf):
        # Yuqori bar
        ov=pygame.Surface((SW,58),pygame.SRCALPHA); ov.fill((0,0,16,210))
        surf.blit(ov,(0,0)); pygame.draw.line(surf,CYAN,(0,58),(SW,58),2)

        # Ochko
        sc_t=self._fmed.render(f"✦ {self._score:,}",True,YELLOW)
        surf.blit(sc_t,(20,14))

        # Tezlik va wave (markazda)
        ct=self._fsml.render(f"TEZLIK {self._espd:.1f}x  |  TO'LQIN #{self._wave}",True,LGRAY)
        surf.blit(ct,ct.get_rect(center=(SW//2,28)))

        # O'yinchi jonlari (yuqori o'ng)
        hfont=pygame.font.SysFont("Segoe UI Emoji",24)
        for pi,pl in enumerate(self._players):
            col=P1_COLOR if pi==0 else P2_COLOR
            lbl=self._fsml.render(f"P{pi+1}:",True,col)
            surf.blit(lbl,(SW-260+pi*130,14))
            for i in range(5):
                hc=col if i<pl.lives else DGRAY
                ht=hfont.render("♥",True,hc)
                surf.blit(ht,(SW-240+pi*130+i*24,16))

        # Power-up indikatorlar
        py_=64
        all_inds=[]
        for pi,pl in enumerate(self._players):
            col=P1_COLOR if pi==0 else P2_COLOR
            pref=f"P{pi+1}"
            if pl.shield_t>0: all_inds.append((f"{pref} 🛡{pl.shield_t//60+1}s",CYAN,pl.shield_t/360))
            if pl.double_t>0: all_inds.append((f"{pref} ⚡{pl.double_t//60+1}s",YELLOW,pl.double_t/420))
            if pl.slow_t>0:   all_inds.append((f"{pref} ❄{pl.slow_t//60+1}s",GREEN,pl.slow_t/300))
            if pl.speed_t>0:  all_inds.append((f"{pref} 🚀{pl.speed_t//60+1}s",(80,255,80),pl.speed_t/300))
            if pl.laser_t>0:  all_inds.append((f"{pref} 🔥{pl.laser_t//60+1}s",MAGENTA,pl.laser_t/240))
        for idx,(txt,col,ratio) in enumerate(all_inds):
            x_=12+idx*118; y_=py_
            bg=pygame.Surface((108,32),pygame.SRCALPHA); bg.fill((0,0,0,160))
            pygame.draw.rect(bg,col,(0,0,108,32),1,border_radius=6)
            surf.blit(bg,(x_,y_))
            draw_hp_bar(surf,x_+2,y_+26,104,4,ratio,bg=(20,20,20),fc=col,bc=col,r=2)
            it=self._fsml.render(txt,True,col); surf.blit(it,(x_+5,y_+6))

        # Combo
        if self._combo>=3:
            a=int(255*pulse(self._t,6,0.7,1.0))
            ct2=self._fmed.render(f"x{self._combo}  COMBO!",True,ORANGE)
            ct2.set_alpha(a); surf.blit(ct2,ct2.get_rect(center=(SW//2,SH-70)))

        # Boss bar
        if self._boss:
            bw=SW-80; bx=40; by_=64; bh=20
            pan=pygame.Surface((bw+20,bh+14),pygame.SRCALPHA)
            pan.fill((10,0,20,200)); pygame.draw.rect(pan,(200,50,255),(0,0,bw+20,bh+14),2,border_radius=10)
            surf.blit(pan,(bx-10,by_-5))
            draw_hp_bar(surf,bx,by_,bw,bh,self._boss.hp_ratio,bg=(40,0,60),fc=(200,0,255),bc=(255,100,255),r=8)
            bt=self._fsml.render(f"BOSS  {self._boss.hp}/{self._boss.max_hp}",True,(255,200,255))
            surf.blit(bt,bt.get_rect(center=(bx+bw//2,by_+bh//2)))

        # Xabarlar
        cx=SW//2
        for msg in self._msgs:
            ratio=msg["t"]/msg["mt"]; alpha=min(255,int(ratio*500))
            sc_=0.7+0.3*min(1.0,(msg["mt"]-msg["t"])/10)
            mt=self._fmed.render(msg["text"],True,msg["col"])
            sz=(max(1,int(mt.get_width()*sc_)),max(1,int(mt.get_height()*sc_)))
            smt=pygame.transform.smoothscale(mt,sz); smt.set_alpha(alpha)
            surf.blit(smt,smt.get_rect(center=(cx,SH//2+80+msg["yo"])))

        # Pastki
        _mlbl = "2P" if self._mode=="2p" else "1P"
        mode_lbl=self._ftny.render(f"[{self._difficulty}]  |  {_mlbl}",True,(80,80,80))
        surf.blit(mode_lbl,(8,SH-20))
        ctrl_lbl=self._ftny.render("ESC=Pauza  |  P1:SPACE=O'q  |  P2:LMB=O'q" if self._mode=="2p" else "ESC=Pauza  |  SPACE=O'q",True,(60,60,60))
        surf.blit(ctrl_lbl,ctrl_lbl.get_rect(midright=(SW-8,SH-20)))
        if self._settings.get("fps_show",False):
            ft=self._ftny.render(f"FPS:{self._clock.get_fps():.0f}",True,(100,100,100))
            surf.blit(ft,(SW-68,SH-36))

    # ════════════════════════════════════════════════════════════════════════
    #  MENYULAR
    # ════════════════════════════════════════════════════════════════════════

    def _draw_bg(self,surf):
        draw_grad(surf,BG_TOP,BG_BOT,pygame.Rect(0,0,SW,SH))
        for s in self._stars: s.update(0.6); s.draw(surf,self._t)

    def _menu(self,events):
        surf=self._screen; mp=pygame.mouse.get_pos()
        self._draw_bg(surf)
        cx=SW//2
        # Animatsiyali sarlavha
        sc=pulse(self._t,1.8,0.97,1.03)
        ttl=self._fhuge.render("✈  SAMALYOTCHA",True,YELLOW)
        st=pygame.transform.smoothscale(ttl,(int(ttl.get_width()*sc),int(ttl.get_height()*sc)))
        surf.blit(st,st.get_rect(center=(cx,120)))
        s2=self._fbig.render("O ' Y I N I",True,CYAN); surf.blit(s2,s2.get_rect(center=(cx,204)))
        au=self._fsml.render("by  Ahrorazamatovich",True,(140,140,170)); surf.blit(au,au.get_rect(center=(cx,244)))
        dc={"Easy":GREEN,"Medium":YELLOW,"Hard":RED}.get(self._difficulty,WHITE)
        _mode_lbl = "2 o'yinchi" if self._mode=="2p" else "1 o'yinchi"
        df=self._fsml.render(f"Qiyinlik: {self._difficulty}   |   Rejim: {_mode_lbl}",True,dc)
        surf.blit(df,df.get_rect(center=(cx,274)))
        hs=max(self._hs.get(self._difficulty,0),self._hs.get("coop",0) if self._mode=="2p" else 0)
        ht=self._fsml.render(f"🏆  Rekord: {hs:,}",True,YELLOW); surf.blit(ht,ht.get_rect(center=(cx,296)))

        for btn in self._mbts: btn.update(mp); btn.draw(surf)
        for e in events:
            if self._mbts[0].event(e): self._reset_game(); return ST_PLAYING
            if self._mbts[1].event(e): return ST_MODE_SEL
            if self._mbts[2].event(e): return ST_DIFFICULTY
            if self._mbts[3].event(e): return ST_LEADERBOARD
            if self._mbts[4].event(e): return ST_SETTINGS
            if self._mbts[5].event(e):
                save_hs(self._hs); save_settings(self._settings)
                pygame.quit(); sys.exit()
        return None

    def _mode_sel(self,events):
        surf=self._screen; mp=pygame.mouse.get_pos()
        self._draw_bg(surf)
        cx=SW//2
        ttl=self._fbig.render("O'YINCHI SONINI TANLANG",True,WHITE); surf.blit(ttl,ttl.get_rect(center=(cx,230)))
        descs=[
            "WASD / Strelkalar — harakatlanish   |   SPACE — o'q otish",
            "P1: Klaviatura   •   P2: Sichqoncha harakati + LMB (chap tugma) — o'q",
        ]
        for i,(btn,desc) in enumerate(zip(self._mode_bts[:2],descs)):
            btn.update(mp); btn.draw(surf)
            ds=self._fsml.render(desc,True,(140,140,160))
            surf.blit(ds,ds.get_rect(center=(cx,312+82*i+46)))
        self._mode_bts[2].update(mp); self._mode_bts[2].draw(surf)
        for e in events:
            if self._mode_bts[0].event(e): self._mode="1p"; return ST_MENU
            if self._mode_bts[1].event(e): self._mode="2p"; return ST_MENU
            if self._mode_bts[2].event(e): return ST_MENU
        return None

    def _difficulty_scr(self,events):
        surf=self._screen; mp=pygame.mouse.get_pos()
        self._draw_bg(surf); cx=SW//2
        ttl=self._fbig.render("QIYINLIK TANLANG",True,WHITE); surf.blit(ttl,ttl.get_rect(center=(cx,230)))
        descs=[("OSON","Sekin,  o'q yo'q,  oddiy",GREEN),("O'RTA","O'rtacha,  dushman o'q otadi",YELLOW),("QIYIN","Tez,  zigzag,  ko'p HP,  agressiv Boss",RED)]
        for i,btn in enumerate(self._dbts[:3]):
            btn.update(mp); btn.draw(surf)
            d=self._fsml.render(descs[i][1],True,descs[i][2])
            surf.blit(d,d.get_rect(center=(cx,318+82*i+46)))
        self._dbts[3].update(mp); self._dbts[3].draw(surf)
        for e in events:
            if self._dbts[0].event(e): self._difficulty="Easy";   return ST_MENU
            if self._dbts[1].event(e): self._difficulty="Medium"; return ST_MENU
            if self._dbts[2].event(e): self._difficulty="Hard";   return ST_MENU
            if self._dbts[3].event(e): return ST_MENU
        return None

    def _paused_scr(self,events):
        surf=self._screen; mp=pygame.mouse.get_pos()
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,24,170)); surf.blit(ov,(0,0))
        cx=SW//2
        pan=pygame.Rect(cx-250,250,500,320)
        tmp=pygame.Surface(pan.size,pygame.SRCALPHA); tmp.fill((10,10,36,240))
        pygame.draw.rect(tmp,CYAN,(0,0,*pan.size),2,border_radius=20); surf.blit(tmp,pan.topleft)
        ttl=self._fbig.render("⏸  PAUZA",True,WHITE); surf.blit(ttl,ttl.get_rect(center=(cx,290)))
        for btn in self._pbts: btn.update(mp); btn.draw(surf)
        for e in events:
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: return "resume"
            if self._pbts[0].event(e): return "resume"
            if self._pbts[1].event(e): self._reset_game(); return ST_PLAYING
            if self._pbts[2].event(e): return ST_MENU
        return None

    def _gameover_scr(self,events,is_new_hs,old_hs):
        surf=self._screen; mp=pygame.mouse.get_pos()
        draw_grad(surf,(20,0,10),(50,5,5),pygame.Rect(0,0,SW,SH))
        self._pm.update(); self._pm.draw(surf)
        cx=SW//2; sc_v=pulse(self._t,2,0.95,1.05)
        pan=pygame.Rect(cx-300,180,600,400)
        tmp=pygame.Surface(pan.size,pygame.SRCALPHA); tmp.fill((10,0,0,220))
        pygame.draw.rect(tmp,RED,(0,0,*pan.size),3,border_radius=24); surf.blit(tmp,pan.topleft)
        ttl=self._fhuge.render("💥 GAME OVER",True,RED)
        st_=pygame.transform.smoothscale(ttl,(int(ttl.get_width()*sc_v),int(ttl.get_height()*sc_v)))
        surf.blit(st_,st_.get_rect(center=(cx,240)))
        st_=self._fbig.render(f"Ochkolar:  {self._score:,}",True,WHITE); surf.blit(st_,st_.get_rect(center=(cx,320)))
        if is_new_hs:
            hs_sc=pulse(self._t,4,0.8,1.0)
            hr=self._fbig.render("🏆  YANGI REKORD!",True,YELLOW)
            hr_s=pygame.transform.smoothscale(hr,(int(hr.get_width()*hs_sc),int(hr.get_height()*hs_sc)))
            surf.blit(hr_s,hr_s.get_rect(center=(cx,375)))
        else:
            hr=self._fsml.render(f"Rekord:  {old_hs:,}",True,LGRAY); surf.blit(hr,hr.get_rect(center=(cx,375)))
        dc={"Easy":GREEN,"Medium":YELLOW,"Hard":RED}.get(self._difficulty,WHITE)
        _rlbl = "2P" if self._mode=="2p" else "1P"
        df=self._fsml.render(f"Qiyinlik:  {self._difficulty}  |  Rejim: {_rlbl}",True,dc)
        surf.blit(df,df.get_rect(center=(cx,415)))
        ms=("AJOYIB! Siz haqiqiy usta!" if self._score>=5000 else
            "Yaxshi o'yin!" if self._score>=2000 else
            "Ko'proq mashq qiling!" if self._score>=500 else "Boshidan boshlang!")
        mt=self._ftny.render(ms,True,(130,130,150)); surf.blit(mt,mt.get_rect(center=(cx,450)))
        for btn in self._gobts: btn.update(mp); btn.draw(surf)
        for e in events:
            if self._gobts[0].event(e): self._reset_game(); return ST_PLAYING
            if self._gobts[1].event(e): return ST_MENU
        return None

    def _leaderboard_scr(self,events):
        surf=self._screen; mp=pygame.mouse.get_pos()
        self._draw_bg(surf); cx=SW//2
        ttl=self._fbig.render("🏆  REKORDLAR TAXTASI",True,YELLOW); surf.blit(ttl,ttl.get_rect(center=(cx,140)))
        rows=[("Easy",GREEN,"⭐"),("Medium",YELLOW,"⭐⭐"),("Hard",RED,"⭐⭐⭐"),("COOP (2P)",CYAN,"🤝")]
        for i,(lbl,col,stars) in enumerate(rows):
            key="coop" if "COOP" in lbl else lbl
            val=self._hs.get(key,0); y=230+i*90
            pr=pygame.Rect(cx-280,y,560,80)
            tmp=pygame.Surface(pr.size,pygame.SRCALPHA); tmp.fill((15,15,40,200))
            pygame.draw.rect(tmp,col,(0,0,*pr.size),2,border_radius=14); surf.blit(tmp,pr.topleft)
            st=self._fsml.render(stars,True,col); surf.blit(st,(pr.x+18,y+12))
            nl=self._fmed.render(lbl.upper(),True,WHITE); surf.blit(nl,(pr.x+18,y+42))
            vt=self._fbig.render(f"{val:,}",True,col); surf.blit(vt,vt.get_rect(midright=(pr.right-20,y+40)))
        ss=self._ftny.render(f"Jami o'yinlar:  {self._hs.get('sessions',0)}",True,(80,80,100))
        surf.blit(ss,ss.get_rect(center=(cx,600)))
        for btn in self._lbbts: btn.update(mp); btn.draw(surf)
        for e in events:
            if self._lbbts[0].event(e): return ST_MENU
        return None

    def _settings_scr(self,events):
        surf=self._screen; mp=pygame.mouse.get_pos()
        self._draw_bg(surf); cx=SW//2
        ttl=self._fbig.render("SOZLAMALAR",True,WHITE); surf.blit(ttl,ttl.get_rect(center=(cx,160)))
        rows=[("SFX Ovoz","sound_on",282,0),("Musiqa","music_on",348,1),
              ("FPS Ko'rsatish","fps_show",414,2),("Scanlines","scanlines",480,3)]
        snd=SoundEngine()
        for lbl,key,y,bi in rows:
            lt=self._fmed.render(lbl,True,LGRAY); surf.blit(lt,(cx-260,y+6))
            active=self._settings.get(key,False)
            col=(0,200,255) if active else DGRAY
            pygame.draw.circle(surf,col,(cx+40,y+18),9)
            self._sett_t_bts[bi].col=(0,200,80) if active else GRAY
            self._sett_t_bts[bi].update(mp); self._sett_t_bts[bi].draw(surf)
        # SFX slayder
        sy=240; sw_=260; sx=cx-260
        sfx_r=pygame.Rect(sx,sy,sw_,8)
        pygame.draw.rect(surf,DGRAY,sfx_r,border_radius=4)
        fw_=int(sw_*self._settings.get("sfx",0.7))
        pygame.draw.rect(surf,CYAN,(sx,sy,fw_,8),border_radius=4)
        pygame.draw.circle(surf,WHITE,(sx+fw_,sy+4),9)
        lbl_s=self._fsml.render(f"SFX: {int(self._settings.get('sfx',0.7)*100)}%",True,LGRAY); surf.blit(lbl_s,(cx-260,220))
        # Musiqa slayder
        my=308; msr=pygame.Rect(sx,my,sw_,8)
        pygame.draw.rect(surf,DGRAY,msr,border_radius=4)
        mw_=int(sw_*self._settings.get("music",0.4))
        pygame.draw.rect(surf,CYAN,(sx,my,mw_,8),border_radius=4)
        pygame.draw.circle(surf,WHITE,(sx+mw_,my+4),9)
        lbl_m=self._fsml.render(f"Musiqa: {int(self._settings.get('music',0.4)*100)}%",True,LGRAY); surf.blit(lbl_m,(cx-260,288))

        for btn in self._sbts: btn.update(mp); btn.draw(surf)
        for e in events:
            if self._sett_t_bts[0].event(e): self._settings["sound_on"]=not self._settings["sound_on"]; snd.toggle_snd()
            if self._sett_t_bts[1].event(e): self._settings["music_on"]=not self._settings["music_on"]; snd.toggle_mus()
            if self._sett_t_bts[2].event(e): self._settings["fps_show"]=not self._settings.get("fps_show",False)
            if self._sett_t_bts[3].event(e): self._settings["scanlines"]=not self._settings.get("scanlines",False)
            if e.type==pygame.MOUSEBUTTONDOWN:
                if sfx_r.collidepoint(e.pos): self._dragging_sfx=True
                if msr.collidepoint(e.pos):   self._dragging_mus=True
            if e.type==pygame.MOUSEBUTTONUP:
                self._dragging_sfx=False; self._dragging_mus=False
            if e.type==pygame.MOUSEMOTION:
                if self._dragging_sfx:
                    v=clamp((mp[0]-sx)/sw_,0,1); self._settings["sfx"]=v; snd.set_sfx(v)
                if self._dragging_mus:
                    v=clamp((mp[0]-sx)/sw_,0,1); self._settings["music"]=v; snd.set_mus(v)
            if self._sbts[0].event(e): save_settings(self._settings); return ST_MENU
        return None

    def _splash(self,events):
        surf=self._screen
        draw_grad(surf,BG_TOP,BG_BOT,pygame.Rect(0,0,SW,SH))
        for s in self._stars: s.update(0.5); s.draw(surf,self._t)
        cx=SW//2; ratio=min(1.0,self._splash_t/80)
        alpha=int(255*ratio)
        ttl=self._fhuge.render("✈  SAMALYOTCHA",True,YELLOW)
        sub=self._fbig.render("ULTIMATE PROFESSIONAL EDITION  v3.0",True,CYAN)
        au=self._fmed.render("by  Ahrorazamatovich",True,LGRAY)
        pr=self._fsml.render("Yuklanmoqda...",True,GRAY)
        for t_,y in [(ttl,240),(sub,340),(au,400),(pr,480)]:
            t_.set_alpha(alpha); surf.blit(t_,t_.get_rect(center=(cx,y)))
        self._splash_t+=1
        if self._splash_t>120:
            for e in events:
                if e.type in(pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN): return ST_MENU
            if self._splash_t>200: return ST_MENU
        return None

    # ════════════════════════════════════════════════════════════════════════
    #  ASOSIY HALQA
    # ════════════════════════════════════════════════════════════════════════

    def run(self):
        _gameover_state={"is_new":False,"old_hs":0}
        while True:
            self._clock.tick(FPS)
            self._t+=1
            events=pygame.event.get()
            for e in events:
                if e.type==pygame.QUIT:
                    save_hs(self._hs); save_settings(self._settings)
                    pygame.quit(); sys.exit()
                if e.type==pygame.KEYDOWN and e.key==pygame.K_F11:
                    self._settings["fullscreen"]=not self._settings.get("fullscreen",False)
                    flags=pygame.DOUBLEBUF|pygame.HWSURFACE
                    if self._settings["fullscreen"]: flags|=pygame.FULLSCREEN
                    self._screen=pygame.display.set_mode((SW,SH),flags)

            result=None
            if   self._state==ST_SPLASH:     result=self._splash(events)
            elif self._state==ST_MENU:        result=self._menu(events)
            elif self._state==ST_MODE_SEL:    result=self._mode_sel(events)
            elif self._state==ST_DIFFICULTY:  result=self._difficulty_scr(events)
            elif self._state==ST_SETTINGS:    result=self._settings_scr(events)
            elif self._state==ST_LEADERBOARD: result=self._leaderboard_scr(events)
            elif self._state==ST_PAUSED:
                # Avval o'yin sahnasini ko'rsatamiz
                self._draw_game(self._screen)
                result=self._paused_scr(events)
                if result=="resume": result=ST_PLAYING
            elif self._state==ST_PLAYING:
                gr=self._update_game(events)
                self._draw_game(self._screen)
                if gr=="gameover":
                    hs_key="coop" if self._mode=="2p" else self._difficulty
                    old=self._hs.get(hs_key,0)
                    is_new=self._score>old
                    if is_new: self._hs[hs_key]=self._score
                    save_hs(self._hs)
                    _gameover_state={"is_new":is_new,"old_hs":old}
                    result=ST_GAMEOVER
                else:
                    for e in events:
                        if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                            result=ST_PAUSED
            elif self._state==ST_GAMEOVER:
                result=self._gameover_scr(events,_gameover_state["is_new"],_gameover_state["old_hs"])

            if result: self._state=result
            pygame.display.flip()


# ════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__=="__main__":
    game=Game()
    game.run()
