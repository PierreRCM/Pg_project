import pandas as pd

weapon_data = pd.DataFrame(index=["speed", "range", "damage", "accuracy", "reloading_time", "loader", "rate"],
                           columns=["Gun"])
weapon_data["Gun"]["speed"] = 350
weapon_data["Gun"]["range"] = 400
weapon_data["Gun"]["damage"] = 15
weapon_data["Gun"]["accuracy"] = 10
weapon_data["Gun"]["reloading_time"] = 1
weapon_data["Gun"]["loader"] = 10
weapon_data["Gun"]["rate"] = 2


class Potion:

    def __init__(self, p_type):

        self.all_type = ["hp"]
        self.p_type = p_type

    def use(self, player_carac):

        if self.p_type["hp"]:

            player_carac["hp"] += player_carac["hp_max"] * 0.5

            if player_carac["hp"] > player_carac["hp_max"]:

                player_carac["hp"] = player_carac["hp_max"]


class Weapon:

    def __init__(self, name):

        self.name = name
        self.rate = self._set_stat("rate")
        self.range = self._set_stat("range")
        self.damage = self._set_stat("damage")
        self.speed = self._set_stat("speed")
        self.accuracy = self._set_stat("accuracy")
        self.reloading_time = self._set_stat("reloading_time")
        self.loader = self._set_stat("loader")

    def _set_stat(self, key):

        global weapon_data

        return weapon_data[self.name][key]
