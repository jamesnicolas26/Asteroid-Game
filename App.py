import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
SPACESHIP_COLOR = (0, 255, 0)
ASTEROID_COLOR = (169, 169, 169)
BULLET_COLOR = (255, 255, 0)
SPACESHIP_SIZE = 20
ASTEROID_SIZE = 30
BULLET_SIZE = 5
ASTEROID_SPEED = 0.2  # Significantly slower asteroids
BULLET_SPEED = 1      # Significantly slower bullets
SPACESHIP_SPEED = 0.05 # Significantly slower spaceship
ROTATION_SPEED = 1     # Slower rotation
FPS = 60
INITIAL_ASTEROIDS = 5
NEW_ASTEROID_INTERVAL = 5000  # New asteroid every 5 seconds

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Asteroids')

# Helper functions
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def wrap_position(position, width, height):
    return pygame.math.Vector2(position.x % width, position.y % height)

def distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def random_position():
    return pygame.math.Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

def random_velocity(speed=1.0):
    angle = random.uniform(0, 2 * math.pi)
    return pygame.math.Vector2(math.cos(angle), math.sin(angle)) * speed

# Classes
class Spaceship:
    def __init__(self):
        self.position = pygame.math.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        self.angle = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.lives = 3
        self.invincible = False
        self.invincibility_timer = 0

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.angle += ROTATION_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.angle -= ROTATION_SPEED * dt
        if keys[pygame.K_UP]:
            # Accelerate in the direction the spaceship is facing
            direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
            self.velocity += direction * SPACESHIP_SPEED * dt

        self.position += self.velocity
        self.position = wrap_position(self.position, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.velocity *= 0.98  # Friction

        if self.invincible:
            self.invincibility_timer += dt
            if self.invincibility_timer > 2000:  # 2 seconds of invincibility
                self.invincible = False
                self.invincibility_timer = 0

    def draw(self, surface):
        angle_radians = math.radians(self.angle)
        cos_a = math.cos(angle_radians)
        sin_a = math.sin(angle_radians)
        points = [
            (self.position.x + cos_a * SPACESHIP_SIZE, self.position.y - sin_a * SPACESHIP_SIZE),
            (self.position.x - sin_a * SPACESHIP_SIZE / 2, self.position.y - cos_a * SPACESHIP_SIZE / 2),
            (self.position.x + sin_a * SPACESHIP_SIZE / 2, self.position.y + cos_a * SPACESHIP_SIZE / 2)
        ]
        color = (255, 255, 255) if self.invincible else SPACESHIP_COLOR
        pygame.draw.polygon(surface, color, points)

class Asteroid:
    def __init__(self):
        self.position = random_position()
        self.velocity = random_velocity(ASTEROID_SPEED)
        self.size = ASTEROID_SIZE

    def update(self, dt):
        self.position += self.velocity * dt
        self.position = wrap_position(self.position, SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, ASTEROID_COLOR, (int(self.position.x), int(self.position.y)), self.size)

class Bullet:
    def __init__(self, position, angle):
        self.position = pygame.math.Vector2(position)
        self.velocity = pygame.math.Vector2(1, 0).rotate(-angle) * BULLET_SPEED

    def update(self, dt):
        self.position += self.velocity * dt
        self.position = wrap_position(self.position, SCREEN_WIDTH, SCREEN_HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.position.x), int(self.position.y)), BULLET_SIZE)

# Game loop
def main():
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)

    spaceship = Spaceship()
    asteroids = [Asteroid() for _ in range(INITIAL_ASTEROIDS)]
    bullets = []

    score = 0
    game_over = False
    last_asteroid_time = pygame.time.get_ticks()

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    # Fire bullet
                    bullets.append(Bullet(spaceship.position, spaceship.angle))
                if event.key == pygame.K_RETURN and game_over:
                    # Restart the game
                    spaceship = Spaceship()
                    asteroids = [Asteroid() for _ in range(INITIAL_ASTEROIDS)]
                    bullets = []
                    score = 0
                    game_over = False

        if not game_over:
            spaceship.update(dt)

            for asteroid in asteroids:
                asteroid.update(dt)
                if not spaceship.invincible and distance(spaceship.position, asteroid.position) < SPACESHIP_SIZE + asteroid.size:
                    spaceship.lives -= 1
                    spaceship.invincible = True
                    if spaceship.lives <= 0:
                        game_over = True

            for bullet in bullets[:]:
                bullet.update(dt)
                for asteroid in asteroids[:]:
                    if distance(bullet.position, asteroid.position) < BULLET_SIZE + asteroid.size:
                        asteroids.remove(asteroid)
                        bullets.remove(bullet)
                        score += 10
                        break

            # Add new asteroids over time
            if pygame.time.get_ticks() - last_asteroid_time > NEW_ASTEROID_INTERVAL:
                asteroids.append(Asteroid())
                last_asteroid_time = pygame.time.get_ticks()

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        spaceship.draw(screen)
        for asteroid in asteroids:
            asteroid.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        draw_text(f"Score: {score}", font, (255, 255, 255), screen, 70, 20)
        draw_text(f"Lives: {spaceship.lives}", font, (255, 255, 255), screen, SCREEN_WIDTH - 70, 20)

        if game_over:
            draw_text("Game Over", font, (255, 0, 0), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text("Press Enter to Restart", font, (255, 255, 255), screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)

        pygame.display.flip()

if __name__ == "__main__":
    main()
