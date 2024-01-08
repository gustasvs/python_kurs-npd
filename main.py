import pygame as pg
import sys
from random import choice, random, randint
from os import path
from settings import *
from sprites import *

import json

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.music = pg.mixer.Sound('music/background_music.ogg')
        self.music.set_volume(0.3) 
        # self.music.play(loops = -1)
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.screen = pg.display.set_mode((ekplat, ekgar))
        pg.display.set_caption(TITLE)
        self.font_name = pg.font.match_font(FONT_NAME)
        self.clock = pg.time.Clock()
        self.load_data()
        self.FPS = FPS
        self.dalitaj = 1000.0

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        
        self.player_stats = None
        # load_player_stats()
        if self.player_stats == None:
            self.player_stats = {
                'total_points_target': 0,
                'total_points': 0,
                'player_size': PLAYER_SIZE,
                'player_mana': PLAYER_MANA,
                'ms_disabled': MS_DISABLED,
                'player_speed': PLAYER_SPEED,
                'add_mana_speed': ADD_MANA_SPEED,
                'add_mana': ADD_MANA
            }
            self.player_stats['player_speed']
        self.point_image_small = pg.transform.scale(pg.image.load(path.join('img', "point.png")), (25, 25))
        self.point_image_large = pg.transform.scale(pg.image.load(path.join('img', "point.png")), (50, 50))
        self.speed_image_small = pg.transform.scale(pg.image.load(path.join('img', "speed.png")), (25, 25))

        self.hit_wall = pg.mixer.Sound('snd/hit_wall.mp3')
        self.ended_snd = pg.mixer.Sound('snd/ended.mp3')
        self.mana_collected_snd = pg.mixer.Sound('snd/collect_mana.mp3')
        self.upgrade_successfull = pg.mixer.Sound('snd/upgrade_successfull.wav')
        self.upgrade_failure = pg.mixer.Sound('snd/upgrade_failure.mp3')
        self.gas_snd = pg.mixer.Sound('snd/swoosh.mp3')
        self.start_playing_snd = pg.mixer.Sound('snd/start_sound.mp3')
        self.hover_button_snd = pg.mixer.Sound('snd/hover_button.mp3')

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

    def setup_tutorial_keys(self):
        keys_info = [
            ("esc", "Pirmslaicīgi zaudēt"), 
            ("shift", "Izmantot dzinēju"),
            ("mouse", "Tēmēt kustību"),
            ("p", "Pauzēt spēli")
        ]
        x, y = 50, ekgar - 70 
        for key, description in keys_info:
            TutorialKey(self, x, y, 160, 75, key, description)  
            y -= 85
    def show_player_upgrades(self):
        upgrade_info = [
            ("Dzīvības", "player_mana", "max_particles.png", 20, 10), 
            ("Ātrums", "player_speed", "speed.png", 100, 0.2),
            ("Lielums", "player_size", "size.png", 50, 1),
            ("Enerģijas patēriņš", "add_mana_speed", "spending_speed.png", 100, 0.1)
        ]
        x, y = 30, ekgar / 2 - 230
        for key, description, image, cost, amount in upgrade_info:
            UpgradeButton(self, x, y, 120, 120, cost, amount, key, description, image)
            x += 130 

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.rays = pg.sprite.Group()
        self.tmp_points = pg.sprite.Group()
        self.tutorial_keys = pg.sprite.Group()
        self.upgrade_buttons = pg.sprite.Group()
        self.mana_blobs = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.main_particles = pg.sprite.Group()
        self.effect_particles = pg.sprite.Group()
        self.player = Player(self, ekplat / 2, ekgar / 2)
        self.draw_debug = False
        self.paused = False
        self.ended = False
        self.started = False
        self.mana_index = 1
        self.current_points = 0

        self.setup_tutorial_keys()
        self.show_player_upgrades()
    
    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(self.FPS) / self.dalitaj
            self.events()
            if not self.paused or not self.ended:
                self.update()
            self.draw()

    def createObstacle(self, x, y, w, h):
        # for xx in range(w):
        #     for yy in range(h):
        #         Obstacle(self, x + xx, y + yy, 1, 1)
        Obstacle(self, x, y, w, h)
    def createManaBlob(self, x, y, w, h):

        ManaBlob(self, x, y, w, h)

    def quit(self):
        save_player_stats(self.player_stats)
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.rays.empty()  
        self.tmp_points.empty()

        for wall in self.walls:
            for corner in wall.get_corners():
                intersections = 0
                hit_same_object_again = False

                for other_wall in self.walls:
                    edges = [ # objekta visas sienas
                        (other_wall.rect.topleft, other_wall.rect.topright),
                        (other_wall.rect.topright, other_wall.rect.bottomright),
                        (other_wall.rect.bottomright, other_wall.rect.bottomleft),
                        (other_wall.rect.bottomleft, other_wall.rect.topleft)
                    ]
                    # vai ar kādu no sienām saskaras
                    for edge_start, edge_end in edges:
                        if do_intersect(self.player.pos, corner, edge_start, edge_end):
                            intersections += 1
                            break
                    if intersections > 1:
                        break

                hit_same_object_again = count_intersections_with_wall(self.player.pos, corner, wall)
                
                angle_to_corner = math.atan2(corner[1] - self.player.pos[1], corner[0] - self.player.pos[0])
                color = CYAN
                if hit_same_object_again:
                    color = MELNS

                extended_side = get_extended_ray_side(self.player.pos, corner, wall)
                angle_offset = math.radians(0.01) if extended_side == 1 else -math.radians(0.01)

                if intersections == 0:
                    dist = distance(corner, self.player.pos)
                    if not hit_same_object_again:
                        ray2 = Ray(self.player.pos, angle_to_corner - angle_offset, dist, color)
                        self.rays.add(ray2)
                    else:
                        ray = Ray(self.player.pos, angle_to_corner, dist, color)
                        self.rays.add(ray)

                if  intersections == 0 and not hit_same_object_again:
                    angle = calculate_distance_to_map_boundary(self.player.pos, angle_to_corner, self.walls, wall)                    
                    # print("angle: ", angle)
                    extended_ray_2 = Ray(self.player.pos, angle_to_corner , angle, color)
                    self.rays.add(extended_ray_2)

        map_corners = [
            (0, 0),
            (ekplat, 0),
            (ekplat, ekgar),
            (0, ekgar)
        ]

        for map_corner in map_corners:
            intersections = 0
            angle_to_corner = math.atan2(map_corner[1] - self.player.pos[1], map_corner[0] - self.player.pos[0])

            for wall in self.walls:
                edges = [
                    (wall.rect.topleft, wall.rect.topright),
                    (wall.rect.topright, wall.rect.bottomright),
                    (wall.rect.bottomright, wall.rect.bottomleft),
                    (wall.rect.bottomleft, wall.rect.topleft)
                ]

                for edge_start, edge_end in edges:
                    if do_intersect(self.player.pos, map_corner, edge_start, edge_end):
                        intersections += 1
                        break  # If one wall intersects, no need to check others

            # If there are no intersections, add a ray to the map corner
            if intersections == 0:
                distance_to_corner = math.hypot(map_corner[0] - self.player.pos[0], map_corner[1] - self.player.pos[1])
                ray_to_corner = Ray(self.player.pos, angle_to_corner, distance_to_corner)
                self.rays.add(ray_to_corner)


        if self.player.mana == 0 or self.player.disabled:
            self.player.gas = False
        if self.player.gas == True:
            self.player.mana -= 1
        if self.player.gas == False:
            if self.player.mana < PLAYER_MANA and not self.paused and not self.ended:
                self.player.mana += self.player_stats['add_mana_speed']
        # print(self.player.pos.y)
        if self.player.pos.y > ekgar:
            if not self.ended:
                self.ended_snd.play(fade_ms=3000)
            self.ended = True

        mana_hits = pg.sprite.spritecollide(self.player, self.mana_blobs, True)
        for _ in mana_hits:
            self.mana_collected_snd.play()
            self.player.mana += ADD_MANA

        # wall_hits = pg.sprite.spritecollide(self.player, self.walls, False)
        # for mana_blob in wall_hits:
        #     self.player.vel.x *= -1
        #     self.player.vel.y *= -1
        #     self.player.mana -= ADD_MANA // 2

        # uz citam psuem ne tikai augšu
        # if self.player.pos.x > ekplat - ekplat / 6:
        #     for obs in self.walls:
        #         obs.rect.x -= self.player.vel.x
        #     for part in self.main_particles:
        #         part.pos.x -= self.player.vel.x
        #     self.player.pos.x -= self.player.vel.x
        #     self.player.atNoCentra.x -= self.player.vel.x
        # if self.player.pos.x < ekplat / 6:
        #     for obs in self.walls:
        #         obs.rect.x -= self.player.vel.x
        #     for part in self.main_particles:
        #         part.pos.x -= self.player.vel.x
        #     self.player.pos.x -= self.player.vel.x
        #     self.player.atNoCentra.x -= self.player.vel.x
        # if self.player.pos.y > ekgar - ekgar / 6:
        #     for obs in self.walls:
        #         obs.rect.y -= self.player.vel.y
        #     for part in self.main_particles:
        #         part.pos.y -= self.player.vel.y
        #     self.player.pos.y -= self.player.vel.y
        #     self.player.atNoCentra.y -= self.player.vel.y
        
        # spēlētajs cenšas uziet uz augšu
        if self.player.pos.y < ekgar / 3:
            self.player.pos.y -= self.player.vel.y;
            groups = [self.walls, self.tutorial_keys, self.mana_blobs, self.upgrade_buttons]
            for group in groups:
                for obs in group:
                    obs.rect.y += abs(self.player.vel.y)
                    if obs.rect.top >= ekgar:
                        obs.kill()
            # for particle effect still following behind
            for part in self.main_particles:
                part.pos.y -= self.player.vel.y
        while len(self.walls) < OBSTACLE_COUNT:
            size = randint(10, 11)
            width = size + randint(50, 200)
            height = size + randint(20, 40)
            pposx = round(self.player.pos.x)
            pposy = round(self.player.pos.y)
            x = randint(0, ekplat - width)
            y = randint(-ekgar * 2, -50)
            self.createObstacle(x, y, width, height)

        while len(self.mana_blobs) < 4:
            x = randint(0, ekplat - 20)
            y = (-ekgar / 1) * self.mana_index
            self.mana_index += 1
            self.createManaBlob(x, y, 20, 20)
            print(x, y)
    # HUD
    def draw_player_mana(self, surf, x, y, pct):
        if pct < 0:
            pct = 0
        if pct > 1:
            pct = 1
        BAR_LENGTH = ekplat / 2
        BAR_HEIGHT = 20
        fill = pct * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)

        # for px in range(x, x + int(BAR_LENGTH)):
        #     for py in range(y, y + int(BAR_HEIGHT)):
        #         if px <= x + fill:  # In the unspent area
        #             spawn_chance = 0.9  # High chance of spawning
        #         else:  # In the spent area
        #             spawn_chance = 0.1  # Low chance of spawning

        #         if random.random() < spawn_chance:
        #             particle_color = (255 * (1 - pct), 255 * pct, 0)
        #             pg.draw.circle(surf, particle_color, (px, py), 2)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        col = (255 * (1 - pct), 255 * pct, 0)
        pg.draw.rect(surf, col, fill_rect)


        pg.draw.rect(surf, DARKGREY, outline_rect, 2)
        # self.draw_text(f"{self.player.mana}", 25, DARKGREY, ekplat / 4 + 20, 43)

        # punkti
        font = pg.font.Font(self.font_name, 40)
        text = f"{self.player_stats['total_points']}"
        if self.player_stats['total_points'] > self.player_stats['total_points_target']:
            self.player_stats['total_points'] -= 1
        if self.player_stats['total_points'] < self.player_stats['total_points_target']:
            self.player_stats['total_points'] += 1
        text_surface = font.render(text, True, GOLDEN)
        text_width, text_height = text_surface.get_size()

        text_x = ekplat - text_width // 2 - 10
        image_x = text_x - self.point_image_small.get_width() - text_width // 2 - 10
        self.draw_text(text, 40, GOLDEN, text_x, 20)
        surf.blit(self.point_image_small, (image_x, 20))


    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        if self.draw_debug:
            self.rays.draw(self.screen)

        self.effect_particles.draw(self.screen)

        visibility_polygon = []
        sorted_rays = sorted(self.rays, key=lambda ray: (ray.angle, ray.length))
        for ray in sorted_rays:
            endpoint = ray.get_endpoint()
            visibility_polygon.append(endpoint)
        if visibility_polygon:
            try:
                fog_surface = pg.Surface((ekplat, ekgar), pg.SRCALPHA)
                fog_surface.fill((0, 0, 0, 200)) # VISIBILITY
                pg.draw.polygon(fog_surface, (255, 255, 255, 0), visibility_polygon)
                self.screen.blit(fog_surface, (0, 0))
            except Exception as e:
                print("Failed to draw inverted visibility polygon:", e)
            
        if self.draw_debug:
            for sprite in self.all_sprites:
                if sprite not in self.particles and sprite not in self.tutorial_keys:
                    pg.draw.rect(self.screen, CYAN, (sprite.hit_rect), 1)
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, wall.rect, 1)

        # HUD functions
        self.draw_player_mana(self.screen, 20, 20, self.player.mana / PLAYER_MANA)
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", 105, WHITE, ekplat / 2, ekgar / 2)

        if self.ended:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text(f"Tu nopelniji {self.current_points} punktus!", 65, WHITE, ekplat / 2, ekgar / 2)
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.ended = True
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LSHIFT:
                    if not self.started:
                        self.started = True
                        self.start_playing_snd.play()
                    if self.player.mana > PLAYER_MANA // 10 and not self.paused and not self.ended and not self.player.disabled:
                        self.player.gas = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_LSHIFT:
                    self.player.gas = False
            if event.type ==pg.MOUSEBUTTONDOWN:
                if self.ended:
                    self.playing = False

    def show_start_screen(self):
        pass
        

# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
