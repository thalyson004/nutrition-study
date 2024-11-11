from dataclasses import dataclass
from typing import List
from app.components.basic_dataframes import (
    mealCodeList,
    dictNutritionByMeal,
)
from app.components.extract_data.dataframes.dictionaries.nutrients import nutrients
from app.components.simple_types import Nutrition, State
import random
from IPython.display import clear_output
from pandas import DataFrame
import numpy as np
import df2img
import seaborn as sns
import matplotlib.pyplot as plt

from app.components.extract_data.extract_data import (
    getDictPersonIdStrata,
    getDictStrataMeals,
)


@dataclass
class SearchResult:
    # personIDs: list[str]=[]
    # initialMeal:State=None,
    # finalMeal:State=None,
    # initialNutrition:Nutrition=None
    # finalNutrition:Nutrition=None

    def __init__(
        self,
        personIDs: list[str] = [],
        initialMeal: State = None,
        finalMeal: State = None,
    ):
        self.personIDs = personIDs
        self.initialMeal = initialMeal
        self.finalMeal = finalMeal
        self.initialNutrition = None
        self.finalNutrition = None

        if initialMeal:
            self.initialNutrition = Nutrition(initialMeal)
        else:
            self.initialNutrition = Nutrition()

        if finalMeal:
            self.finalNutrition = Nutrition(finalMeal)
        else:
            self.finalNutrition = Nutrition()

    def get_df(self):

        data = {}
        data["Nutrient"] = [nutrient for nutrient in list(self.initialNutrition)]
        data["Initial Value"] = [round(x, 2) for x in self.initialNutrition.values()]
        data["Final Value"] = [round(x, 2) for x in self.finalNutrition.values()]

        targetNutrition = Nutrition.idealNutritionByPersonId(self.personIDs)

        # TODO: Use correct personID
        data["Target Value"] = targetNutrition.values()

        df = DataFrame(
            data=data,
            # index=list(self.initialNutrition),
        )

        for nutrient in ["CHOTOT", "PTN", "LIP", "AGTRANS", "AGSAT", "AGPOLI"]:
            df.loc[df["Nutrient"] == nutrient, "Initial Value"] = 100 * (
                self.initialNutrition[nutrient] / targetNutrition["ENERGIA_KCAL"]
            )

        for nutrient in ["CHOTOT", "PTN", "LIP", "AGTRANS", "AGSAT", "AGPOLI"]:
            df.loc[df["Nutrient"] == nutrient, "Final Value"] = 100 * (
                self.finalNutrition[nutrient] / targetNutrition["ENERGIA_KCAL"]
            )

        for nutrient in ["CHOTOT", "PTN", "LIP", "AGTRANS", "AGSAT", "AGPOLI"]:
            df.loc[df["Nutrient"] == nutrient, "Target Value"] = 100 * (
                targetNutrition[nutrient] / targetNutrition["ENERGIA_KCAL"]
            )

        # df.set_index("Nutrients")

        return df

    def get_df_grouping(self):

        nutrient = []
        status = []
        value = []

        target = Nutrition.idealNutritionByPersonId(self.personIDs)

        for state, nutrition in [
            ("initial", self.initialNutrition),
            ("final", self.finalNutrition),
        ]:

            for temp in list(self.initialNutrition):
                nutrient.append(temp)
                status.append(state)
                value.append(min(2.0, nutrition[temp] / target[temp]))

        data = {}
        data["nutrient"] = nutrient
        data["status"] = status
        data["value"] = value

        df = DataFrame(
            data=data,
        )

        return df

    def show_comparison_graph(self, path="", title="Search Result") -> sns.FacetGrid:
        df = self.get_df_grouping()
        g = sns.catplot(
            data=df,
            x="value",
            y="nutrient",
            hue="status",
            kind="bar",
            palette="pastel",
            edgecolor=".6",
        )

        plt.axvline(x=1)

        plt.show()

        return g

    def save_as_xls(self, path: str):
        df = self.get_df()
        df.to_excel(f"{path}.xlsx", engine="xlsxwriter")
        return df

    def save_as_png(self, path: str, title="Search Result"):
        fig = df2img.plot_dataframe(
            self.get_df(),
            title=dict(
                font_color="black",
                font_family="Times New Roman",
                font_size=16,
                text=title,
            ),
            tbl_header=dict(
                align="center",
                fill_color="blue",
                font_color="white",
                font_size=14,
                line_color="darkslategray",
                font_family="Times New Roman",
            ),
            tbl_cells=dict(
                align="center",
                font_size=14,
                line_color="darkslategray",
                font_family="Times New Roman",
            ),
            row_fill_color=("#ffffff", "#d7d8d6"),
            fig_size=(1200, 550),
        )

        df2img.save_dataframe(fig=fig, filename=f"{path}.png")

    def __str__(self):
        return f"""initialMeal {self.initialMeal}
initialNutrition {self.initialNutrition}
finalMeal {self.finalMeal}
finalNutrition {self.finalNutrition}
        """

    def __add__(self, temp):
        resultSum = SearchResult()

        resultSum.initialMeal = self.initialMeal + temp.initialMeal
        resultSum.finalMeal = self.finalMeal + temp.finalMeal
        resultSum.initialNutrition = self.initialNutrition + temp.initialNutrition
        resultSum.finalNutrition = self.finalNutrition + temp.finalNutrition

        return resultSum

    def __truediv__(self, divValue):
        if isinstance(divValue, int) or isinstance(divValue, float):
            resultDiv = SearchResult()

            resultDiv.initialMeal = self.initialMeal / divValue
            resultDiv.finalMeal = self.finalMeal / divValue
            resultDiv.initialNutrition = self.initialNutrition / divValue
            resultDiv.finalNutrition = self.finalNutrition / divValue

            return resultDiv
        else:
            raise TypeError("Unsupported operand type(s)")


def cosine_similarity(array1, array2):
    dot_product = np.dot(array1, array2)
    magnitude1 = np.linalg.norm(array1)
    magnitude2 = np.linalg.norm(array2)

    similarity = dot_product / (magnitude1 * magnitude2)

    return similarity


def papaSingleSeach(
    personID: str,
    unit=10,
    max_unit=5,
    max_population_set=100,
    max_population_selected=50,
    expansion_set=10,
    expansion_select=3,
    max_steps=100,
    verbose=False,
    fitness=Nutrition.absDifference,
    preselect: list[str] = ["Strata"],
) -> SearchResult:
    """Algorithm
    K: number of moviments for each expansion
    D: Vector difference between the ideal and actual nutrition
    """

    # Config
    UNIT = unit  # Quantity of grams using in an step
    MAX_UNIT = max_unit  # Max units added of removed by one step

    MAX_POPULATION_SET = (
        max_population_set  # Quantity of leaves nodes that will be random selected
    )
    MAX_POPULATION_SELECT = (
        max_population_selected  # Quantity of leaves nodes that was random selected
    )

    EXPANSION_SET = (
        expansion_set  # Quantity of good steps that have been selected to be an option
    )
    EXPANSION_SELECT = (
        expansion_select  # Quantity of good steps that have been selected to apply
    )

    MAX_STEPS = max_steps  # Maximum number of modifications

    # Init a set of states
    initialState = State.getStateByPersonId(personID)
    population: list[State] = [initialState]

    # Define target nutrition
    targetNutrition = Nutrition.idealNutritionByPersonId(personID)

    mealList = []

    if len(preselect) == 0:
        mealList = mealCodeList

    if preselect.count("Strata"):
        strata = getDictPersonIdStrata().get(personID, None)

        if strata == None:
            strata = random.choice(list(set(getDictPersonIdStrata().values())))

        mealList = getDictStrataMeals()[strata]

    # Start search
    for i in range(1, MAX_STEPS + 1):
        if verbose:
            clear_output(wait=True)
            print(f"Step {i}: ")

        newPopulation = []
        # For each state
        for state in population:
            # Get the difference vector between ideal and actual state (D vector)
            stateNutrition = Nutrition(state)
            # direction = Nutrition.directionDifference(stateNutrition, targetNutrition)
            # print("direction: ", direction)

            # Test increase and decrease each meal
            options = []  # Init the options of steps as an empty array

            for mealCode in mealList:
                for signal in [-1, 1]:  # Try remove and add

                    # # TODO: GAMBI
                    # if mealCode == "C0007K" and signal == 1:
                    #     continue

                    for times in range(1, MAX_UNIT + 1):

                        factor: float = float(times) * UNIT * float(signal)

                        # zero the meal
                        if factor <= 0:
                            factor = max(factor, -state[mealCode])

                        # Set a maximum quantity for one meal
                        maximum = 400.0
                        if state[mealCode] + factor >= maximum:
                            factor = min(factor, state[mealCode] - maximum)

                        if factor == 0:
                            continue

                        # Calc similatiry between mealDirection and direction
                        # To calculate similarity, cosine similarity was employed. (-1,1).
                        # stepDirection = {
                        #     nutritionCode: nutritionQuantity*factor for nutritionCode, nutritionQuantity in dictNutritionByMeal[mealCode].items()}
                        # similarity = cosine_similarity(list(stepDirection.values()), direction.values())

                        # Calc stepNutrition

                        stepNutrition = Nutrition(stateNutrition.data)  # O(len(meals))

                        for nutrient in list(nutrients):
                            stepNutrition[nutrient] += (
                                dictNutritionByMeal[mealCode][nutrient] * factor
                            )

                        # Calc using fitness function
                        similarity = fitness(
                            stepNutrition,
                            targetNutrition,
                        )  # O(len(nutrients))

                        # Store tuple (similarity: float, mealCode: str, factor:float) into options.
                        options.append((similarity, mealCode, factor))

            # Rank each possible  between
            options.sort(reverse=False)

            # Select EXPANSION_SELECT options to expand between EXPANSION_SET better options
            options = options[: min(EXPANSION_SET, len(options))]
            random.shuffle(options)
            options = options[: min(EXPANSION_SELECT, len(options))]

            # print("Options:", options)

            # Expand the state using the K best moviments
            selectedOptions = []
            population.clear()

            for option in options:
                newState = state.change(option[1], option[2])  # (mealCode, factor)
                selectedOptions.append(newState)

            # Rank the population using module difference SUM ((Ni - Nt)/Nt)
            newPopulation = newPopulation + [
                (
                    fitness(
                        Nutrition(solution),
                        targetNutrition,
                    ),
                    solution,
                )
                for solution in selectedOptions
            ]

        if verbose:
            print(
                "Best fitness: ",
                min([distance for distance, solution in newPopulation]),
            )

        newPopulation.sort(reverse=False)
        newPopulation = newPopulation[: min(MAX_POPULATION_SET, len(newPopulation))]
        random.shuffle(newPopulation)

        newPopulation.sort(reverse=False)
        newPopulation = [
            person
            for (x, person) in newPopulation[
                : min(MAX_POPULATION_SELECT, len(newPopulation))
            ]
        ]

        population = newPopulation

    if verbose:
        print("initialState: ", initialState)
        print("Population[0]: ", population[0])

        for meal in list(initialState.data):
            if initialState[meal] != population[0][meal]:
                print(
                    meal,
                    "- Init:",
                    initialState[meal],
                    " / Final:",
                    population[0][meal],
                )

    return SearchResult([personID], initialState, population[0])


def papaSearch(
    personIDs: List[str],
    unit=10,
    max_unit=5,
    max_population_set=100,
    max_population_selected=50,
    expansion_set=10,
    expansion_select=3,
    max_steps=100,
    verbose=False,
) -> SearchResult:

    result = SearchResult()

    for index, personID in enumerate(personIDs):
        if verbose:
            print(index, "Init search from", personID)

        result = (
            papaSingleSeach(
                personID=personID,
                unit=unit,
                max_unit=max_unit,
                max_population_set=max_population_set,
                max_population_selected=max_population_selected,
                expansion_set=expansion_set,
                expansion_select=expansion_select,
                max_steps=max_steps,
                verbose=verbose,
            )
            + result
        )

    return result / len(personIDs)
