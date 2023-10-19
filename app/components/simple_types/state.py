from dataclasses import dataclass

from app.components.basic_dataframes import mealCodeList


@dataclass
class State:
    data: dict = None

    def __getitem__(self, index):
        return self.data[index]

    def __init__(self):
        self.data = {key: 0 for key in mealCodeList}

    def __setitem__(self, index, value):
        self.data[index] = value

    def keys(self):
        return self.data.keys()

    def nutrition(self) -> dict:
        from .nutrition import Nutrition

        return Nutrition(self)
