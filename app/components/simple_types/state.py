from dataclasses import dataclass
from copy import deepcopy
from app.components.basic_dataframes import mealCodeList


@dataclass
class State:

    def __init__(self, data=None):
        self.data: dict = None

        if data == None:
            # self.data = {key: 0 for key in mealCodeList}
            self.data = {}
        else:
            self.data = data

    def keys(self):
        return self.data.keys()

    def nutrition(self) -> dict:
        from .nutrition import Nutrition

        return Nutrition(self)

    def change(self, mealCode: str, quantity: float):
        newState = deepcopy(self)

        # newState[mealCode] += quantity

        if mealCode in newState:
            newState.data[mealCode] += quantity
        else:
            newState.data[mealCode] = quantity

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
        if self == None:
            return temp
        if temp == None:
            return self

        stateSum = State()
        for key in mealCodeList:
            stateSum[key] = self[key] + temp[key]

        return stateSum

    def __getitem__(self, index):
        return self.data.get(index, None)

    def __setitem__(self, index, value):
        self.data[index] = value

    def __truediv__(self, divValue):
        if isinstance(divValue, int) or isinstance(divValue, float):
            state = State()
            for mealKey, mealValue in self.data.items():
                state[mealKey] = mealValue / divValue

            return state
        else:
            raise TypeError("Unsupported operand type(s)")

    def __str__(self):
        return f"State: {self.data}"

    def __contains__(self, key):
        return key in self.data.keys()
