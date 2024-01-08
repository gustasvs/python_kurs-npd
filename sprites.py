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
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((1, 1))
        # self.image.fill(MELNS)
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
        self.mana = self.game.player_stats['player_mana']
        self.slowmo = False
        self.gas = False
        self.disabled = False
        self.tick_disabled = 0

    def update(self):
        
        # player disabled check
        if self.disabled:
            now = pg.time.get_ticks()
            if now - self.tick_disabled >= MS_DISABLED:
                self.disabled = False
                self.gravity = GRAVITY / 2
                self.acc = vec(0, self.gravity)

        particle_count = round(1 + self.mana * self.game.player_stats['player_size'] / self.game.player_stats['player_mana'])
        x, y = pg.mouse.get_pos()
        self.distaa = hypot(self.pos[0] - x, self.pos[1] - y)
        self.rot = (((x, y) - self.pos).angle_to(vec(1,0))) 
        if self.distaa > 10:
            if self.gas == True:
                self.gravity = GRAVITY / 2
                self.acc = vec(1, 0).rotate(-self.rot)# - 180)
                for _ in range(particle_count // 3):
                    ParticleBoosting(self.game, self.pos, self.rot)
            else:
                self.acc = vec(0, 0)
        elif self.gas:
            
            self.acc = vec(0, 0)
            self.gravity = 0
            for _ in range(particle_count // 10):
                ParticleBoosting(self.game, self.pos, random.randint(1, 360))
        gravity_multiplier = 1
        if self.game.started and not self.game.paused and not self.game.ended and not self.disabled:
            if (self.mana < self.game.player_stats['player_mana'] / 10) and not self.gas:
                gravity_multiplier = 6
        self.acc.y += self.gravity * gravity_multiplier
        self.acc += self.vel * PLAYER_FRICTION
        self.acc *= self.game.player_stats['player_speed']
        self.vel += self.acc
        if abs(self.vel.x) < 0.2:
            self.vel.x = 0

        if self.vel.y < 0 and not self.game.ended and not self.game.paused:
            # self.game.total_points += round(abs(self.vel.y / 6)) 
            self.game.player_stats['total_points_target'] += round(abs(self.vel.y / 6)) 
            self.game.current_points += round(abs(self.vel.y / 6)) 
        if self.game.started and not self.pos.y > ekgar + 40:
            self.pos += self.vel + 0.5 * self.acc
        self.rect.center = self.pos
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos[0]
        self.hit_rect.centery = self.pos[1]
        self.rect.center = self.hit_rect.center
        
        # particles that make up player
        for _ in range(particle_count):
            radius = particle_count
            if self.disabled:
                now = pg.time.get_ticks()

                elapsed_time = now - self.tick_disabled
                remaining_time = self.game.player_stats['ms_disabled'] - elapsed_time

                normalized_time = (elapsed_time / self.game.player_stats['ms_disabled']) ** 0.1
                normalized_remaining_time = remaining_time / self.game.player_stats['ms_disabled']

                radius_factor = 40 * normalized_time * normalized_remaining_time
                radius = particle_count + (radius_factor * particle_count)

                if random.randint(1, 30) == 1:
                    ParticleBoosting(self.game, self.pos, random.randint(1, 360))

            ParticleMain(self.game, self.pos, self.vel, (radius if self.game.started else random.choice(
                [15, 15, 15, 15, 15, 25, 50, 80]
            )))

        self.mask = pg.mask.from_surface(self.image)
        if self.mana < 0:
            self.mana = 0
        hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)

        if hits and not self.game.ended:
            self.game.hit_wall.play()
            if not self.disabled:
                self.mana -= ADD_MANA // 2
                self.disabled = True
                self.tick_disabled = pg.time.get_ticks()

                if self.rect.right < hits[0].rect.left:
                    print("HIT RIGHT")
                    self.pos.x = hits[0].rect.left - self.hit_rect.width * 2# / 2
                    self.vel.x *= -0.1
                elif self.rect.left > hits[0].rect.right:
                    print("HIT LEFT")
                    self.pos.x = hits[0].rect.right + self.hit_rect.width * 2
                    self.vel.x *= -0.1

                elif self.rect.y < hits[0].rect.y:
                    print("HIT TOP")
                    self.pos.y = hits[0].rect.top - self.hit_rect.height * 2
                    self.vel.y = 0
                elif self.rect.y > hits[0].rect.y:
                    print("HIT BOTTOM")
                    self.pos.y = hits[0].rect.bottom + self.hit_rect.height * 2
                    self.vel.y = 0
                    self.acc.y = self.gravity
                    self.gravity *= 2
                

                self.rect.center = self.pos
        # self.collide_with_walls(self, self.game.walls, 'x')
        # self.hit_rect.centery = self.pos.y
        # self.collide_with_walls(self, self.game.walls, 'y')
        # self.rect.center = self.hit_rect.center

    def add_mana(self, amount):
        self.mana += amount
        self.mana = min(self.mana, self.game.player_stats['player_mana'])


    def collide_with_walls(self, sprite, group, dir):
        if dir == 'x':
         
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            
            if hits:
                # self.mana -= ADD_MANA // 2
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.vel.x *= -5
                self.acc.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                
                if sprite.rect.top >= hits[0].rect.bottom or sprite.rect.bottom <= hits[0].rect.top:

                    # self.mana -= ADD_MANA // 2
                    if hits[0].rect.centery > sprite.hit_rect.centery:
                        sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                        sprite.vel.y *= -2
                    if hits[0].rect.centery < sprite.hit_rect.centery:
                        sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                        sprite.vel.y *= -2
                    sprite.vel.x = 0
                    
                    sprite.hit_rect.centery = sprite.pos.y


class Ray(pg.sprite.Sprite):
    def __init__(self, origin, angle, length=200, color=CYAN, end=None):
        super().__init__()
        self.image = pg.Surface([max(1, length), 1], pg.SRCALPHA)
        self.image.fill(color) 
        self.rect = self.image.get_rect()
        self.origin = origin
        self.angle = angle
        self.length = length
        end_point = pg.Vector2(math.cos(self.angle), math.sin(self.angle)) * self.length
        if end is not None:
            end_point - end
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
    particle_surface = pg.Surface((1, 1))
    particle_surface.fill(MELNS)

    def __init__(self, game, pos, rot):
        pg.sprite.Sprite.__init__(self, (game.all_sprites, game.particles))
        self.game = game
        self.image = ParticleBoosting.particle_surface
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
    def __init__(self, game, pos, vel, dzivibas):
        pg.sprite.Sprite.__init__(self, (game.all_sprites, game.particles, game.main_particles))
        self.game = game
        self.image = pg.Surface((2, 2))
        self.image.fill(MELNS)
        self.rect = self.image.get_rect()

        offset = vel / 10 * 10
        offset = vec(min(offset.x, 10), min(offset.y, 10))
        self.pos = vec(randomInCircle(pos, dzivibas // 2)) + offset
        self.rect.center = self.pos
        self.lifetime = (150 + randint(-50, 50))
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

        direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])
        while check_wall_collisions(self):
            self.rect.x += direction[0]
            self.rect.y += direction[1]

    def update(self):
        if self.game.started and not self.game.paused and not self.game.ended:
            self.rect.y += 1

    def get_corners(self):
        if self.rect.bottom < -10 or self.rect.top > ekgar:
            return []
        corners = [
            (self.rect.topleft),
            (self.rect.topright),
            (self.rect.bottomleft),
            (self.rect.bottomright)
        ]
        return corners

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
            self.image.fill(BGCOLOR)
            self.image.blit(image, (0, 0))
            self.text_offset = image_w
            self.draw_key_text(self.description)
        else:
            self.image = pg.Surface((w * 3, h))
            self.image.fill(BGCOLOR)
            self.draw_key_text(f"{self.key} - {self.description}")

        

        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.x = x
        self.rect.y = y

    def draw_key_text(self, text):
        text = f"{text}"
        font = pg.font.Font(self.game.font_name, 30)
        text_surface = font.render(text, True, MELNS)
        text_rect = text_surface.get_rect(center=(self.text_offset + (self.rect.w - self.text_offset) / 2, self.rect.h / 2))
        self.image.blit(text_surface, text_rect)
    
    def update(self):
        if self.game.started and not self.game.paused and not self.game.ended:
            self.rect.y += 1


class UpgradeButton(pg.sprite.Sprite):
    point_img = pg.transform.scale(pg.image.load(path.join('img', "point.png")), (30, 30))
    def __init__(self, game, x, y, w, h, cost, amount, short_desc, player_field, image):
        self.groups = game.upgrade_buttons, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.cost = cost
        self.amount = amount
        self.short_desc = short_desc
        self.player_field = player_field
        self.clicked = False
        
        text_area_height = 50

        self.button_color = (100, 100, 100, 100)
        self.hover_color = (50, 50, 50, 240)

        img_path = path.join('img', image)

        image = pg.image.load(img_path)
        image = pg.transform.scale(image, (w, h))

        self.image_to_blit = image
        self.h = h

        #normal
        self.image_normal = pg.Surface((w + text_area_height, h + text_area_height), pg.SRCALPHA)
        self.image_normal.fill((0, 0, 0, 0))
        self.image_normal.blit(image, (0, 20))
        
        self.draw_text(self.image_normal, f"{self.short_desc}", (10, h + 20), MELNS, 30)
        self.draw_text(self.image_normal, f"{self.game.player_stats[self.player_field]}", (10, 0), MELNS, 37)
        
        #hover
        self.image_hover = pg.Surface((w + text_area_height, h + text_area_height), pg.SRCALPHA)
        self.image_hover.fill((0, 0, 0, 0))
        self.image_hover.blit(image, (0, 0))
        overlay = pg.Surface((w, h), pg.SRCALPHA)
        overlay.fill(self.hover_color)
        self.image_hover.blit(overlay, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        
        # self.draw_text(self.image_hover, f"{self.cost}", (0, h))
        self.draw_text(self.image_hover, f"{self.short_desc}", (10, h), MELNS, 30)
        text_rect = self.draw_text(self.image_hover, f"{self.cost}", (10, h / 2 - 10), GOLDEN, 50)
        point_pos = (text_rect.right + 5, text_rect.centery - 18)
        self.image_hover.blit(self.point_img, point_pos)

        self.image = self.image_normal
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.x = x
        self.rect.y = y

        self.was_clicked = False
        self.was_hovered = False

    def draw_text(self, surface, text, position, color, size):
        font = pg.font.Font(self.game.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(topleft=position)
        surface.blit(text_surface, position)
        return text_rect
    
    def update(self):
        if self.game.started and not self.game.paused and not self.game.ended:
            self.rect.y += 1

        mouse_pos = pg.mouse.get_pos()
        mouse_clicked = pg.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            self.image = self.image_hover
            if not self.was_hovered:
                self.game.hover_button_snd.play()
                self.was_hovered = True
            if mouse_clicked and not self.was_clicked:  
                self.on_click()
                self.was_clicked = True
            elif not mouse_clicked:
                self.was_clicked = False
        else:
            self.image = self.image_normal
            self.was_hovered = False

    def on_click(self):
        if not self.was_clicked:
            iters = 30
            color = GOLDEN
            if self.game.player_stats['total_points_target'] >= self.cost:
                self.game.upgrade_successfull.play()
                self.game.player_stats['total_points_target'] -= self.cost
                self.game.player_stats[self.player_field] += self.amount
                
                self.image_normal.fill((0, 0, 0, 0))
                self.image_normal.blit(self.image_to_blit, (0, 20))
                self.draw_text(self.image_normal, f"{self.short_desc}", (10, self.h + 20), MELNS, 30)
                self.draw_text(self.image_normal, f"{round(self.game.player_stats[self.player_field])}", (10, 0), MELNS, 37)
            else:
                self.game.upgrade_failure.play()
                color = RED
                iters = 6
            
            for _ in range(iters):
                ParticlePoint(self.game, color, 
                              vec(random.randint(self.rect.centerx - 20, self.rect.centerx + 20), 
                                  random.randint(self.rect.centery - 20, self.rect.centery + 20)))

class ParticlePoint(pg.sprite.Sprite):
    point_img = pg.transform.scale(pg.image.load(path.join('img', "point.png")), (10, 10))
    def __init__(self, game, color, pos):
        pg.sprite.Sprite.__init__(self, (game.all_sprites, game.effect_particles))
        self.game = game
        self.image = pg.Surface((6, 6), pg.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        pg.draw.circle(self.image, color, (1, 1), 3)
        if random.randint(1, 5) == 5 and color != RED:
            self.image = ParticlePoint.point_img
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.vel = vec(0, 0)
        self.rot = random.randint(1, 360)
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
        
        self.collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

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