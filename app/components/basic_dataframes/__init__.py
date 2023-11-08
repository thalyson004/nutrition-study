from pandas import DataFrame
from app.components.extract_data.extract_data import (
    get_meals_codes,
    get_meals_codes_list,
    getDfConsumo,
    getDfDieta,
    getDfMorador,
    getDfPerson,
    getDfMealState,
    getDictNutritionByMeal,
    getDictMealState,
    getDictPersonEer,
)


print("Loading basic data")
## Read the dataframes

# dfDomicilio = pd.read_sas(datasetPath+domicilioPath)
dfMorador: DataFrame = getDfMorador()  # Gender, age
dfDieta: DataFrame = getDfDieta()  # Height, Weight
dfConsumo: DataFrame = getDfConsumo()  # All meals
dfPerson: DataFrame = getDfPerson()  # Nutrition
dfMealState: DataFrame = getDfMealState()  # Person and all meals in grams
dfMealCode: DataFrame = get_meals_codes()  # Meals codes


print("Loading basic dictionary")
## Dictionaries
dictNutritionByMeal: dict[str, dict] = getDictNutritionByMeal()  # Nutrition by meal
dictMealState: dict[
    str, dict[str, int]
] = getDictMealState()  # Person and all meals in grams
dictPersonEer: dict[str, float] = getDictPersonEer()


## Lists
mealCodeList: list = get_meals_codes_list()

print("Finish!")
