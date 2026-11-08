import pygame
import random
import math
import array

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# ==============================
# AUDIO GENERATOR (SYNTHESIZER)
# ==============================

def generate_tone(frequency, duration, volume=0.3, wave_type="sine"):
    """Menghasilkan Sound object Pygame secara terprogram"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        if wave_type == "sine":
            val = math.sin(2.0 * math.pi * frequency * t)
        elif wave_type == "square":
            val = 1.0 if math.sin(2.0 * math.pi * frequency * t) >= 0 else -1.0
        elif wave_type == "sawtooth":
            val = 2.0 * (t * frequency - math.floor(0.5 + t * frequency))
        elif wave_type == "noise":
            val = random.uniform(-1, 1)
        else:
            val = math.sin(2.0 * math.pi * frequency * t)
        
        envelope = min(1.0, (n_samples - i) / (sample_rate * 0.01))
        sample = int(val * 32767 * volume * envelope)
        buf.append(sample)
        buf.append(sample)
        
    return pygame.mixer.Sound(buffer=buf)

# Membuat Efek Suara (SFX)
paddle_hit_sfx = generate_tone(523.25, 0.06, volume=0.35, wave_type="square")   # Suara C5
block_hit_sfx = generate_tone(1046.50, 0.08, volume=0.4, wave_type="sine")      # Suara C6
life_lost_sfx = generate_tone(130.81, 0.4, volume=0.5, wave_type="sawtooth")    # Suara C3 drop

# Musik Latar Rame & Enerjik (Fast Arcade Synthwave with Beat)
def generate_upbeat_music():
    sample_rate = 44100
    bpm = 140  # Tempo lebih cepat & lebih asik
    beat_duration = 60.0 / bpm
    total_beats = 16
    total_samples = int(sample_rate * beat_duration * total_beats)
    buf = array.array('h')
    
    # Scale: A minor pentatonic / Chords (Am - F - C - G)
    bass_notes = [110, 110, 87.31, 87.31, 130.81, 130.81, 98, 98]
    lead_arps = [
        440, 523.25, 659.25, 880, 659.25, 523.25, 440, 523.25,
        349.23, 440, 523.25, 698.46, 523.25, 440, 349.23, 440,
        523.25, 659.25, 783.99, 1046.5, 783.99, 659.25, 523.25, 659.25,
        392, 493.88, 587.33, 783.99, 587.33, 493.88, 392, 493.88
    ]
    
    for i in range(total_samples):
        t = float(i) / sample_rate
        beat_idx = int(t / beat_duration) % total_beats
        sub_beat = int((t / (beat_duration / 2)) % len(lead_arps))
        
        # 1. Kick Drum (setiap beat)
        beat_phase = (t % beat_duration) / beat_duration
        kick_freq = max(40, 150 * (1 - beat_phase * 4)) if beat_phase < 0.25 else 0
        kick_val = math.sin(2.0 * math.pi * kick_freq * t) if kick_freq > 0 else 0
        
        # 2. Snare Noise (pada beat ke-2 dan ke-4)
        snare_val = 0
        if beat_idx % 2 == 1 and beat_phase < 0.15:
            snare_val = random.uniform(-1, 1) * (1 - beat_phase / 0.15)
        
        # 3. Bass synth
        freq_bass = bass_notes[(beat_idx // 2) % len(bass_notes)]
        bass_val = 1.0 if math.sin(2.0 * math.pi * freq_bass * t) >= 0 else -1.0
        
        # 4. Fast Lead Arpeggio
        freq_lead = lead_arps[sub_beat]
        lead_val = math.sin(2.0 * math.pi * freq_lead * t)
        
        # Campur semua instrumen
        mix = (kick_val * 0.3) + (snare_val * 0.15) + (bass_val * 0.15) + (lead_val * 0.15)
        sample = int(mix * 32767)
        buf.append(sample)
        buf.append(sample)
        
    bg_sound = pygame.mixer.Sound(buffer=buf)
    return bg_sound

bg_music = generate_upbeat_music()
bg_music.play(loops=-1)

# ==============================
# SCREEN SETTINGS
# ==============================

WIDTH, HEIGHT = 800, 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NEON BLOCK BREAKER")

clock = pygame.time.Clock()
FPS = 60

# ==============================
# COLORS
# ==============================

BLACK = (10, 10, 25)
WHITE = (255, 255, 255)

RED = (255, 70, 70)
ORANGE = (255, 150, 50)
YELLOW = (255, 230, 70)
GREEN = (50, 255, 130)
BLUE = (50, 180, 255)
PURPLE = (180, 80, 255)
CYAN = (0, 255, 255)

BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, CYAN]

# ==============================
# FONTS
# ==============================

font = pygame.font.Font(None, 30)
bigFont = pygame.font.Font(None, 65)
smallFont = pygame.font.Font(None, 22)

# ==============================
# BACKGROUND STARS
# ==============================

stars = []
for i in range(80):
    stars.append([
        random.randint(0, WIDTH),
        random.randint(0, HEIGHT),
        random.randint(1, 3)
    ])

def drawBackground():
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(
            screen,
            (70, 80, 120),
            (star[0], star[1]),
            star[2]
        )

# ==============================
# PARTICLE EFFECT
# ==============================

particles = []

def createParticles(x, y, color):
    for i in range(12):
        particles.append({
            "x": x,
            "y": y,
            "dx": random.uniform(-4, 4),
            "dy": random.uniform(-4, 4),
            "life": 30,
            "color": color
        })

def updateParticles():
    for particle in particles[:]:
        particle["x"] += particle["dx"]
        particle["y"] += particle["dy"]
        particle["life"] -= 1

        if particle["life"] <= 0:
            particles.remove(particle)
        else:
            pygame.draw.circle(
                screen,
                particle["color"],
                (int(particle["x"]), int(particle["y"])),
                3
            )

# ==============================
# STRIKER CLASS
# ==============================

class Striker:
    def __init__(self, posx, posy, width, height, speed, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.speed = speed
        self.color = color
        self.strikerRect = pygame.Rect(posx, posy, width, height)

    def display(self):
        # Baris di bawah ini sudah diperbaiki dan disambung menjadi satu baris utuh
        glow = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
        
        pygame.draw.rect(
            glow,
            (*self.color, 60),
            (5, 5, self.width + 10, self.height + 10),
            border_radius=10
        )
        screen.blit(glow, (self.posx - 10, self.posy - 10))
        pygame.draw.rect(screen, self.color, self.strikerRect, border_radius=8)

    def update(self, xFac):
        self.posx += self.speed * xFac
        if self.posx <= 0:
            self.posx = 0
        elif self.posx + self.width >= WIDTH:
            self.posx = WIDTH - self.width
        self.strikerRect = pygame.Rect(self.posx, self.posy, self.width, self.height)

    def getRect(self):
        return self.strikerRect

# ==============================
# BLOCK CLASS
# ==============================

class Block:
    def __init__(self, posx, posy, width, height, color):
        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height
        self.color = color
        self.damage = 100

        # Daya tahan balok bervariasi berdasarkan warna
        if color == WHITE:
            self.health = 200
        elif color == CYAN:
            self.health = 300
        else:
            self.health = 100

        self.blockRect = pygame.Rect(posx, posy, width, height)

    def display(self):
        if self.health > 0:
            pygame.draw.rect(screen, self.color, self.blockRect, border_radius=5)
            # Balok lebih tebal jika health > 100
            border_thick = 2 if self.health > 100 else 1
            pygame.draw.rect(screen, WHITE, self.blockRect, border_thick, border_radius=5)

    def hit(self):
        self.health -= self.damage
        if self.health <= 0:
            createParticles(
                self.posx + self.width // 2,
                self.posy + self.height // 2,
                self.color
            )

    def getRect(self):
        return self.blockRect

    def getHealth(self):
        return self.health

# ==============================
# BALL CLASS
# ==============================

class Ball:
    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.color = color
        self.xFac = 1
        self.yFac = -1

    def display(self):
        pygame.draw.circle(
            screen,
            (60, 100, 150),
            (int(self.posx), int(self.posy)),
            self.radius + 5
        )
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.posx), int(self.posy)),
            self.radius
        )

    def update(self):
        self.posx += self.xFac * self.speed
        self.posy += self.yFac * self.speed

        if self.posx - self.radius <= 0:
            self.xFac = abs(self.xFac)
        elif self.posx + self.radius >= WIDTH:
            self.xFac = -abs(self.xFac)

        if self.posy - self.radius <= 0:
            self.yFac = abs(self.yFac)

        if self.posy - self.radius >= HEIGHT:
            return True

        return False

    def reset(self):
        self.posx = WIDTH // 2
        self.posy = HEIGHT - 100
        self.xFac = random.choice([-1, 1])
        self.yFac = -1

    def hit(self):
        self.yFac *= -1

    def getRect(self):
        return pygame.Rect(
            self.posx - self.radius,
            self.posy - self.radius,
            self.radius * 2,
            self.radius * 2
        )

# ==============================
# HELPER FUNCTIONS
# ==============================

def collisionChecker(rect, ball):
    return rect.colliderect(ball)

def populateBlocksIrregular():
    """Menghasilkan tata letak balok acak dan tidak beraturan"""
    listOfBlocks = []
    possible_widths = [40, 55, 75, 90]
    blockHeight = 22
    gap = 8

    # Generate 7 baris balok dengan offset dan celah acak
    for row in range(7):
        y = 60 + row * (blockHeight + gap)
        x = 30 + (row % 2) * 15 # Offsetting baris secara zig-zag
        
        while x < WIDTH - 40:
            w = random.choice(possible_widths)
            if x + w > WIDTH - 30:
                w = (WIDTH - 30) - x

            # Ada peluang 20% tempat ini dikosongkan (celah tidak beraturan)
            if random.random() > 0.20 and w >= 30:
                color = random.choice(BLOCK_COLORS)
                listOfBlocks.append(Block(x, y, w, blockHeight, color))
            
            x += w + gap

    return listOfBlocks

# ==============================
# HUD
# ==============================

def drawHUD(score, lives, level):
    pygame.draw.rect(screen, (20, 25, 50), (0, HEIGHT - 50, WIDTH, 50))
    scoreText = font.render(f"SCORE : {score}", True, CYAN)
    livesText = font.render(f"LIVES : {lives}", True, RED)
    levelText = font.render(f"LEVEL : {level}", True, GREEN)

    screen.blit(scoreText, (30, HEIGHT - 38))
    screen.blit(livesText, (330, HEIGHT - 38))
    screen.blit(levelText, (650, HEIGHT - 38))

# ==============================
# GAME OVER
# ==============================

def gameOver(score):
    while True:
        screen.fill(BLACK)
        title = bigFont.render("GAME OVER", True, RED)
        scoreText = font.render(f"FINAL SCORE : {score}", True, WHITE)
        restartText = font.render("PRESS SPACE TO RESTART", True, CYAN)
        quitText = smallFont.render("PRESS ESC TO QUIT", True, WHITE)

        screen.blit(title, title.get_rect(center=(WIDTH // 2, 200)))
        screen.blit(scoreText, scoreText.get_rect(center=(WIDTH // 2, 280)))
        screen.blit(restartText, restartText.get_rect(center=(WIDTH // 2, 360)))
        screen.blit(quitText, quitText.get_rect(center=(WIDTH // 2, 410)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False

# ==============================
# MAIN GAME
# ==============================

def main():
    running = True

    lives = 3
    score = 0
    level = 1

    striker = Striker(WIDTH // 2 - 60, HEIGHT - 80, 120, 15, 9, CYAN)
    strikerXFac = 0
    ball = Ball(WIDTH // 2, HEIGHT - 100, 9, 5, WHITE)

    listOfBlocks = populateBlocksIrregular()

    # ==========================
    # GAME LOOP
    # =================
    while running:
        drawBackground()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    strikerXFac = -1
                if event.key == pygame.K_RIGHT:
                    strikerXFac = 1
                if event.key == pygame.K_ESCAPE:
                    running = False
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    strikerXFac = 0

        # Game over
        if lives <= 0:
            if gameOver(score):
                lives = 3
                score = 0
                level = 1
                particles.clear()
                ball.speed = 5
                ball.reset()
                listOfBlocks = populateBlocksIrregular()
            else:
                running = False
            continue

        # All blocks destroyed
        if not listOfBlocks:
            level += 1
            ball.speed += 1
            listOfBlocks = populateBlocksIrregular()

        # Collision with striker
        if collisionChecker(striker.getRect(), ball.getRect()):
            paddle_hit_sfx.play()
            ball.yFac = -abs(ball.yFac)

            hitPosition = ball.posx - (striker.posx + striker.width / 2)
            ball.xFac = hitPosition / (striker.width / 2)
            ball.xFac = max(-1, min(1, ball.xFac))
            if ball.xFac == 0:
                ball.xFac = 0.1

        # Collision with blocks
        for block in listOfBlocks[:]:
            if collisionChecker(block.getRect(), ball.getRect()):
                block_hit_sfx.play()
                ball.hit()
                block.hit()

                if block.getHealth() <= 0:
                    listOfBlocks.remove(block)
                    score += 10
                break

        # Update
        striker.update(strikerXFac)
        lifeLost = ball.update()

        if lifeLost:
            life_lost_sfx.play()
            lives -= 1
            ball.reset()

        # Display
        for block in listOfBlocks:
            block.display()

        striker.display()
        ball.display()
        updateParticles()

        drawHUD(score, lives, level)

        pygame.display.update()
        clock.tick(FPS)

    bg_music.stop()
    pygame.quit()

# ==============================
# START GAME
# ==============================

if __name__ == "__main__":
    main()