from app.components.extract_data.extract_data import (
    getDfConsumo,
    getDfDieta,
    getDfMorador,
    getDfPerson,
    getDfMealState,
)


print("Reading the datasets")
## Read the dataframes

# dfDomicilio = pd.read_sas(datasetPath+domicilioPath)
dfMorador = getDfMorador()  # Gender, age
dfDieta = getDfDieta()  # Height, Weight
dfConsumo = getDfConsumo()  # All meals
dfPerson = getDfPerson()  # Nutrition
dfMealState = getDfMealState()  # Person and all meals in grams

print("Finish!")
