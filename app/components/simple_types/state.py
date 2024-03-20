from dataclasses import dataclass
from copy import deepcopy
from app.components.basic_dataframes import mealCodeList


@dataclass
class State:
    data: dict = None

    def __getitem__(self, index):
        return self.data[index]

    def __init__(self, data=None):
        if data == None:
            self.data = {key: 0 for key in mealCodeList}
        else:
            self.data = data

    def __setitem__(self, index, value):
        self.data[index] = value

    def keys(self):
        return self.data.keys()

    def nutrition(self) -> dict:
        from .nutrition import Nutrition

        return Nutrition(self)

    def change(self, mealCode: str, quantity: float):
        newState = deepcopy(self)
        newState[mealCode] += quantity
        return newState

    @staticmethod
    def getStateByPersonId(personId: str):
        from app.components.basic_dataframes import dictMealState

        return State(dictMealState[personId])

    def __lt__(self, other):
        if isinstance(other, State):
            return False

        return NotImplemented

    def __add__(self, temp):
        stateSum = State()
        for key in mealCodeList:
            stateSum[key] = self[key] + temp[key]

        return stateSum
