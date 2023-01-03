def calc_bmi(height:float, weight:float) -> float:
    """
        Calculate the BMI (Body Mass Index)
        
        Args:
            height (int): height in cms
            weight (int): weight in kilograms
            
        Returns:
            bmi (float): The BMI factor
    """
    
    height /= 100
    return weight/(height*height)

# ESTIMATED ENERGY REQUIREMENT (EER) EQUATION
# https://globalrph.com/medcalcs/estimated-energy-requirement-eer-equation/
# https://www150.statcan.gc.ca/n1/pub/82-003-x/2008004/article/10703/t/5800493-eng.htm#:~:text=EER%20%3D%20113.5%20%2D%2061.9*age,and%201.42%20if%20very%20active.
def calc_eer(
    gender:str,
    age:float,
    height:float,
    weight:float,
    activity:str,
    
    ) -> float:
    '''
    
    Input:
        gender: male or female
        age: year
        height: cm
        weight: kilogram
        activity: 
            sedentary   (Daily PAL range: 1.0 - 1.39)
            low_active  (Daily PAL range: 1.4 - 1.59)
            active      (Daily PAL range: 1.6 - 1.89)
            very_active (Daily PAL range: 1.9 - 2.50)
    '''
    bmi = calc_bmi(weight=weight, height=height)
    eer = 0.0
    
    # TODO: Calculate correctly the PAL
    PAL = 1.5 # active_fact 
    
    
    height /= height
    if(gender == 'male'):
        if(age >= 9 and age <= 18):
            eer = 88.5 - 61.9*age + PAL * (26.7*weight + 903*height) +25
        elif(age > 18):
            eer = 662 - (9.53*age) + PAL * (15.91*weight + 539.6*height)
        else:
            return 0.0 # TODO: Resolve year error
    else:
        if(age >= 9 and age <= 18):
            eer = 135.3 - (30.8*age) + PAL * (10.0*weight + 934*height) + 25
        elif(age > 18):
            eer = 354 - (6.91*age) + PAL *(9.36*weight + 726*height)
        else:
            return 0.0 # TODO: Resolve year error
    
    # Pregnancy (14-50 years old)
    # 1st trimester EER = Non-pregnant EER + 0

    # 2nd trimester EER = Non-pregnant EER + 340

    # 3rd trimester EER = Non-pregnant EER + 452

    # Lactation
    # 0-6 months postpartum EER = Non-pregnant EER + 330
    # 7-12 months postpartum EER = Non-pregnant EER + 400

    # Overweight or obese children, 3-18 years old (maintenance)
    # Male TEE = -114 -50.9 x Age [y] + PA x (19.5 x Wt [kg] + 1161.4 x Ht [m])
    # Female TEE = 389 - 41.2 x Age [y] + PA x (15 x Wt [kg] + 701.6 x Ht [m])

    return eer