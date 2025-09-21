import random
import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard

WIDTH, HEIGHT = 800, 600
GRAVITY, JUMP_STRENGTH = 0.5, -12

class GameState:
    MENU, PLAYING = 0, 1
    state, music_on, sound_on = MENU, True, True

class Hero:
    def __init__(self, x, y):
        self.actor = Actor('hero_idle_1', (x, y))
        self.actor.scale = 0.7
        self.vx = self.vy = 0
        self.on_ground = False
        self.anim_frames = {
            'idle': [f'hero_idle_{i}' for i in range(1, 7)],
            'walk-left': [f'hero_walk_left_{i}' for i in range(1, 7)],
            'walk-right': [f'hero_walk_right_{i}' for i in range(1, 7)],
            'jump': [f'hero_jump_{i}' for i in range(1, 7)]
        }
        self.anim_state, self.anim_index, self.anim_timer = 'idle', 0, 0
        self.anim_speed, self.width, self.height = 0.1, 24, 36

    def update(self, dt):
        self.vx = -5 if keyboard.left else 5 if keyboard.right else 0
        self.anim_state = self._get_anim_state()
        if keyboard.space and self.on_ground:
            self.vy, self.on_ground = JUMP_STRENGTH, False
            if GameState.sound_on:
                sounds.jump.play()
        self.vy += GRAVITY
        # Clamp hero position within screen bounds
        self.actor.x = max(self.width / 2, min(WIDTH - self.width / 2,
                                               self.actor.x + self.vx))
        self.actor.y = max(self.height / 2, min(HEIGHT - self.height / 2,
                                                self.actor.y + self.vy))
        self._update_animation(dt)

    def _get_anim_state(self):
        """Determine animation state based on movement and ground status."""
        if keyboard.left:
            return 'walk-left'
        if keyboard.right:
            return 'walk-right'
        return 'idle' if self.on_ground else 'jump'

    def _update_animation(self, dt):
        """Cycle through animation frames based on current state."""
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            frames = self.anim_frames[self.anim_state]
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.actor.image = frames[self.anim_index]
            self.anim_timer = 0

    def collides_with(self, x, y, w, h):
        """Check if hero collides with a rectangle (x, y, w, h)."""
        return (abs(self.actor.x - x) < (self.width + w) / 2 and
                abs(self.actor.y - y) < (self.height + h) / 2)

    def draw(self):
        self.actor.draw()

class Enemy:
    def __init__(self, x, y, start, end):
        self.actor = Actor('enemy_idle_1', (x, y))
        self.vx = random.choice([-1.5, 1.5])
        self.patrol_start, self.patrol_end = start, end
        self.anim_frames = {
            'idle': [f'enemy_idle_{i}' for i in range(1, 7)],
            'walk-right': [f'enemy_walk_right_{i}' for i in range(1, 7)],
            'walk-left': [f'enemy_walk_left_{i}' for i in range(1, 7)]
        }
        self.anim_state = 'walk-right' if self.vx > 0 else 'walk-left'
        self.anim_index, self.anim_timer = 0, 0
        self.anim_speed, self.width, self.height = 0.15, 32, 32

    def update(self, dt):
        self.actor.x += self.vx
        # Reverse direction if enemy reaches patrol boundaries
        if self.actor.x <= self.patrol_start or self.actor.x >= self.patrol_end:
            self.vx = -self.vx
            self.anim_state = 'walk-right' if self.vx > 0 else 'walk-left'
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            frames = self.anim_frames[self.anim_state]
            self.anim_index = (self.anim_index + 1) % len(frames)
            self.actor.image = frames[self.anim_index]
            self.anim_timer = 0

    def draw(self):
        self.actor.draw()

class Platform:
    def __init__(self, x, y, w, h, img='platform'):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.actor = Actor(img, (x, y))
        self.actor.scale = min(w / self.actor.width, h / self.actor.height)

    def draw(self):
        self.actor.pos = (self.x, self.y)
        self.actor.draw()

class Trophy:
    def __init__(self, x, y):
        self.actor = Actor('trophy', (x, y))
        self.actor.scale = 0.5
        self.width, self.height = 20, 20

    def draw(self):
        self.actor.draw()

class Game:
    def __init__(self):
        self.hero = Hero(50, 500)
        self.trophy = Trophy(770, 120 - 36)
        self.platforms = [
            Platform(400, 550, 800, 50, 'platform_ground'),
            Platform(210, 450, 160, 20), Platform(380, 340, 160, 20),
            Platform(550, 230, 160, 20), Platform(770, 120, 160, 20)
        ]
        self.enemies = [
            Enemy(300, 500, 0, 800), Enemy(500, 500, 0, 800),
            Enemy(210, 450 - 26, 130, 290), Enemy(380, 340 - 26, 300, 460),
            Enemy(550, 230 - 26, 470, 630), Enemy(490, 230 - 26, 470, 630)
        ]
        self.buttons = [
            Actor('button_start', (WIDTH // 2, HEIGHT // 2 - 75)),
            Actor('btn_music_on' if GameState.music_on else 'btn_music_off',
                  (50, 35)),
            Actor('btn_sounds_on' if GameState.sound_on else 'btn_sounds_off',
                  (125, 35)),
            Actor('button_exit', (WIDTH // 2, HEIGHT // 2 + 75))
        ]
        self.background = Actor('background', topleft=(0, 0))
        self.menu_background = Actor('menu_background', topleft=(0, 0))
        self.controls_image = Actor('controls_mapping', topleft=(600, 50))
        if GameState.music_on:
            music.play('background_music')

    def reset_game(self):
        self.hero = Hero(50, 500)
        self.trophy = Trophy(770, 120 - 26)
        self.platforms = [
            Platform(400, 550, 800, 50, 'platform_ground'),
            Platform(210, 450, 160, 20), Platform(380, 340, 160, 20),
            Platform(550, 230, 160, 20), Platform(770, 120, 160, 20)
        ]
        self.enemies = [
            Enemy(300, 500, 0, 800), Enemy(500, 500, 0, 800),
            Enemy(210, 450 - 26, 130, 290), Enemy(380, 340 - 26, 300, 460),
            Enemy(550, 230 - 26, 470, 630), Enemy(490, 230 - 26, 470, 630)
        ]
        if GameState.music_on:
            music.play('background_music')

    def update(self):
        if GameState.state == GameState.PLAYING:
            self.hero.update(1 / 60)
            self.hero.on_ground = False
            # Check platform collisions to support hero
            for p in self.platforms:
                if (self.hero.collides_with(p.x, p.y, p.width, p.height) and
                        self.hero.vy > 0 and self.hero.actor.y < p.y):
                    self.hero.actor.y = p.y - p.height / 2 - self.hero.height / 2
                    self.hero.vy, self.hero.on_ground = 0, True
            # Check enemy collisions to reset game
            for e in self.enemies:
                e.update(1 / 60)
                if self.hero.collides_with(e.actor.x, e.actor.y, e.width, e.height):
                    if GameState.sound_on:
                        sounds.collision.play()
                    GameState.state = GameState.MENU
                    self.hero.actor.pos = (100, 500)
            # Check trophy collision to win
            if self.hero.collides_with(self.trophy.actor.x, self.trophy.actor.y,
                                      self.trophy.width, self.trophy.height):
                if GameState.sound_on:
                    sounds.win.play()
                print("You won!")
                GameState.state = GameState.MENU

    def draw(self):
        screen.clear()
        if GameState.state == GameState.MENU:
            self.menu_background.draw()
            self.controls_image.draw()
            for b in self.buttons:
                b.draw()
        else:
            self.background.draw()
            for p in self.platforms:
                p.draw()
            self.hero.draw()
            self.trophy.draw()
            for e in self.enemies:
                e.draw()

def update():
    game.update()

def draw():
    game.draw()

def on_mouse_down(pos):
    if GameState.state == GameState.MENU:
        for b in game.buttons:
            if b.collidepoint(pos):
                if b.image == 'button_start':
                    game.reset_game()
                    GameState.state = GameState.PLAYING
                elif b.image in ['btn_music_on', 'btn_music_off']:
                    GameState.music_on = not GameState.music_on
                    music.play('background_music') if GameState.music_on else music.stop()
                    b.image = 'btn_music_on' if GameState.music_on else 'btn_music_off'
                elif b.image in ['btn_sounds_on', 'btn_sounds_off']:
                    GameState.sound_on = not GameState.sound_on
                    b.image = 'btn_sounds_on' if GameState.sound_on else 'btn_sounds_off'
                elif b.image == 'button_exit':
                    exit()

game = Game()
pgzrun.go()