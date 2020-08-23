import pygame
import random

pygame.init()
WIDTH, HEIGHT = (750, 750)
WHITE = (255, 255, 255)
BLACK = (20, 18, 18)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 255)

bg = pygame.transform.scale(pygame.image.load("assets/background-black.png"), (WIDTH, HEIGHT))
blue_ship = pygame.image.load("assets/pixel_ship_blue_small.png")
green_ship = pygame.image.load("assets/pixel_ship_green_small.png")
red_ship = pygame.image.load("assets/pixel_ship_red_small.png")
yellow_ship = pygame.image.load("assets/pixel_ship_yellow.png")
yellow_laser = pygame.image.load("assets/pixel_laser_yellow.png")
red_laser = pygame.image.load("assets/pixel_laser_red.png")
green_laser = pygame.image.load("assets/pixel_laser_green.png")
blue_laser = pygame.image.load("assets/pixel_laser_blue.png")
background_music = pygame.mixer.Sound("assets/feel_the_beat_cropped.wav")
shoot_effect = pygame.mixer.Sound("assets/bullet.wav")
font = pygame.font.Font('freesansbold.ttf', 20)
bg_rect = bg.get_rect()

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
SONG_END = pygame.USEREVENT + 1
pygame.display.set_caption('Starships')

enemies = []
clock = pygame.time.Clock()
enemy_images = [blue_ship, green_ship, red_ship]
enemy_lasers = [blue_laser, green_laser, red_laser]
level = 1
life = 3
score = 0
FPS = 60
lost = False


class Ship:
    def __init__(self, xcord, ycord, health):
        self.x = xcord
        self.y = ycord
        self.img = None
        self.laser = None
        self.lasers = []
        self.health = health
        self.VEL = 15

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def shoot(self):
        missile = Laser(self.x, self.y, self.laser)
        pygame.mixer.Channel(1).play(missile.fire_sound)
        self.lasers.append(missile)

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()


class Player(Ship):
    def __init__(self, xcord, ycord, health):
        super().__init__(xcord, ycord, health)
        self.img = yellow_ship
        self.mask = pygame.mask.from_surface(self.img)
        self.laser = yellow_laser
        self.max_health = 100

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def move_lasers(self, objects):
        global score
        for missile in self.lasers:
            for obj in objects:
                if missile.collide(obj):
                    if missile in self.lasers:
                        self.lasers.remove(missile)
                    enemies.remove(obj)
                    score += obj.score

            if missile.y < -50 and missile in self.lasers:
                self.lasers.remove(missile)
            missile.draw(SCREEN)
            missile.move(missile.VEL)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.img.get_height() + 10, self.img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.img.get_height() + 10, self.img.get_width() * (self.health / self.max_health), 10))

    def hit(self, damage):
        if self.health - damage > 0:
            self.health -= damage
        else:
            self.health = 0


class Enemy(Ship):
    def __init__(self, xcord, ycord, health, image, laser):
        super().__init__(xcord, ycord, health)
        self.img = image
        self.mask = pygame.mask.from_surface(self.img)
        self.laser = laser
        self.VEL = 5
        self.score = 10
        self.damage_inflict = 10

    def draw(self, window):
        super().draw(window)

    def move(self):
        global life
        self.y += self.VEL
        if self.y > WIDTH:
            enemies.remove(self)
            lose_life(1)

    def move_lasers(self, user):
        for missile in self.lasers:
            if missile.collide(user):
                if missile in self.lasers:
                    self.lasers.remove(missile)
                user.hit(self.damage_inflict)

            if missile.y > WIDTH + 50 and missile in self.lasers:
                self.lasers.remove(missile)
            missile.draw(SCREEN)
            missile.move(-missile.VEL)


class Laser:
    def __init__(self, xcord, ycord, image):
        self.x = xcord
        self.y = ycord
        self.img = image
        self.mask = pygame.mask.from_surface(image)
        self.lasers = []
        self.VEL = 20
        self.fire_sound = shoot_effect

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, velocity):
        self.y -= velocity

    def collide(self, obj):
        return collide(self, obj)


def lose_life(damage):
    global life
    if life - damage > 0:
        life -= damage
    else:
        life = 0


def collide(object1, object2):
    offset_x = object2.x - object1.x
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) is not None


def create_enemies(level):
    while len(enemies) < level * 5:
        x = random.randint(100, WIDTH - 100)
        y = random.randint(-200, -50)
        image = random.choice(enemy_images)
        laser = enemy_lasers[enemy_images.index(image)]
        obj = Enemy(x, y, 100, image, laser)
        enemies.append(obj)


def reset():
    global level, life, score, lost, player, enemies
    level = 1
    life = 3
    score = 0
    lost = False
    enemies = []
    player = Player(375, 600, 100)


def main():
    global level, score, life, player
    player = Player(375, 600, 100)
    pygame.mixer.Channel(0).play(background_music)
    pygame.mixer.Channel(0).set_endevent(SONG_END)
    background_music.set_volume(0.15)
    shoot_effect.set_volume(0.05)
    while True:
        # Pygame system controls
        ########################

        # Setting the frame rate of the game
        clock.tick(FPS)

        # Check for quit events in the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == SONG_END:
                pygame.mixer.Channel(0).play(background_music)

        # Check for keyed events in the game
        ####################################
        keys = pygame.key.get_pressed()

        # Check for user inputs validate boundary values
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= player.VEL
        if keys[pygame.K_RIGHT] and player.x + player.get_width() < WIDTH:
            player.x += player.VEL
        if keys[pygame.K_UP] and player.y > 0:
            player.y -= player.VEL
        if keys[pygame.K_DOWN] and player.y + player.get_height() < HEIGHT:
            player.y += player.VEL
        if keys[pygame.K_SPACE]:
            player.shoot()

        # Creation of the gui components
        ################################
        lives = font.render(f"Lives: {life}", True, WHITE, BLACK)
        levels = font.render(f"Level: {level}", True, WHITE, BLACK)
        scores = font.render(f"Score: {score}", True, WHITE, BLACK)

        create_enemies(level)

        # Game mechanics for all the objects in the game
        ###############################################
        # Game settings
        if 0 <= score < 1000:
            level = 1
        elif 1000 <= score < 2000:
            level = 2
        else:
            level = 3

        # Winning conditions
        if life == 0 or player.health == 0:
            pygame.mixer.Channel(0).stop()
            break

        # Enemy mechanics
        for enemy in enemies:
            enemy.move()
            if random.randint(0, 120) == 1:
                enemy.shoot()
            if collide(player, enemy):
                player.hit(enemy.damage_inflict)
                if enemy in enemies:
                    enemies.remove(enemy)
        # Drawing all the objects to the screen
        #######################################
        # Background
        SCREEN.blit(bg, (0, 0, WIDTH, HEIGHT))
        # Lives stat
        SCREEN.blit(lives, (10, 10))
        SCREEN.blit(levels, (WIDTH - 100, 10))
        SCREEN.blit(scores, (10, 40))
        # Enemy ships
        for enemy in enemies:
            enemy.move_lasers(player)
            enemy.draw(SCREEN)

        # Player ship
        player.move_lasers(enemies)
        player.draw(SCREEN)

        # Update the screen
        pygame.display.update()


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    while True:
        SCREEN.blit(bg, bg_rect)
        title = title_font.render(f"Press space to begin...", True, WHITE, BLACK)
        SCREEN.blit(title, (WIDTH / 2 - title.get_width() / 2, 350))
        pygame.display.update()

        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if keys[pygame.K_SPACE]:
            reset()
            main()
            pygame.time.wait(1000)


main_menu()
