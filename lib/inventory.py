import pygame as pg


class Inventory:

    def __init__(self):

        self.slot = 3
        self.items = list()

    def kill(self, i):

        self.items.pop(i)

    def