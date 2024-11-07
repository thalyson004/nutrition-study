nutrients: dict = {
    "ENERGIA_KCAL": "Energy (kcal)",
    "CHOTOT": "Carbohydrates (g)",
    "PTN": "Protein (g)",
    "LIP": "Total fats (g)",
    "FIBRA": "Total fiber (g)",
    "COLEST": "Cholesterol (mg)",
    "CALCIO": "Calcium (mg)",
    "AGTRANS": "Trans-fat (g)",
    "AGSAT": "Saturated fat (g)",
    "AGPOLI": "PUFA (g)",
    "SODIO": "Sodium (mg)",
    "POTASSIO": "Potassium (mg)",
    "FERRO": "Iron (mg)",
    "MAGNESIO": "Magnesium (mg)",
    "TIAMINA": "Vitamin B1 (mg)",
    "RIBOFLAVINA": "Vitamin B2 (mg)",
    "PIRIDOXAMINA": "Vitamin B6 (mg)",
    "NIACINA": "Niacin/B3 (mg)",
    "COBALAMINA": "Vitamin B12 (mcg)",
    "VITC": "Vitamin C (mg)",
    "VITA_RAE": "Vitamin A (µg)",
    "COBRE": "Copper (mg)",
    "FOLATO": "Folate (µg)",
    "FOSFORO": "Phosphorus (mg)",
    "ZINCO": "Zinc (mg)",
    # TODO: Add fruit and vegetables into mealState
    # "FRUIT": "Fruit and vegetables (g)"
    # TODO: Add fish into mealState
    # "FISH": "Fish (g)",
    # TODO: Add free sugar into mealState
    # "SUGAR": "Freesugar (g)"
}

nutrients_signal: dict = {
    "ENERGIA_KCAL": ">",
    "CHOTOT": ">",
    "PTN": ">",
    "LIP": "<",
    "FIBRA": ">",
    "COLEST": "<",
    "CALCIO": ">",
    "AGTRANS": "<",
    "AGSAT": "<",
    "AGPOLI": "<",
    "SODIO": "<",
    "POTASSIO": ">",
    "FERRO": ">",
    "MAGNESIO": ">",
    "TIAMINA": ">",
    "RIBOFLAVINA": ">",
    "PIRIDOXAMINA": ">",
    "NIACINA": ">",
    "COBALAMINA": ">",
    "VITC": ">",
    "VITA_RAE": ">",
    "COBRE": ">",
    "FOLATO": ">",
    "FOSFORO": ">",
    "ZINCO": ">",
    # TODO: Add fruit and vegetables into mealState
    # "FRUIT": ">",
    # TODO: Add fish into mealState
    # "FISH": ">",
    # TODO: Add free sugar into mealState
    # "SUGAR": ">"
}
