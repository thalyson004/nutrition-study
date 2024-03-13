from app.components.basic_dataframes import (
    dictMealState,
    mealCodeList,
    dictNutritionByMeal,
)
from app.components.simple_types import Nutrition, State
import random
from IPython.display import clear_output
from pandas import DataFrame
import numpy as np
import df2img


class SearchResult:
    def __init__(
        self,
        initialMeal=None,
        finalMeal=None,
    ):
        self.initialMeal = initialMeal
        self.finalMeal = finalMeal

        self.initialNutrition = None
        if initialMeal:
            self.initialNutrition = Nutrition(initialMeal)

        self.finalNutrition = None
        if finalMeal:
            self.finalNutrition = Nutrition(finalMeal)

    def get_df(self, personID=""):

        data = {}
        data["Initial Value"] = [round(x, 2) for x in self.initialNutrition.values()]
        data["Final Value"] = [round(x, 2) for x in self.initialNutrition.values()]

        # TODO: Use correct personID
        data["Target Value"] = Nutrition.idealNutritionByPersonId(
            "110000016.0#1.0#2.0#1.0"
        ).values()

        return DataFrame(
            data=data,
            index=self.initialNutrition.keys(),
        )

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
            fig_size=(800, 550),
        )

        df2img.save_dataframe(fig=fig, filename=f"{path}.png")


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
) -> SearchResult:

    # Config
    UNIT = unit  # Quantity of grams using in an step
    MAX_UNIT = max_unit  # Max units added of removed by one step

    MAX_POPULATION_SET = max_population_set  # Quantity of leaves nodes
    MAX_POPULATION_SELECT = max_population_selected  # Quantity of leaves nodes

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
            direction = Nutrition.directionDifference(stateNutrition, targetNutrition)
            # print("direction: ", direction)

            # Test increase and decrease each meal
            options = []  # Init the options of steps as an empty array

            for mealCode in mealCodeList:
                for signal in [-1, 1]:  # Try remove and add
                    for times in range(1, MAX_UNIT + 1):

                        factor = times * UNIT * signal
                        if state[mealCode] + factor >= 0.0:

                            # Calc similatiry between mealDirection and direction
                            # To calculate similarity, cosine similarity was employed. (-1,1).
                            # stepDirection = {
                            #     nutritionCode: nutritionQuantity*factor for nutritionCode, nutritionQuantity in dictNutritionByMeal[mealCode].items()}

                            # similarity = cosine_similarity(list(stepDirection.values()), direction.values())

                            # Calc using absDistance
                            similarity = 0
                            similarity = Nutrition.absDifference(
                                dictNutritionByMeal[mealCode], direction, factor=factor
                            )

                            # Store tuple (similarity, mealCode, signal) into options.
                            options.append((similarity, mealCode, factor))

            # Rank each possible  between
            options.sort(reverse=False)

            # Select EXPANSION_SELECT options to expand between EXPANSION_SET better options
            options = options[: min(EXPANSION_SET, len(options))]
            random.shuffle(options)
            options = options[: min(EXPANSION_SELECT, len(options))]

            # print("Options:", options)

            # Expand the state using the K best moviments
            population.clear()
            for option in options:
                newState = state.change(option[1], option[2])  # (mealCode, factor)
                population.append(newState)
                # print(f"newState ({option[1]}, {option[2]}):", newState)

            # Rank the population using module difference SUM ((Ni - Nt)/Nt)
            newPopulation = newPopulation + [
                (
                    Nutrition.absDifference(Nutrition(solution), targetNutrition),
                    solution,
                )
                for solution in population
            ]
            # print("newPopulation:", newPopulation)
        if verbose:
            print(
                "Mininum absDistance: ",
                min([distance for distance, solution in newPopulation]),
            )

        newPopulation.sort(reverse=False)
        newPopulation = newPopulation[: min(MAX_POPULATION_SET, len(newPopulation))]
        random.shuffle(newPopulation)
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

        for meal in initialState.data.keys():
            if initialState[meal] != population[0][meal]:
                print(
                    meal,
                    "- Init:",
                    initialState[meal],
                    " / Final:",
                    population[0][meal],
                )

    return SearchResult(initialState, population[0])
