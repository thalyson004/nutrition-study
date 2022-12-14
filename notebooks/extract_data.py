import pandas as pd
import numpy as np
from dictionaries.nutrients import nutrients
from calculations.factors import calc_eer

datasetPath = "../datasets/"
domicilioPath = "domicilio.sas7bdat"
moradorPath = "morador.sas7bdat"
consumoPath = "consumo.sas7bdat"
dietaPath = "caract_dieta.sas7bdat"

## Read the dataframes
#dfDomicilio = pd.read_sas(datasetPath+domicilioPath)
dfMorador = pd.read_sas(datasetPath+moradorPath) # Gender, age
dfDieta = pd.read_sas(datasetPath+dietaPath) # Height, Weight

dfConsumo = pd.read_sas(datasetPath+consumoPath)
'''Dataframe with meals registries'''



## Gerar coluna que identifica uma pessoa
def criarPessoa(row):
    '''
        Create the person id
        COD_UPA + NUM_UC + NUM_DOM + COD_INFORMANTE
    '''
    return f'{row["COD_UPA"]}#{row["NUM_UC"]}#{row["NUM_DOM"]}#{row["COD_INFORMANTE"]}'


dfConsumo = dfConsumo[dfConsumo.QUADRO == 72] 

dfConsumo['PESSOA'] = dfConsumo.apply(lambda row: criarPessoa(row), axis=1)
dfMorador['PESSOA'] = dfMorador.apply(lambda row: criarPessoa(row), axis=1)
dfDieta['PESSOA'] = dfDieta.apply(lambda row: criarPessoa(row), axis=1)

# Remove unnecessary columns (at this time)
features = []
'''List of useable features to calculate the nutrition of each person'''
features.append('PESSOA')
features = features + list(nutrients.keys())
features.append("UF")
features.append("RENDA_TOTAL")

dfPerson = dfConsumo[features].groupby('PESSOA', as_index=False).agg({
    'ENERGIA_KCAL': np.sum, 
    'CHOTOT': np.sum, 
    'PTN' : np.sum, 
    'LIP' : np.sum, 
    'FIBRA' : np.sum, 
    'COLEST' : np.sum,
    'CALCIO' : np.sum, 
    'SODIO' : np.sum, 
    'POTASSIO': np.sum, 
    'FERRO': np.sum, 
    'MAGNESIO' : np.sum, 
    'TIAMINA' : np.sum,
    'RIBOFLAVINA' : np.sum, 
    'NIACINA' : np.sum, 
    'PIRIDOXAMINA' : np.sum, 
    'COBALAMINA' : np.sum, 
    'VITC': np.sum,
    'VITA_RAE' : np.sum, 
    'COBRE' : np.sum, 
    'FOLATO' : np.sum, 
    'FOSFORO' : np.sum, 
    'ZINCO' : np.sum, 
    'UF': np.mean, 
    'RENDA_TOTAL' : np.mean,
    # 'GENDER' : np.mean, 
    # 'AGE' : np.mean, 
    # 'WEIGHT': np.mean, 
    # 'HEIGHT' : np.mean,
})

# Salve gender
gender = dict()
person_list = list(zip(dfMorador.PESSOA, dfMorador.V0404))
for person in person_list:
    gender[person[0]] = "male" if person[1]==1 else "female"

def get_gender(person:str) -> str:
    return gender.get(person, 0)

# dfPerson["GENDER"] = dfPerson.apply(lambda row: get_gender(row["PESSOA"]), axis=1)  

# Salve ages
age = dict()
person_list = list(zip(dfMorador.PESSOA, dfMorador.V0403))
for person in person_list:
    age[person[0]] = person[1]

def get_age(person:str) -> int:
    return age.get(person, 0)

# dfPerson["AGE"] = dfPerson.apply(lambda row: get_age(row["PESSOA"]), axis=1)
    
# Salve weights
weight = dict()
person_list = list(zip(dfDieta.PESSOA, dfDieta.V72C01))
for person in person_list:
    weight[person[0]] = person[1]

def get_weight(person:str) -> int:
    return weight.get(person, 0)

# dfPerson["WEIGHT"] = dfPerson.apply(lambda row: get_weight(row["PESSOA"]), axis=1)

# Salve heights
height = dict()
person_list = list(zip(dfDieta.PESSOA, dfDieta.V72C02))
for person in person_list:
    height[person[0]] = person[1]

def get_height(person:str) -> int:
    return height.get(person, 0)

# dfPerson["HEIGHT"] = dfPerson.apply(lambda row: get_height(row["PESSOA"]), axis=1)

dfPerson["EER"] = dfPerson.apply(
    lambda row: calc_eer(
                        gender=get_gender(row["PESSOA"]), 
                        age=get_age(row["PESSOA"]),
                        height=get_height(row["PESSOA"]),
                        weight=get_weight(row["PESSOA"]),
                        activity="active",
                    )
                    , axis=1)

# dfConsumo.drop("ESTRATO_POF", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("TIPO_SITUACAO_REG", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("COD_UPA", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("NUM_DOM", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("NUM_UC", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("COD_INFORMANTE", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("QUADRO", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("SEQ", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("iddomic", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("id", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("DIA_ATIPICO", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("DIA_SEMANA", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("PESO", axis=1, inplace=True, errors="ignore")
# dfConsumo.drop("PESO_FINAL", axis=1, inplace=True, errors="ignore")


    


    