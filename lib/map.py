import pygame as pg
from pygame.locals import *
import os
import Entity as en
import bonus as b
from image_data import convert_images
pg.init()
pg.font.init()


class Map:

    def __init__(self, groupe_dict):

        self.image = pg.image.load(os.getcwd() + "/picture/map.png").convert()
        self.rect = self.image.get_rect()
        self.groupe_dict = groupe_dict  # Actually contain 2 sprite groupe keys Bullets and Players
        self.player = groupe_dict["Entity"].sprites()[0]
        self.screen_stuff = list()
        self.enemy_to_unpack = list()
        self.enemy_ready = True
        self.last_enemy = 0
        self.border_width = 30

    def update(self):
        """Call update method for all sprites"""
        self._check_alive()

        for groupe in self.groupe_dict.values():

            groupe.update()

    def check_borders(self, screen_rect):
        """Check whether sprites collide with the borders, if it's True, set border arguments"""

        for groupe in self.groupe_dict.values():
            for sprite in groupe.sprites():

                # image = sprite.image.get_size() #  HAVE TO USED TO SHIFT FOR LARGE SPRITE, FOR ACCURATE BORDERS

                if sprite.get_attr("position")[0] + sprite.rect.w + self.border_width >= screen_rect[0]:

                    sprite.flags["border"] = True

                elif sprite.get_attr("position")[0] - self.border_width <= 0:

                    sprite.flags["border"] = True

                elif sprite.get_attr("position")[1] + sprite.rect.h - self.border_width >= screen_rect[1]:

                    sprite.flags["border"] = True

                elif sprite.get_attr("position")[1] - sprite.rect.h - self.border_width <= 0:

                    sprite.flags["border"] = True

                else:

                    sprite.flags["border"] = False

    def render(self, screen):

        screen.blit(self.image, self.rect)
        for groupe in self.groupe_dict.values():
            for sprite in groupe.sprites():

                screen.blit(sprite.my_image, sprite.rect)

    def render_screen_stuff(self, screen):

        for stuff in self.screen_stuff:

            screen.blit(stuff[0], stuff[1])
            self.screen_stuff.remove(stuff)

    def check_shot(self):
        """input player instance check whether the player create a sprite, add it to the map"""

        for sprite in self.groupe_dict["Entity"].sprites():

            if sprite.flags["fire"] and sprite.flags["shot_ready"]:

                a_bullet = sprite.create_bullet()
                self.groupe_dict["Bullets"].add(a_bullet)
                sprite.flags["fire"] = False

    def _check_alive(self):
        """Check whether each sprites is alive remove them if it's not the case"""

        for groupe in self.groupe_dict.values():
            for sprite in groupe.sprites():
                if not sprite.flags["alive"]:

                    groupe.remove(sprite)

    def generate_enemy(self, level):  # Todo deploy enemy, level generator create enemy, the map deploy it on the map

        if self._enemy_cooldown(level) and len(self.enemy_to_unpack) != 0:

            self.groupe_dict["Entity"].add(self.enemy_to_unpack.pop(0))

    def level_clear(self):
        """Check whether there are enemies to release and if enemies are still on the map"""

        if isinstance(self.groupe_dict["Entity"].sprites()[-1], en.Player) and len(self.enemy_to_unpack) == 0:
            return True
        else:
            return False

    def _enemy_cooldown(self, level):

        now = pg.time.get_ticks()

        if (now - self.last_enemy)/1000 >= 1:

            self.last_enemy = now

            return True

        else:

            return False

    def collision(self):
        """Test whether each players collide with bullets, deduce hp and kill sprite in case"""

        for sprite in self.groupe_dict["Entity"]:
            for i, bullet in enumerate(self.groupe_dict["Bullets"]):
                if (sprite.name is not bullet.owner) and (sprite.rect.colliderect(bullet)):

                    new_hp = sprite.get_attr("hp") - bullet.get_attr("damage")
                    sprite.set_attr("hp", new_hp)

                    self.player.flags["hit"] = True

                    if sprite.get_attr("hp") <= 0:

                        sprite.set_attr("hp", 0)
                        sprite.flags["alive"] = False

                        if isinstance(sprite, en.Enemy):
                            self.player.handle_xp(sprite.get_attr("xp"))

                            if sprite.flags["bonus_bool"]:

                                sprite.get_attr("bonus").set_attr("position", sprite.get_attr("position"))
                                self.groupe_dict["Bonus"].add(sprite.get_attr("bonus"))

                    self.groupe_dict["Bullets"].remove(bullet)

        for bonus in self.groupe_dict["Bonus"]:

            if bonus.get_attr("display_time") > bonus.get_attr("available_time"):

                bonus.flags["alive"] = False

            if self.player.rect.colliderect(bonus):

                if isinstance(bonus, b.BonusNova):

                    for bullet in bonus.bullets:
                        bullet.set_attr("position", bonus.get_attr("position").copy())

                    self.groupe_dict["Bullets"].add(bonus.bullets)

                else:
                    self.player.add_bonus(bonus)

                bonus.flags["alive"] = False


class Screen:

    def __init__(self):

        self.resolution = (1800, 900)
        self.res_playable = (1800, 860)
        self.screen = pg.display.set_mode(self.resolution)
        convert_images(en.Enemy.all_images)
        self.fullscreen = False
        self.game_name = pg.display.set_caption("CURRENTLY NONE")
        self.shortcut = {"FULLSCREEN": K_F1, "QUIT": K_ESCAPE} # we may create a menu when pressing a key
                                                               # so we can access to option/exit
                                                               # and handle it with mouse click
        self.window = True
        self.last_call = 0
        self.font_b_round = pg.font.SysFont("ubuntu", 40)
        self.timer = 1
        self.countdown_done = False
        self.font_2_display = self.font_b_round.render("Wave number : " + str(1) + "..." + str(self.timer) + "...",
                                                       0, (255, 255, 255))
        self.time_dic = {"xp": 0, "hit": 0, "levelup": 0}
        self.font_style = {"xp": ["+ ", 1, (0, 255, 0), 10, "xp", "ubuntu", []],
                           "levelup": ["Level", 1, (255, 255, 0), 25, "reached !", "ubuntu", []],
                           "hit": ["", 1, (255, 0, 0), 10, "", "ubuntu", []]}
        self.stuff_displayed = list()

    def check_input(self, inputs):

        if inputs[self.shortcut["FULLSCREEN"]]:

            if not self.fullscreen:

                pg.display.set_mode(self.res_playable, pg.FULLSCREEN)
                self.fullscreen = True

            else:

                pg.display.set_mode(self.res_playable)
                self.fullscreen = False

        if inputs[self.shortcut["QUIT"]]:

            self.window = False

    def new_wave_countdown(self, level):

        now = pg.time.get_ticks()
        font_pos = (self.res_playable[0] / 2 - self.font_2_display.get_rect().center[0],
                    self.res_playable[1] / 2 - self.font_2_display.get_rect().center[1])

        if (now - self.last_call) >= 1000:

            if self.timer != 0:

                self.font_2_display = self.font_b_round.render("Wave number : " + str(level) + "..." + str(self.timer)
                                                               + "...", 0, (255, 255, 255))
                self.timer -= 1
                self.last_call = now

            else:

                self.countdown_done = True
                self.timer += 3
                self.last_call = 0

            return self.font_2_display, font_pos

        else:

            return self.font_2_display, font_pos

    def draw_hp(self, player):
        """Create rect to display for interface"""

        hp_perc = player.get_attr("hp") / player.get_attr("hp_max")
        surf_hp_rect = pg.Surface((hp_perc * self.resolution[0], 20))
        surf_hp_rect.fill((255, 0, 0))

        return [(surf_hp_rect, (0, 0))]

    def game_over(self):
        """Create font to display for game over"""

        self.font_2_display = self.font_b_round.render("GAME OVER", 1, (255, 0, 0))
        font_pos = (self.res_playable[0] / 2 - self.font_2_display.get_rect().center[0],
                    self.res_playable[1] / 2 - self.font_2_display.get_rect().center[1])

        return [(self.font_2_display, font_pos)]

    def display(self, player, clock):

        for key in player.flags.keys():

            p_pos = player.get_attr("position")
            size = player.rect.size
            print(key, player.flags[key])
            if player.flags[key] and key in self.time_dic.keys():

                self.time_dic[key] += clock.get_time()
                font_style = pg.font.SysFont(self.font_style[key][5], self.font_style[key][3])

                stuff_to_displayed = font_style.render(self.font_style[key][0] + str(player.get_attr(key))
                                                       + self.font_style[key][4], self.font_style[key][1],
                                                       self.font_style[key][2])

                if self.time_dic[key] / 1000 < 1:

                    if not key == "levelup":

                        font_pos = (p_pos[0] + size[0], p_pos[1] - size[1]*len(self.stuff_displayed) - size[1])

                    else:
                        font_pos = (self.resolution[0] - stuff_to_displayed.get_width()[0], self.resolution[1]-100)

                    self.stuff_displayed.append((stuff_to_displayed, font_pos))

                else:

                    self.stuff_displayed.pop(0)
                    player.flags[key] = False
                    self.time_dic[key] = 0
        return self.stuff_displayed













