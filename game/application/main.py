from ast import And
from glob import glob
import os
from pickle import FALSE
import random
from random import randint
from tracemalloc import start
import pygame
import math
from pygame.display import flip
import time


"""
===============================
========== FUNCTIES ===========
===============================
"""

#Kijken voor een knop voor game te beginnen
def check_press():
    global runStatus
    global startscreen
    # de events opvragen en in var steken
    e = pygame.event.get()
    # de lijst van events opvragen en doorlopen
    for event in e:
        #QUIT dan sluiten
        if event.type == pygame.QUIT:
            runStatus = False  
        #IF BUTTON PRESSED
        if event.type == pygame.KEYDOWN:
           startscreen = False

#Kijken voor restart knop
def check_reset(gs):
    global runStatus
    # de events opvragen en in var steken
    e = pygame.event.get()
    # de lijst van events opvragen en doorlopen
    for event in e:
        #QUIT dan sluiten
        if event.type == pygame.QUIT:
            runStatus = False  
        #IF BUTTON PRESSED
        if event.type == pygame.KEYDOWN:
            #P voor restart
            if event.key == pygame.K_p:
                gs.resetGS()

#Foto's inladen
def load_images(path):
    return pygame.image.load(path)

# Muziek inladen
def play_music():
    global musicPause
    pygame.mixer.init()
    musicGame = pygame.mixer.Sound(musicPath)
    musicPause = pygame.mixer.Sound(musicPathPause)
    pygame.mixer.Channel(1).play(musicGame, -1)

# Genereren van window
def create_main_surface():
    return pygame.display.set_mode(screen_size)
# De events nakijken
def check_events(gs):
    global runStatus
    global pause
    # de events opvragen en in var steken
    e = pygame.event.get()
    # de lijst van events opvragen en doorlopen
    for event in e:
        #QUIT dan sluiten
        if event.type == pygame.QUIT:
            runStatus = False  
        #IF BUTTON PRESSED
        if event.type == pygame.KEYDOWN:
            #ESCAPE DAN PAUZE
            if event.key == pygame.K_ESCAPE:
                # als false dan true
                if pause != True:
                    pause = True
                    pygame.mixer.Channel(1).pause()
                    pygame.mixer.Channel(2).play(musicPause, -1)
                # als true dan false
                else:
                    pause = False
                    pygame.mixer.Channel(2).stop()
                    pygame.mixer.Channel(1).unpause()
            #SPATIE DAN Schieten
            if event.key == pygame.K_SPACE:
                gs.fire_bullet()
                
        
# De keys iets laten doen
def process_keys(state):
    keys = pygame.key.get_pressed()
    x_direction = 0
    y_direction = 0
    toMove = False

    # if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_z]:
    #     y_direction -= 1
    # if keys[pygame.K_DOWN] or keys[pygame.K_s]:
    #     y_direction += 1
    if keys[pygame.K_LEFT] or keys[pygame.K_q] or keys[pygame.K_a]:
        x_direction -= 10
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        x_direction += 10
    if y_direction != 0 or x_direction != 0:
        if state.entities['player'].x + x_direction < 660 and state.entities['player'].x + x_direction > 0:
            state.moveEntity(state.entities['player'], x_direction, y_direction)

        
# Scherm clearen
def clear_surface():
    surface.fill((0,0,0))
"""
===============================
========== KLASSEN ============
===============================
"""
#De State class
class State:
    def __init__(self, clock):
        global hp
        self.entities = dict()
        image = pygame.image.load("..\\assets\\img\\sprite.png")
        self.entities["player"] = entity(image, 325, 597, player_speed, (image.get_width(), image.get_height())) #Aanmaken player object en in dictionary steken
        self.elapsed_time = clock / 1000
        self.bullets = []
        self.bullet_number = 0
        self.bullets_left = 20
        self.enemy_counter = 0
        self.enemy_reg_counter = 0
        self.enemy_tank_counter = 0
        self.enemy_bomber_counter = 0
        self.enemy_killed = 0
        self.wallHp = hp
        self.wave_number = 0
        self.wave_update_count = 0
        self.wave_queue = []
        self.enemy_killed = 0
        self.cooldowns = dict()
        self.cooldowns['shoot'] = cooldown(2)
        self.cooldowns['wave'] = cooldown(3)
        self.animations = [] # lijst voor de animated_sprites
        self.__background = background() #Background genereren in private field

    """
    ===============================
    ======= MOVE FUNCTIONS ========
    ===============================
    """
    def moveEntity(self, entity, x_direction, y_direction):
        mover = entity
        diagonal = math.sqrt(math.pow(x_direction,2) + math.pow(y_direction, 2))
        mover.x += (x_direction/diagonal) * mover.speed * self.elapsed_time
        mover.y += (y_direction/diagonal) * mover.speed * self.elapsed_time
        entity.update_collision_position()

    """
    ===============================
    ==== COLLISION FUNCTIONS ======
    ===============================
    """
    def collides(self, entity1, entity2):
        return pygame.Rect.colliderect(entity1.collision, entity2.collision)

    def handle_bullet_hit(self, i, enemy):
        if enemy not in self.entities:
            return
        death = self.entities[enemy]

        self.renderExplosion(death.x, death.y)

        bullet = self.bullets.pop(i)
        del bullet
        if self.entities[enemy].decrease_hp():
            self.kill_enemy(enemy)

    def is_out_of_bounds(self, entity, originx, originy, width, height):
        if entity.x < originx or entity.y < originy or entity.x > width or entity.y > height:
            return True
        return False

    """
    ===============================
    ====== BULLET FUNCTIONS =======
    ===============================
    """
    def fire_bullet(self):
        cooldown = self.cooldowns['shoot']
        if cooldown.ready:
            library.play("Gunshot.mp3")
            image = pygame.image.load("..\\assets\\img\\bullet.png")
            bullet = entity(image, (self.entities["player"].x + x_bullet_standoff), (self.entities["player"].y + y_bullet_standoff), bullet_speed, (image.get_width(), image.get_height()))
            self.bullets.append(bullet)
            self.bullet_number += 1
            self.bullets_left -= 1
            if self.bullet_number%20 == 0:
                cooldown.reset()
                self.bullets_left = 20    
                library.play("Reloading.mp3")

    def display_bullets(self, state):
        if state:
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"{self.bullets_left} BULLETS LEFT",True,white)
            surface.blit(text, (20,665))
        else:
            cooldown = self.cooldowns['shoot'].time_left()
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"RELOADING... {cooldown} SEC LEFT", True, white)
            surface.blit(text, (20, 665))

    def move_bullet(self):
        for i in range(len(self.bullets)-1, -1, -1):
            bullet = self.bullets[i]
            self.moveEntity(bullet, 0, -50)

        self.check_bullets()

    def check_bullets(self):
        hits = []
        continue_bullet = False
        for i in range(len(self.bullets)-1, -1, -1):
            continue_bullet = False
            for entity in self.entities:
                if continue_bullet:
                    continue
                if 'enemy' in entity:
                    if self.collides(self.bullets[i], self.entities[entity]):
                        hits.append((i, entity))
                        continue_bullet = True

        for i in hits:
            self.handle_bullet_hit(i[0], i[1])

        for i in range(len(self.bullets)-1, -1, -1):
            if self.is_out_of_bounds(self.bullets[i], 0, 0, screen_size[0], screen_size[1]):
                remove = self.bullets.pop(i)
                del remove

    """
    ===============================
    ========== ENEMIES ============
    ===============================
    """
    def generate_enemy(self, type):
        y_coord = 25
        x_coord = randint(0, 650)
        self.enemy_counter += 1

        if type == "reg":
            img = pygame.image.load('..\\assets\\img\\enemy_type1_sprite.png')
            speed = 75
            hp = 2
            self.entities[f'enemy_reg_{self.enemy_counter}'] = enemy(img, x_coord, y_coord, speed, (img.get_width(), img.get_height()), hp)
        elif type == "tank":
            img = pygame.image.load('..\\assets\\img\\enemy_tank.png')
            speed = 50
            hp = 4
            self.entities[f'enemy_tank_{self.enemy_counter}'] = enemy(img, x_coord, y_coord, speed, (img.get_width(), img.get_height()), hp)
        elif type == "bomb":
            img = pygame.image.load('..\\assets\\img\\enemy_bomb.png')
            speed = 100
            hp = 1
            self.entities[f'enemy_bomber_{self.enemy_counter}'] = enemy(img, x_coord, y_coord, speed, (img.get_width(), img.get_height()), hp)
        
    def move_enemies(self):
        global wall_y
        global gameover
        to_delete = []
        for entity in self.entities:
            if 'enemy' in entity:
                if(((self.entities[entity].y) + (self.entities[entity]).img.get_height()) < wall_y):
                    self.moveEntity(self.entities[entity], 0, 10)
                else:
                    if self.wallHp <= 0:
                        gameover = True
                    elif 'bomb' in entity:
                        self.wallHp -= 1000
                        self.renderExplosion(self.entities[entity].x, self.entities[entity].y)
                        to_delete.append(entity)
                    else:
                        self.wallHp -= self.elapsed_time * 300
        for i in to_delete:
            del self.entities[i]

    def kill_enemy(self, enemy):
        self.enemy_killed += 1
        if "reg" in enemy:
            self.enemy_reg_counter += 1
        if "tank" in enemy:
            self.enemy_tank_counter += 1
        if "bomb" in enemy:
            self.enemy_bomber_counter += 1
        del self.entities[enemy]
                
    """
    ===============================
    ============ WAVES ============
    ===============================
    """
    def generate_wave(self):
        if self.wave_number > 0:
            library.play("hasta_la_vista.mp3")
        
        self.wave_number += 1
    
        if self.wave_number == 1:
            for i in range(3):
                self.wave_queue.append('reg')
        elif self.wave_number == 2:
            for i in range(8):
                self.wave_queue.append('reg')
        elif self.wave_number == 3:
            self.wave_queue.append('tank')
        elif self.wave_number == 4:
            for i in range(4):
                self.wave_queue.append('reg')
            self.wave_queue.append('tank')
        elif self.wave_number == 5:
            for i in range(2):
                for i in range(4):
                    self.wave_queue.append('reg')
                self.wave_queue.append('tank')
        elif self.wave_number == 6:
            for i in range(5):
                self.wave_queue.append('reg')
            self.wave_queue.append('bomb')
        elif self.wave_number == 7:
            for i in range(8):
                self.wave_queue.append('bomb')
        elif self.wave_number == 8:
            for i in range(3):
                self.wave_queue.append('reg')
            for i in range(2):
                self.wave_queue.append('bomb')
            self.wave_queue.append('tank')
            for i in range(4):
                self.wave_queue.append('reg')
            for i in range(2):
                self.wave_queue.append('tank')
            for i in range(3):
                self.wave_queue.append('bomb')
        else:
            for i in range(20):
                rand = randint(1,3)
                if rand == 1:
                    self.wave_queue.append('reg')
                elif rand == 2:
                    self.wave_queue.append('tank')
                else:
                    self.wave_queue.append('bomb')

    def update_wave(self):
        if len(self.wave_queue) > 0:
            random = randint(1,100)
            if random > 95 :
                self.generate_enemy(self.wave_queue.pop(0))
        elif self.wave_done():
            if self.wave_update_count < self.wave_number:
                self.cooldowns['wave'].reset()
                self.wave_update_count += 1
            elif self.cooldowns['wave'].ready:
                self.generate_wave()

    def wave_done(self):
        for i in self.entities:
            if 'enemy' in i:
                return False
        return True

    """
    ===============================
    =========== UPDATE ============
    ===============================
    """
    def update(self, clock):
        self.elapsed_time = clock / 1000
        self.move_bullet()
        self.move_enemies()
        for ability in self.cooldowns:
            self.cooldowns[ability].update(self.elapsed_time)
        self.update_wave()
        process_keys(self)

    """
    ===============================
    =========== RENDER ============
    ===============================
    """
    def render(self):
        clear_surface()
        self.__background.render(surface) #Background renderen op de surface
        for entity in self.entities:
            self.entities[entity].render(surface) #dan de speler op de surface
        self.display_bullets(self.cooldowns['shoot'].ready)
        self.render_bullet(surface)
        self.renderHealthbar(surface)
        for anim in self.animations: #Loopen door animaties, eerst inrenderen, daarna updaten
            anim.render(surface)
            anim.update()
        

    def render_bullet(self, surface):
        for bullet in self.bullets:
            surface.blit(bullet.img, (bullet.x, bullet.y)) #Player op background plakken

    def renderPause(self):
        self.render()
        #dan alles renderen van pause screen
        font = pygame.font.SysFont(None, 24)
        text_controls_movement = font.render(f'Arrows or "wasd" / "zqsd" IS MOVING', True, white)
        text_controls_shoot = font.render(f'"SPACEBAR" IS SHOOT', True, white)
        text_controls_pause = font.render(f'"ESCAPE" IS PAUSE', True, white)
        pausedOverlay = pygame.image.load("..\\assets\\img\\paused.png")
        surface.blit(pausedOverlay,(0,0))
        surface.blit(text_controls_movement, (100, 410))
        surface.blit(text_controls_shoot, (100, 425))
        surface.blit(text_controls_pause, (100, 440))
        self.renderStats()

    def renderGameOver(self):
        self.render()
        font = pygame.font.SysFont(None, 24)
        text_reset = font.render("PRESS 'P' TO RESTART", True, white)
        gameOverOverlay = pygame.image.load("..\\assets\\img\\game_over.png")
        surface.blit(gameOverOverlay, (0,0))
        self.renderStats()
        surface.blit(text_reset, (260, 500))

    def renderStats(self):
        font = pygame.font.SysFont(None, 24)
        text_bullets = font.render(f'{self.bullet_number} BULLETS FIRED', True, white)
        text_enemies = font.render(f'{self.enemy_killed} KILLED', True, white)
        text_regs = font.render(f'{self.enemy_reg_counter} REGS KILLED', True, white)
        text_tank = font.render(f'{self.enemy_tank_counter} TANKS KILLED', True, white)
        text_bomber = font.render(f'{self.enemy_bomber_counter} BOMBERS KILLED', True, white)
        surface.blit(text_bullets, (100, 255))
        surface.blit(text_enemies, (100, 270))
        surface.blit(text_regs, (463, 240))
        surface.blit(text_tank, (453, 255))
        surface.blit(text_bomber, (425, 270))

    def renderExplosion(self, x, y):
        library.play_random_explosion()
        images = [load_images(f'..\\assets\\img\\explosions\\explosion{i}.png') for i in range(1, 17)]
        self.animations.append(animated_sprite(images, 0.5, x, y))

    def renderStart(self, surface):
        startscreenimg = pygame.image.load('..\\assets\\img\\startscreen.jpg')
        surface.blit(startscreenimg, (0,0))
        font = pygame.font.SysFont(None, 40)
        text_starscreen = font.render("Press any button to start", True, white)
        surface.blit(text_starscreen, (250, 475))
        flip()

    def renderHealthbar(self, surface):
        healthBar = round((self.wallHp/2000)*10)
        font = pygame.font.SysFont(None, 24)
        text_healthbar = font.render(f"HEALTH: {healthBar}%", True, red)
        surface.blit(text_healthbar, (555,665))
        


    """
    ===============================
    =========== RESET =============
    ===============================
    """

    def resetGS(self):
        global hp
        self.entities = dict()
        image = pygame.image.load("..\\assets\\img\\sprite.png")
        self.entities["player"] = entity(image, 325, 597, 150, (image.get_width(), image.get_height())) #Aanmaken player object en in dictionary steken
        self.bullets = []
        self.bullet_number = 0
        self.bullets_left = 20
        self.enemy_counter = 0
        self.enemy_reg_counter = 0
        self.enemy_tank_counter = 0
        self.enemy_bomber_counter = 0
        self.enemy_killed = 0
        self.wave_number = 0
        self.wave_update_count = 0
        self.wave_queue = []
        self.enemy_killed = 0
        self.cooldowns = dict()
        self.cooldowns['shoot'] = cooldown(2)
        self.cooldowns['wave'] = cooldown(3)
        self.animations = [] # lijst voor de animated_sprites
        self.__background = background() #Background genereren in private field
        self.wallHp = hp
        global gameover
        gameover = False


class entity:
    def __init__(self, img, x, y, speed, collision_offset):
        self.img = img
        self.x = x
        self.y = y
        self.speed = speed
        self.collision = pygame.Rect(x, y, collision_offset[0], collision_offset[1]/3 * 2)

    def update_collision_position(self):
        self.collision.x = self.x
        self.collision.y = self.y

    def render(self, surface):
        surface.blit(self.img, (self.x, self.y)) #Player op background plakken


class enemy(entity):
    def __init__(self, img, x, y, speed, collision_offset, hp):
        super().__init__(img, x, y, speed, collision_offset)
        self.hp = hp

    def decrease_hp(self):
        self.hp -= 1
        if self.hp == 0:
            return True
        return False

class soundLibrary:
    def __init__(self):
        paths = self.find_audio_files("..\\assets\\sounds")
        self.library = dict()
        for i in paths:
            self.library[i] = "..\\assets\\sounds\\" + i

        self.explosions = []
        for sound in self.library:
            if 'explosion' in sound or 'Explosion' in sound:
                self.explosions.append(sound)

    def add(self, name, path):
        self.library[name] = path

    def play(self, name):
        pygame.mixer.Sound.play(pygame.mixer.Sound(self.library[name]))

    def find_audio_files(self, path):
        paths = []

        for root, directories, files in os.walk(path):
            for name in files:
                strFullPathSounds = os.path.join(root, name)
                derive = strFullPathSounds[17:len(strFullPathSounds)]
                paths.append(derive)

        return paths

    def play_random_explosion(self):
        index = random.randint(0, len(self.explosions) - 1)
        self.play(self.explosions[index])

#Cooldown klasse
class cooldown:
    def __init__(self, time):
        self.ready = False
        self.time = time
        self.elapsed_time = 0

    def update(self, elapsed_seconds):
        if not self.ready:
            self.elapsed_time += elapsed_seconds
            if self.elapsed_time > self.time:
                self.ready = True

    def time_left(self):
        return math.ceil(self.time - self.elapsed_time)

    def reset(self):
        self.ready = False
        self.elapsed_time = 0
        
#Background klasse
class background:
    def __init__(self):
        self.img = self.__create_image()

    #Image inladen
    def __create_image(self):
        return pygame.image.load("..\\assets\\img\\background.png")

    #Image op de achtergrond(surface) zetten
    def render(self, surface):
        surface.blit(self.img, (0,0))

#Animated Sprite
class animated_sprite:
    def __init__(self, images, seconds_per_frame, x, y):
        self.images = images
        self.second_per_frame = seconds_per_frame
        self.time_passed = 0
        self.x = x
        self.y = y

    #Berekenen welke frame en deze inladen
    def render(self, surface):
        index = self.time_passed / self.second_per_frame
        if index < len(self.images):
            frame = self.images[round(index)]
            surface.blit(frame, (self.x, self.y))

    #Tijd aanpassen => index voor volgende frame
    def update(self):
        self.time_passed += self.second_per_frame

"""
===============================
============ MAIN =============
===============================
"""
#de main functie
def main():
    #VARIABELEN
    global runStatus #de runstatus global om te kunnen sluiten
    global pause
    global startscreen
    #INITIALISEREN
    pygame.init()

    #playing the music
    play_music()
    #de game state opslaan
    gameState = State(clock.tick(15))

    #Starten van het spel en blijven spelen
    while runStatus:
        
        while startscreen and runStatus:
            gameState.renderStart(surface)
            check_press()

        c = clock.tick(15)
        check_events(gameState)

        if pause:
            gameState.renderPause()
        elif gameover:
            gameState.renderGameOver()
            flip()
            while gameover and runStatus:
                check_reset(gameState)

        else:
            gameState.update(c)
            gameState.render()  # render de gamestate
        flip()

"""
===============================
========= VARIABLEN ===========
===============================
"""
runStatus = True #
pause = False
gameover = False
clock = pygame.time.Clock()
library = soundLibrary()
musicPath = "..\\assets\\sounds\\BackgroundMusic.mp3"
musicPathPause = "..\\assets\\sounds\\ElevatorMusic.mp3"
screen_size = (700, 700)
x_bullet_standoff = 18
y_bullet_standoff = -3
player_speed =  200
bullet_speed = 250
wall_y = 585
white = (255,255,255)
red = (255,0,0)
startscreen = True
global hp
hp = 20000

"""
===============================
======= FUNCTION CALLS ========
===============================
"""
#Hoe de code runt
surface = create_main_surface() #maak de viewscreen
main() #roep de main functie op