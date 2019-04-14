import pygame as pg
import map as m
import Entity as en
from pygame.locals import *
from level_generator import LevelGenerator

pg.init()

pg.display.init()
pg.key.set_repeat(10, 10)


class Main:
    """ class to handle all input of the player
        might create an option to change shortcut """

    def __init__(self):

        self.screen = m.Screen()
        self.player = en.Player()
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(60) / 1000
        self.map = m.Map({"Entity": pg.sprite.Group(self.player), "Bullets": pg.sprite.Group(),
                          "Bonus": pg.sprite.Group()})
        self.input = pg.key.get_pressed()
        self.gameOn = True
        self.level = 1
        self.level_clear = False
        self.level_generated = False
        self.generator = LevelGenerator(self.player, self.level, self.screen.resolution, self.clock)

    def _set_mouse_motion(self):

        events = pg.event.get()  # Todo: pull only mouse event, to avoid for
        for event in events:
            if event.type == MOUSEMOTION:

                self.player.set_attr("mouse", list(pg.mouse.get_pos()))

    def _handle_level_state(self):

        sc_stuff = self.screen.draw_hp(self.player)
        sc_stuff.extend(self.screen.display_damage(self.player, self.clock))
        self.map.screen_stuff.extend(sc_stuff)

        if self.level_clear:

            self.level += 1
            self.generator.level += 1
            self.level_clear = False
            self.level_generated = False
            self.screen.countdown_done = False

        elif not self.level_generated:

            an_enemy, self.level_generated = self.generator.create_enemy()
            self.map.enemy_to_unpack.append(an_enemy)

        elif not self.screen.countdown_done:

            font_surface, font_pos = self.screen.new_wave_countdown(self.level)
            self.map.screen_stuff.append((font_surface, font_pos))

        elif not self.player.get_attr("alive"):

            font = self.screen.game_over()
            self.map.screen_stuff.extend(font)
        else:

            self.map.generate_enemy(self.level)
            self.level_clear = self.map.level_clear()

    def game_loop(self):

        while self.gameOn:
            self._handle_level_state()

            self.clock.tick(60)
            self._set_mouse_motion()
            self.player.keys = pg.key.get_pressed()
            self.player.check_inputs()  # todo: Try to find a way to avoid moving and rotation the player in this method
            self.player.check_bonus()
            self.input = pg.key.get_pressed()
            self.map.check_shot()  # Need player instance to check whether the player is shooting

            # self.level_clear = self.map.check_enemies Todo: method that check whether there are enemies still incoming

            # Updating / displaying on screen
            self.map.check_borders(self.screen.res_playable)

            self.map.collision()
            self.map.update()

            self.map.render(self.screen.screen)
            self.map.render_screen_stuff(self.screen.screen)
            self.screen.check_input(self.input)

            pg.display.update()
            pg.event.pump()
            self.gameOn = self.screen.window



main = Main()

main.game_loop()
