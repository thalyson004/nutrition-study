from pandas import DataFrame
from app.components.extract_data.extract_data import (
    get_meals_codes,
    getDfConsumo,
    getDfDieta,
    getDfMorador,
    getDfPerson,
    getDfMealState,
    getDictNutritionByMeal,
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

## Dictionaries
dictNutritionByMeal: dict[str, dict] = getDictNutritionByMeal()  # Nutrition by meal


print("Finish!")
