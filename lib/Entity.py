import pygame as pg
from weapon import Weapon
import numpy as np
import os
from pygame.locals import *
from pyganim import getImagesFromSpriteSheet
from image_data import image_data_original
pg.init()
print(os.getcwd())

class Bullet(pg.sprite.Sprite):

    def __init__(self, name, direction, position, range_, damage, speed, tick):

        self.owner = name  # Used for collision
        self.image = "Bullet"
        self.my_image = self._init_image()
        self.my_image.set_colorkey((255, 255, 255))
        image_data_original[self.image].set_colorkey((255, 255, 255))
        self.rect = pg.Rect((position[0], position[1]), image_data_original[self.image].get_size())
        # Depend on the weapon characteristics
        self._attr = {"direction": direction - 90, "reference": 270, "init_position": position.copy(),
                      "position": position.copy(), "distance_traveled": 0, "speed": speed,
                      "damage": damage, "tick": tick,  # todo: set real tick time of the loop
                      "range": range_, "alive": True, "border": False, "hit": False}

        self._rotate()

        pg.sprite.Sprite.__init__(self)

    def get_attr(self, variable):
        """input string variable,
           find in dictionnary self._attr argument required
           output depend of variable asked"""
        return self._attr[variable]

    def _move(self):
        """move the bullet, shift 90 deg because 0 stand for 90 """
        self._attr["position"][0] += np.cos((self._attr["direction"] + 90) * np.pi / 180) * self._attr["speed"] * self._attr["tick"]
        self._attr["position"][1] += np.sin(-(self._attr["direction"] + 90) * np.pi / 180) * self._attr["speed"] * self._attr["tick"]

        self._attr["distance_traveled"] += self._attr["speed"] * self._attr["tick"]

        # get distance travelled by the sprite so we can remove when it's superior to the range of the spell

    def update(self):
        """First we move the spell then the rectangle"""

        self._move()

        center_image = image_data_original[self.image].get_rect().center
        self.rect = pg.Rect((self._attr["position"][0] - center_image[0],  # so we can position our rectangle
                             self._attr["position"][1] - center_image[1]), image_data_original[self.image].get_size())
        self._outrange()
        self._outborder()

    def _rotate(self):
        """input newdirection in degree
           rotate the image in subtracting by the reference (position of picture)"""

        self.my_image = pg.transform.rotate(image_data_original[self.image],
                                                     (self._attr["direction"] - self._attr["reference"]))

        self._attr["reference"] = self._attr["direction"]

    def _outrange(self):

        if self._attr["distance_traveled"] >= self._attr["range"]:

            self._attr["alive"] = False

    def _outborder(self):

        if self._attr["border"]:

            self._attr["alive"] = False

    def set_attr(self, key, value):

        self._attr[key] = value

    def _init_image(self):

        global image_data_original

        image_data_original[self.image] = pg.image.load(os.getcwd() + "/picture/bullet.png").convert()

        return pg.image.load(os.getcwd() + "/picture/bullet.png").convert()


class Player(pg.sprite.Sprite):

    def __init__(self):

        self.name = "Player1"
        self.image = "Player"  # image that ll be blit
        self.my_image = self._init_image()
        self.my_image.set_colorkey((255, 255, 255))
        image_data_original[self.image].set_colorkey((255, 255, 255))  # Set image transparence
        self.rect = image_data_original[self.image].get_rect()  # called when updating sprite
        self.weapon = Weapon("Gun")
        self.shortcut = {"up": K_z, "down": K_s, "left": K_q, "right": K_d, "shoot": K_e}
        self.last_shot = pg.time.get_ticks()
        self._attr = {"reference": 270, "position": [80, 80], "old_position": [10, 10], "speed": 180, "hp": 100,
                      "alive": True, "border": False, "mouse": [0, 0], "direction": 0,
                      "tick": pg.time.Clock().tick(60)/1000, "money": 0, "hp_max": 100, "hit": False,
                      "damage": self.weapon.damage, "rate": self.weapon.rate}

        self.all_bonus = []
        self.shot_ready = True
        self.fire = False
        self.keys = pg.key.get_pressed()
        pg.sprite.Sprite.__init__(self)

    def check_bonus(self):

        if len(self.all_bonus) != 0:

            for bonus in self.all_bonus:

                if bonus.get_attr("time") == 0:

                    self._attr[bonus.get_attr("bonus_type")] = self._attr[bonus.get_attr("bonus_type")] * bonus.get_attr('multiplicateur')

                if bonus.check_timer():

                    self._attr[bonus.get_attr("bonus_type")] = int(self._attr[bonus.get_attr("bonus_type")] / bonus.get_attr('multiplicateur'))

                    self.all_bonus.remove(bonus)

    def add_bonus(self, bonus):

        if bonus.bonus_type in [i.bonus_type for i in self.all_bonus]:

            for a_bonus in self.all_bonus:
                if a_bonus.bonus_type == bonus.bonus_type:
                    a_bonus.set_attr("time", 10)
                    self.all_bonus.append(bonus)
                    break

        else:

            self.all_bonus.append(bonus)

    def _move(self, vx, vy):
        """input time between last call of clock.tick()
           compute the distance in pixel/second"""
        if vx != 0 and vy != 0:

            vx = np.cos(np.pi/4)*vx
            vy = np.cos(np.pi/4)*vy

        if not self._attr["border"]:

            self._attr["old_position"] = self._attr["position"].copy()
            self._attr["position"][0] += (vx*self._attr["tick"])
            self._attr["position"][1] += (vy*self._attr["tick"])

        else:

            self._attr["position"] = self._attr["old_position"].copy()

    def get_attr(self, variable):
        """input string variable,
           find in dictionary self._attr argument required
           output depend of variable asked"""

        return self._attr[variable]

    def set_attr(self, variable, value):

        self._attr[variable] = value

    def update(self):
        """Update new rectangle"""

        self._rotate()
        center_image = image_data_original[self.image].get_rect().center  # center of our rotated image,
        self.rect = pg.Rect((self._attr["position"][0] - center_image[0],  # so we can position our rectangle
                             self._attr["position"][1] - center_image[1]), image_data_original[self.image].get_size())

    def _cooldown_shot(self):
        """ Check difference between now and last shot, depend on the weapon's rate """

        now = pg.time.get_ticks()

        if (now - self.last_shot)/1000 >= (1/self._attr["rate"]):

            self.last_shot = now

            self.shot_ready = True

        else:

            self.shot_ready = False

    def _rotate(self):
        """Rotate the image in calculating the the angle, between mouse position and player position"""

        deltax = self._attr["mouse"][0] - self._attr["position"][0]
        deltay = self._attr["mouse"][1] - self._attr["position"][1]
        # difference of position between position of sprite and mouse position
        self._attr["direction"] = np.arctan2(deltax, deltay) * 180 / np.pi + self._attr["reference"]

        self.my_image = pg.transform.rotate(image_data_original[self.image],
                                            (self._attr["direction"] - self._attr["reference"]))

    def create_bullet(self):
        """return a bullet instance"""

        new_bullet = Bullet(self.name, self._attr["direction"], self._attr["position"], self.weapon.range,
                            self._attr["damage"], self.weapon.speed, self._attr["tick"])  # get_attr method for weapon
        self.fire = False

        return new_bullet

    def check_inputs(self):

        vx = 0
        vy = 0

        if self.keys[self.shortcut["up"]]:

            vy = -self._attr["speed"]

        elif self.keys[self.shortcut["down"]]:

            vy = self._attr["speed"]

        if self.keys[self.shortcut["left"]]:

            vx = -self._attr["speed"]

        elif self.keys[self.shortcut["right"]]:

            vx = self._attr["speed"]

        if self.keys[self.shortcut["shoot"]]:

            self.fire = True
            self._cooldown_shot()

        self._move(vx, vy)

    def _init_image(self):

        global image_data_original

        image_data_original[self.image] = pg.image.load(os.getcwd() + "/picture/player.png").convert()

        return pg.image.load(os.getcwd() + "/picture/player.png").convert()


class Enemy(pg.sprite.Sprite):  # TODO: Create an entity class, and different enemy, different IA

    def __init__(self, player, carac):

        self.name = ""
        self.image = "Enemy"  # image that ll be blit
        self.my_image = self._init_image()
        self.target = player
        self.all_images = getImagesFromSpriteSheet(os.getcwd() + "/picture/sprite_monster1.png", rows=2, cols=3)

        self.my_image.set_colorkey((255, 255, 255))
        image_data_original[self.image].set_colorkey((255, 255, 255))  # Set image transparence
        self.rect = image_data_original[self.image].get_rect()  # called when updating sprite
        self.last_shot = pg.time.get_ticks()
        self._attr = {"reference": 270, "position": [carac["pos"][0], carac["pos"][1]], "old_position": [10, 10],
                      "speed": carac["speed"], "hp": carac["hp"], "alive": True, "border": False, "direction": 0,
                      "tick": pg.time.Clock().tick(60)/1000, "rate": carac["rate"], "damage": carac["damage"],
                      "range": carac["range"], "shot_speed": carac["shot_speed"], "hit": False,
                      "bonus_bool": carac["bonus_bool"], "bonus": carac["bonus"]}
        self.shot_ready = True
        self.fire = False
        pg.sprite.Sprite.__init__(self)

    def update(self):
        """Update new rectangle"""

        self._decision()
        self._cooldown_shot()
        self._shoot()
        center_image = image_data_original[self.image].get_rect().center  # center of our rotated image,
        self.rect = pg.Rect((self._attr["position"][0] - center_image[0],  # so we can position our rectangle
                             self._attr["position"][1] - center_image[1]), image_data_original[self.image].get_size())

    def create_bullet(self):
        """return a bullet instance"""

        new_bullet = Bullet(self.name, self._attr["direction"], self._attr["position"], self._attr["range"],
                            self._attr["damage"], self._attr["shot_speed"], self._attr["tick"])  # get_attr method for weapon
        self.fire = False

        return new_bullet

    def _init_image(self):

        global image_data_original

        image_data_original[self.image] = pg.image.load(os.getcwd() + "/picture/player.png").convert()

        return pg.image.load(os.getcwd() + "/picture/player.png").convert()

    def _decision(self):

        t_pos_x = self.target.get_attr("position")[0]
        t_pos_y = self.target.get_attr("position")[1]
        e_pos_x = self._attr["position"][0]
        e_pos_y = self._attr["position"][1]
        speed = self._attr["speed"]
        tick = self._attr["tick"]
        vx = np.cos(np.pi / 4) * speed
        vy = np.cos(np.pi / 4) * speed
        # 8 possible vectors for a movement
        dxl = (- speed * tick, 0)
        dxr = (speed * tick, 0)
        dyt = (0, - speed * tick)
        dyb = (0, speed * tick)
        ddbl = (- vx * tick, vy * tick)
        ddtl = (- vx * tick, - vy * tick)
        ddbr = (vx * tick, vy * tick)
        ddtr = (vx * tick, - vy * tick)

        distance = [dxl, dxr, dyt, dyb, ddtl, ddbl, ddbr, ddtr]

        norm = []

        for dist in distance:

            norm.append(np.sqrt((-t_pos_x + e_pos_x + dist[0])**2 + (-t_pos_y + e_pos_y + dist[1])**2))

        i_max = norm.index(min(norm))

        self._attr["position"][0] += distance[i_max][0]
        self._attr["position"][1] += distance[i_max][1]

    def _shoot(self):

        norm = np.sqrt((self.target.get_attr("position")[0] - self._attr["position"][0])**2 +
                       (self.target.get_attr("position")[1] - self._attr["position"][1])**2)
        if norm < self._attr["range"]:
            self._direction_shot()
            self.fire = True

    def _cooldown_shot(self):
        """ Check difference between now and last shot, depend on the weapon's rate """

        now = pg.time.get_ticks()

        if (now - self.last_shot)/1000 >= self._attr["rate"]:

            self.last_shot = now

            self.shot_ready = True

        else:

            self.shot_ready = False

    def get_attr(self, variable):
        """input string variable,
           find in dictionary self._attr argument required
           output depend of variable asked"""

        return self._attr[variable]

    def set_attr(self, variable, value):

        self._attr[variable] = value

    def _direction_shot(self):

        deltax = self.target.get_attr("position")[0] - self._attr["position"][0]
        deltay = self.target.get_attr("position")[1] - self._attr["position"][1]
        # difference of position between position of sprite and mouse position
        self._attr["direction"] = np.arctan2(deltax, deltay) * 180 / np.pi + self._attr["reference"]

