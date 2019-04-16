import pygame as pg
from Entity import Enemy
from numpy import random
import bonus as b
pg.init()


class LevelGenerator:

    def __init__(self, player, level, screen_res, clock):

        self.player = player
        self.level = level
        self.enemy_number = 0  # Todo: create different style of enemy
        self.enemy_send = 0
        self.screen_resolution = screen_res
        self.enemy_stat = dict()
        self._enemy_stat()
        self.clock = clock

    def _enemy_stat(self):

        # Todo: self level with a log function ?
        self.enemy_number = 1 * self.level
        rate = 1
        shot_speed = 250 + self.level
        speed = 50 + self.level
        range_a = 250
        damage = 5 * self.level
        hp = 50 * self.level
        xp = 5 * self.level

        self.enemy_stat = {"rate": rate, "shot_speed": shot_speed, "speed": speed, "tick": self.player.get_attr("tick"),
                           "range": range_a, "damage": damage, "hp": hp, "xp": xp, "bonus_bool": False, "bonus": None}

    def _create_bonus(self):

        number = random.randint(1, 40)
        bonus_enhance_nb = [1, 2, 3]

        if number in bonus_enhance_nb:
            self.enemy_stat["bonus_bool"] = True
            self.enemy_stat["bonus"] = b.BonusEnhance(random.randint(0, 3), self.clock)  # 1 to len(number of bonus

        elif number == 4:

            self.enemy_stat["bonus_bool"] = True
            self.enemy_stat["bonus"] = b.BonusNova(self.player, self.clock)
        else:
            self.enemy_stat["bonus_bool"] = False

    def create_enemy(self):

        posx = random.randint(100, self.screen_resolution[0])
        posy = random.randint(100, self.screen_resolution[1])
        self.enemy_stat["pos"] = [posx, posy]

        if self.enemy_send == self.enemy_number:
            level_generated = True
            self.enemy_send = 0

            an_enemy = Enemy(self.player, self.enemy_stat, self.clock)
            an_enemy.flags["alive"] = False
            self._enemy_stat()

        else:

            self._create_bonus()
            self.enemy_send += 1
            an_enemy = Enemy(self.player, self.enemy_stat, self.clock)
            level_generated = False

        return an_enemy, level_generated
