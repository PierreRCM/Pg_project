import pygame as pg
import os
from image_data import image_data_original
from Entity import Bullet


class Bonus(pg.sprite.Sprite):

    def __init__(self, clock):

        self.image = "Bonus"

        self.my_image = self._init_image()
        self.my_image.set_colorkey((255, 255, 255))
        self._attr = {"position": (0, 0), "display_time": 0, "available_time": 20}
        self.flags = {"alive": True}
        image_data_original[self.image].set_colorkey((255, 255, 255))  # Set image transparence
        self.rect = image_data_original[self.image].get_rect()  # called when updating sprite
        self.clock = clock
        pg.sprite.Sprite.__init__(self)

    def get_attr(self, variable):
        """input string variable,
           find in dictionary self._attr argument required
           output depend of variable asked"""

        return self._attr[variable]

    def update(self):
        """Update new rectangle"""

        self._attr["display_time"] += self.clock.get_time() / 1000
        center_image = image_data_original[self.image].get_rect().center  # center of our rotated image,
        self.rect = pg.Rect((self._attr["position"][0] - center_image[0],  # so we can position our rectangle
                             self._attr["position"][1] - center_image[1]), image_data_original[self.image].get_size())

    def set_attr(self, variable, value):

        self._attr[variable] = value

    def _init_image(self):

        global image_data_original

        image_data_original[self.image] = pg.image.load(os.getcwd() + "/picture/bonus.png").convert()
        return pg.image.load(os.getcwd() + "/picture/bonus.png").convert()


class BonusEnhance(Bonus):

    def __init__(self, number, clock):

        Bonus.__init__(self, clock)

        self.all_bonus = [("rate", 4), ("damage", 4), ("speed", 1.5)]
        self._attr = {"position": [0, 0], "alive": True, "time": 0, "max_time": 10,
                      "bonus_type": self.all_bonus[number][0], "multiplicateur": self.all_bonus[number][1],
                      "display_time": 0, "available_time": 20}

        self.bonus_type = self.all_bonus[number]
        self.last_call = 0

    def check_timer(self):

        self._attr["time"] += self.clock.get_time()/1000

        if self._attr["time"] >= self._attr["max_time"]:

            return True
        else:
            return False


class BonusNova(Bonus):

    def __init__(self, player, clock):
        Bonus.__init__(self, clock)
        self._attr = {"position": [0, 0], "alive": True, "display_time": 0, "available_time": 20,
                      "damage": player.get_attr("damage"), "number": 30}

        self.bullets = self._create_bullet(player)

    def _create_bullet(self, player):

        angle = 0
        bullets = list()

        for i in range(self._attr["number"]):

            bullet = Bullet(player.name, angle, self._attr["position"], 2000,
                            player.get_attr("damage"), player.weapon.speed, player.get_attr("tick"))

            angle += 360 / self.get_attr("number")  # add angle depending on the number of bullet
            bullets.append(bullet)

        return bullets





