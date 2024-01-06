import pygame as pg
from random import uniform, choice, randint, random
from os import path
from settings import *
from functions import *
import pytweening as tween
from math import sin, cos, pi, atan2, hypot
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.speed = PLAYER_SPEED
        self.image = pg.Surface((1, 1))
        self.image.fill(MELNS)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.atNoCentra = vec(0, 0)
        self.vel = vec(0, 0)
        self.gravity = GRAVITY / 2
        self.acc = vec(0, self.gravity)
        self.rot = 0
        self.mana = PLAYER_MANA
        self.slowmo = False
        self.gas = False
        self.dzivibas = 10

    def update(self):
        x, y = pg.mouse.get_pos()
        self.distaa = hypot(self.pos[0] - x, self.pos[1] - y)
        self.rot = (((x, y) - self.pos).angle_to(vec(1,0))) 
        if self.distaa > 10:
            self.gravity = GRAVITY / 2
            if self.gas == True:
                self.acc = vec(1, 0).rotate(-self.rot)# - 180)
                for e in range(self.dzivibas // 2):
                    ParticleBoosting(self.game, self.pos, self.rot)
            else:
                self.acc = vec(0, 0)
        else:
            self.acc = vec(0, 0)
            self.gravity = 0
        if self.game.started:
            self.acc.y += self.gravity
        self.acc += self.vel * PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.4:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos[0]
        self.hit_rect.centery = self.pos[1]
        self.rect.center = self.hit_rect.center
        for particle in range(self.dzivibas):
            ParticleMain(self.game, self.pos, self.dzivibas)
       # self.image = pg.transform.rotate(self.image, self.rot)
        self.mask = pg.mask.from_surface(self.image)
        if self.mana < 0:
            self.mana = 0

    def add_mana(self, amount):
        self.mana += amount
        if self.mana > PLAYER_MANA:
            self.mana = PLAYER_MANA

    def collide_with_walls(self, sprite, group, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x *= -1
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = 0
                sprite.hit_rect.centery = sprite.pos.y

class Segment:
    # Represents an obstacle in the game
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def intersects(self, ray):
        # Implement intersection logic between a ray and this segment
        pass

class Ray(pg.sprite.Sprite):
    def __init__(self, origin, angle, length=200, color=CYAN):
        super().__init__()
        self.image = pg.Surface([length, 2], pg.SRCALPHA)  # Create a transparent surface
        self.image.fill(color) 
        self.rect = self.image.get_rect()
        self.origin = origin
        self.angle = angle
        self.length = length
        self.max_length = length
        self.update()

    def update(self):
        end_point = pg.Vector2(math.cos(self.angle), math.sin(self.angle)) * self.length
        self.rect.x, self.rect.y = self.origin
        self.image = pg.transform.rotate(self.image, -math.degrees(self.angle))
        self.rect = self.image.get_rect(center=(self.origin[0] + end_point.x / 2, self.origin[1] + end_point.y / 2))

    def get_endpoint(self):
        end_point = pg.Vector2(math.cos(self.angle), math.sin(self.angle)) * self.length
        return self.origin + end_point

    # def calculate_intersection(self, edge):
    #     # Edge is defined by two points (start and end)
    #     edge_start, edge_end = edge

    #     # Ray direction
    #     ray_dir = pg.Vector2(math.cos(self.angle), math.sin(self.angle))

    #     # Find vectors
    #     v1 = self.origin - pg.Vector2(edge_start)
    #     v2 = pg.Vector2(edge_end) - pg.Vector2(edge_start)
    #     v3 = pg.Vector2(-ray_dir.y, ray_dir.x)

    #     # Check if the ray and the edge are parallel
    #     dot = v2.dot(v3)
    #     if abs(dot) < 1e-10:
    #         return None  # They are parallel so they don't intersect

    #     # Calculate the t and u parameters to find the intersection point
    #     t = v2.cross(v1) / dot
    #     u = v1.dot(v3) / dot

    #     # Check if the intersection is on the edge and on the ray
    #     if 0 <= u <= 1 and t >= 0:
    #         intersection = self.origin + t * ray_dir
    #         return intersection
    #     return None


class ParticleBoosting(pg.sprite.Sprite):
    def __init__(self, game, pos, rot):
        pg.sprite.Sprite.__init__(self, (game.all_sprites, game.particles))
        self.game = game
        self.image = pg.Surface((2, 2))
        self.image.fill(MELNS)
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.vel = vec(0, 0)
        if randint(0, 10) != 1:
            self.rot = rot + randint(-12, 12)
        else:
            self.rot = rot + choice([randint(-15,-12), randint(12,15)])
        self.acc = vec(1, 0).rotate(self.rot)
        self.rect.center = self.pos
        self.lifetime = PARTICLE_LIFETIME + randint(-500, 500)
        self.spawn_time = pg.time.get_ticks()
        self.update_time = pg.time.get_ticks()
        self.hit_rect = self.rect
        
    def update(self): 
        self.rect = self.image.get_rect()
        now = pg.time.get_ticks()
        if now - self.spawn_time < 100:
            self.acc = vec(1, GRAVITY).rotate(-self.rot - 180)
        else:
            self.acc = vec(0, GRAVITY)
        self.vel += self.acc
        if self.pos.x > ekplat:
            self.vel.x *= -1
        if self.pos.x < 0:
            self.vel.x *= -1
        if self.pos.y >= ekgar:
            self.kill()
        self.pos += self.vel + 0.5 * self.acc
        self.hit_rect.centerx = self.pos.x
        # hits = pg.sprite.spritecollide(self, self.game.walls, False)
        # for hit in hits:
        #     hit.create_hole(self.pos)
        #     self.kill() 
        
        self.collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        # ex, ey = self.image.get_size()
        # if now - self.update_time > self.lifetime / 2:
        #     self.update_time = now
        #     ex -= 1
        #     ey -= 1
        #     if ex >= 1 and ey >= 1:
        #         self.image = pg.transform.scale(self.image, (ex, ey))
        if now - self.spawn_time > self.lifetime:
            self.kill()

        

    def collide_with_walls(self, sprite, group, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x *= -1
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.vel.y = (sprite.vel.y * -1) // 2 + choice([random.random() * -1, random.random()])
                sprite.hit_rect.centery = sprite.pos.y


class ParticleMain(pg.sprite.Sprite):
    def __init__(self, game, pos, dzivibas):
        pg.sprite.Sprite.__init__(self, (game.all_sprites, game.particles, game.main_particles))
        self.game = game
        self.image = pg.Surface((2, 2))
        self.image.fill(MELNS)
        self.dzivibas = dzivibas // 2
        self.rect = self.image.get_rect()
        self.pos = vec(randomInCircle(pos, self.dzivibas))
        self.rect.center = self.pos
        self.lifetime = (200 + randint(-100, 100))
        self.spawn_time = pg.time.get_ticks()
        self.update_time = pg.time.get_ticks()

    def update(self):
        now = pg.time.get_ticks()
        rando = randint(1, 8)
        if rando == 1:
            self.pos[0] += 1
        if rando == 2:
            self.pos[0] -= 1
        if rando == 3:
            self.pos[1] -= 1
        if rando == 4:
            self.pos[1] += 1
        ex, ey = self.image.get_size()
        if now - self.update_time > self.lifetime / 2:
            self.update_time = now
            ex -= 1
            ey -= 1
            if ex >= 1 and ey >= 1:
                self.image = pg.transform.scale(self.image, (ex, ey))
        if now - self.spawn_time > self.lifetime:
            self.kill()
        self.rect.center = self.pos

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.image = pg.Surface((w, h))
        self.image.fill(MELNS)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.game.started:
            self.rect.y += 1

    def get_corners(self):
        if self.rect.y < 0 or self.rect.y > ekgar:
            return []
        corners = [
            (self.rect.topleft),
            (self.rect.topright),
            (self.rect.bottomleft),
            (self.rect.bottomright)
        ]
        return corners

    def create_hole(self, pos):
        # Convert global position to local position on the obstacle
        local_pos = (int(pos[0] - self.rect.x), int(pos[1] - self.rect.y))
        # Create a 1-pixel hole
        self.image.set_at(local_pos, pg.Color("white"))

class ManaBlob(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.mana_blobs, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.image = pg.Surface((w, h))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class TmpPoint(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.tmp_points, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.image = pg.Surface((w, h))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class TutorialKey(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, key, description):
        self.groups = game.tutorial_keys, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.text_offset = w
        self.rect = pg.Rect(x, y, w * 3, h)
        self.key = key
        self.description = description

        img_path = path.join('img', f"{key}_key.png")
        if path.exists(img_path):
            image = pg.image.load(img_path)
            image = pg.transform.scale(image, (w, h))
            image_w, image_h = image.get_size()
            self.image = pg.Surface((image_w * 2 + self.text_offset, h))
            self.image.fill(CYAN)
            self.image.blit(image, (0, 0))
            self.text_offset = image_w
        else:
            self.image = pg.Surface((w * 3, h))
            self.image.fill(CYAN)

        self.draw_key_text()

        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.x = x
        self.rect.y = y

    def draw_key_text(self):
        text = f"{self.key}: {self.description}"
        font = pg.font.Font(self.game.font_name, 25)
        text_surface = font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=(self.text_offset + (self.rect.w - self.text_offset) / 2, self.rect.h / 2))
        self.image.blit(text_surface, text_rect)
    
    def update(self):
        if self.game.started:
            self.rect.y += 1


