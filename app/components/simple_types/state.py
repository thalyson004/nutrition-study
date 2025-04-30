from dataclasses import dataclass
from copy import deepcopy
from app.components.basic_dataframes import mealCodeList
import random


@dataclass
class State:

    def __init__(self, data=None):
        self.data: dict = None

        if data == None:
            self.data = {key: 0 for key in mealCodeList}
            # self.data = {}
        else:
            self.data = deepcopy(data)

    def keys(self):
        return list(self.data)

    def nutrition(self) -> dict:
        from .nutrition import Nutrition

        return Nutrition(self)

    def copy(self) -> "State":
        return deepcopy(self)

    def change(self, mealCode: str, quantity: float):
        newState = deepcopy(self)

        # newState[mealCode] += quantity

        if mealCode in newState:
            newState.data[mealCode] += quantity
        else:
            newState.data[mealCode] = quantity

        return newState

    @staticmethod
    def crossover(state1: "State", state2: "State") -> list["State"]:
        states = [State(state1.data), State(state2.data)]
        for mealCode in state1.data:
            if random.random() >= 0.5:
                states[0][mealCode], states[1][mealCode] = (
                    states[1][mealCode],
                    states[0][mealCode],
                )

        return states

    @staticmethod
    def squareDifference(state1: "State", state2: "State") -> float:
        result = 0.0
        for mealCode in state1.data:
            result += pow(state1[mealCode] - state2[mealCode], 2.0)
        return result

    @staticmethod
    def getStateByPersonId(personId: str):
        from app.components.basic_dataframes import dictMealState

        try:
            return State(dictMealState[personId])
        except:
            return State()

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
        return key in list(self.data)
