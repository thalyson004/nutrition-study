from dataclasses import dataclass
from copy import deepcopy
from typing import Union
from typing import Any

from app.components.extract_data.dataframes.dictionaries.nutrients import (
    nutrients,
    nutrients_signal,
)


@dataclass
class Nutrition:
    from .state import State

    def __init__(self, state: Union[State, any] = None):
        """
        State: A state with quanties of food or a dictionary with the nutrition quantity

        return: A nutrition
        """
        from .state import State
        from app.components.basic_dataframes import dictNutritionByMeal

        if isinstance(state, State):
            self.data = {key: 0.0 for key in list(nutrients)}

            for code in list(state.keys()):  # Meals code
                for nutrient in list(self):  # Nutrient code
                    self.data[nutrient] += (
                        dictNutritionByMeal[code][nutrient] * state[code]
                    )
        elif type(state) is dict:
            self.data = deepcopy(state)
        else:
            self.data = {key: 0 for key in list(nutrients)}

    def keys(self):
        return list(self.data)

    def values(self):
        return list(self.data.values())

    def change(self, nutritionCode: str, quantity: float):
        newState = deepcopy(self)
        newState[nutritionCode] += quantity
        return newState

    @staticmethod
    def keys() -> list:
        return list(nutrients)

    @staticmethod
    def getDictNutrition(state: State) -> dict:
        """TODO: Describe the function"""
        return Nutrition(state).data

    @staticmethod
    def idealNutritionByEer(eer: float = None):
        """Given the EER factor, retuns a dictionary with the right nutrition

        Args:
            eer (float): EER factor

        Returns:
            nutrition dictionary (dict): Dictionary with the right nutrition of each nutrient for a specific person with EER factor

        """
        # TODO: Define the right quantities
        # FROM Eliseu 2020
        nutrients_quantiy = {
            "ENERGIA_KCAL": eer if eer != None else 50,
            "CHOTOT": (eer * (55 / 100) if eer != None else 50) / 4,  # 55-75 eer
            "PTN": (eer * (10 / 100) if eer != None else 50) / 4,  # 10-15 eer
            "LIP": (eer * (15 / 100) if eer != None else 50) / 9.0,  # 15–30 eer
            "FIBRA": 31,
            "COLEST": 300.0,
            "CALCIO": 868,
            "AGTRANS": (eer * (1.0 / 100.0) if eer != None else 50) / 9.0,
            "AGSAT": (eer * (10.0 / 100.0) if eer != None else 50) / 9.0,
            "AGPOLI": (eer * (6 / 100) if eer != None else 50) / 9.0,  # 6-10 err
            "SODIO": 2000,  # World Health Organization (WHO) recommendation
            "POTASSIO": 3510,
            "FERRO": 6.8,
            "MAGNESIO": 303,
            "TIAMINA": 0.9,
            "RIBOFLAVINA": 1,
            "PIRIDOXAMINA": 1.1,
            "NIACINA": 11.5,
            "COBALAMINA": 2,
            "VITC": 66.1,
            "VITA_RAE": 560,
            "COBRE": 0.7,
            "FOLATO": 322,
            "FOSFORO": 649,
            "ZINCO": 8,
            # "FRUIT": 400
            # "FISH": 43,
            # "SUGAR": (-1) * (-1) * (eer * (5 / 100) if eer != None else 50),  # 5 err,
        }

        return Nutrition(nutrients_quantiy)

    # TODO: Fix idealNutritionByPersonId to be used be a group of people
    @staticmethod
    def idealNutritionByPersonId(personId: str = None):
        from app.components.basic_dataframes import dictPersonEer

        if isinstance(personId, list) and len(personId) == 1:
            personId = personId[0]

        try:
            return Nutrition.idealNutritionByEer(dictPersonEer[personId])
        except:
            return Nutrition.idealNutritionByEer(2388.8400)

    @staticmethod
    def nutritionAdequancyByPersonId(nutrition: "Nutrition", personID: str):
        idealNutrition = Nutrition.idealNutritionByPersonId(personID)
        greaters = [
            nutrient for nutrient, signal in nutrients_signal.items() if signal == ">"
        ]
        less = [
            nutrient for nutrient, signal in nutrients_signal.items() if signal == "<"
        ]
        quantity = len(nutrients_signal) - 1

        adequancy = 0.0
        for nutrient in greaters:
            adequancy += (
                min(1.0, nutrition[nutrient] / idealNutrition[nutrient]) / quantity
            )

        for nutrient in less:
            if nutrient == "ENERGIA_KCAL":
                continue
            adequancy += (
                1.0 if nutrition[nutrient] <= idealNutrition[nutrient] else 0.0
            ) / quantity

        return adequancy

    @staticmethod
    def directionDifference(initNutrition, finalNutrition):
        initNutrition: Nutrition = initNutrition
        finalNutrition: Nutrition = finalNutrition

        data = {
            key: (finalNutrition[key] - initNutrition[key])
            for key in list(initNutrition)
        }
        return Nutrition(data)

    @staticmethod
    # TODO: Use signal
    def absDifference(initNutrition: "Nutrition", finalNutrition: "Nutrition") -> float:

        return sum(
            [
                abs((initNutrition[key] - finalNutrition[key])) / finalNutrition[key]
                for key in list(initNutrition)
            ]
        )

    @staticmethod
    # works fine with 1007
    def absDifferenceNegativePenalty(
        initNutrition, finalNutrition, mult=50007
    ) -> float:
        initNutrition: Nutrition = initNutrition
        finalNutrition: Nutrition = finalNutrition

        def calc(init: float, final: float, signal: str):
            if signal == ">":
                if init <= final:
                    return abs(init - final) * mult
                else:
                    # TODO: Try fix the energy
                    if init / final > 1.5:
                        # return abs(init - final) * mult
                        return abs(init - final)
                    else:
                        return abs(init - final)
            else:
                if init <= final:
                    return 0.0
                else:
                    return abs(init - final) * mult

        return sum(
            [
                (
                    calc(initNutrition[key], finalNutrition[key], nutrients_signal[key])
                    / finalNutrition[key]
                )
                for key in list(initNutrition)
            ]
        )

    @staticmethod
    # TODO: Use signal
    def distanceDifference(
        initNutrition,
        finalNutrition,
    ) -> float:
        initNutrition: Nutrition = initNutrition
        finalNutrition: Nutrition = finalNutrition

        return sum(
            [
                (
                    (initNutrition[key] - finalNutrition[key])
                    * (initNutrition[key] - finalNutrition[key])
                )
                / (finalNutrition[key] * finalNutrition[key])
                for key in list(initNutrition)
            ]
        )

    def distance() -> dict:
        return 0

    def __iter__(self):
        return iter(self.data)

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        return self.data[index]

    def __add__(self, temp):
        if self == None:
            return temp
        if temp == None:
            return self

        nutrition = Nutrition()
        for nutrient in list(nutrition):
            nutrition[nutrient] = self[nutrient] + temp[nutrient]

        return nutrition

    def __truediv__(self, divValue):
        if isinstance(divValue, int) or isinstance(divValue, float):
            nutrition = Nutrition()
            for nutrientKey, nutrientValue in self.data.items():
                nutrition[nutrientKey] = nutrientValue / divValue
            return nutrition
        else:
            raise TypeError("Unsupported operand type(s)")

    def __str__(self):
        return f"Nutrition: {self.data}"
