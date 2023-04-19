from .calculations.factors import calc_eer

def get_right_nutrition(eer: float) -> dict:
    '''Given the EER factor, retuns a dictionary with the right nutrition
    
        Args:
            eer (float): EER factor
            
        Returns:
            nutrition dictionary (dict): Dictionary with the right nutrition of each nutrient for a specific person with EER factor 
    
    '''
    # TODO: Define the right quantities
    # FROM Eliseu 2020
    # Negative means lower than
    nutrients_quantiy = {
        "ENERGIA_KCAL" : eer,
        "CHOTOT": eer * (55/100), # 55-75 eer
        "PTN" : eer * (10/100), # 10-15 eer
        "LIP": (-1) * eer * (30/100), # 15–30 eer
        "FIBRA": 0,
        "COLEST": (-1) * 300,
        "CALCIO" : 868,
        "SODIO": 0, 
        "POTASSIO": 3510,
        "FERRO" : 6.8,
        "MAGNESIO": 303,
        "TIAMINA": 0.9,
        "RIBOFLAVINA": 1,
        "NIACINA": 11.5,
        "PIRIDOXAMINA": 1.1,
        "COBALAMINA": 2,
        "VITC": 66.1,
        "VITA_RAE": 560,
        "COBRE": 0.7,
        "FOLATO": 322,
        "ZINCO": 8,
        "FOSFORO": 649,
    }
    
    return nutrients_quantiy

nutrients = {
    "ENERGIA_KCAL" : "Energy (kcal)",
    "CHOTOT": "Carbohydrates (g)",
    "PTN" : "Protein (g)",
    "LIP": "Total fats (g)",
    "FIBRA": "Total fiber (g)",
    "COLEST": "Cholesterol (mg)",
    "CALCIO" : "Calcium (mg)",
    "SODIO": "Sodium (mg)",
    "POTASSIO": "Potassium (mg)",
    "FERRO" : "Iron (mg)",
    "MAGNESIO":"Magnesium (mg)",
    "TIAMINA": "Vitamin B1 (mg)",
    "RIBOFLAVINA": "Vitamin B2 (mg)",
    "NIACINA": "Niacin/B3 (mg)",
    "PIRIDOXAMINA": "Vitamin B6 (mg)",
    "COBALAMINA": "Vitamin B12",
    "VITC": "Vitamin C (mg)",
    "VITA_RAE": "Vitamin A (µg)",
    "COBRE": "Copper (mg)",
    "FOLATO": "Folate (µg)",
    "FOSFORO": "Phosphorus (mg)",
    "ZINCO": "Zinc (mg)",
    # PUFA (%EER) 6–10 6–10
    # Sat. fat (%EER) <10 <10
    # Trans-fat (%EER) <1 <1
    # Free sugarsa (%EER) <5 <5
    # Fruit and vegetables (g) ≥400 ≥400
    # Fish (g) ≥43b ≥43b
}