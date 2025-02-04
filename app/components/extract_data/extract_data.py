import pickle
from pandas import DataFrame
import pandas as pd
import numpy as np
import os
import pyreadstat

from .dataframes.dictionaries.nutrients import nutrients
from .dataframes.dictionaries.calculations.factors import calc_eer

datasetPath = os.path.dirname(os.path.abspath(__file__)) + "/../../../datasets/"
datasetPicklePath = (
    os.path.dirname(os.path.abspath(__file__)) + "/../../../datasets/pickle"
)
domicilioPath = "domicilio.sas7bdat"
moradorPath = "morador.sas7bdat"
consumoPath = "consumo.sas7bdat"
# consumoPath = "CONSUMO_ALIMENTAR.txt"
dietaPath = "caract_dieta.sas7bdat"


def criarPessoa(row):
    """
    Create the person id given a row
    COD_UPA + NUM_DOM + NUM_UC  + COD_INFORMANTE
    """
    return f'{int(row["COD_UPA"])}#{int(row["NUM_DOM"])}#{int(row["NUM_UC"])}#{int(row["COD_INFORMANTE"])}'


# Dataframes


def getDfMorador() -> DataFrame:
    """Get dfMorador with columns:
    TODO:
    x:..
    y:..
    z:..
    """
    try:
        with open(datasetPicklePath + "/dfMorador.pickle", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        dfMorador = pd.read_sas(datasetPath + moradorPath)
        dfMorador["PESSOA"] = dfMorador.apply(lambda row: criarPessoa(row), axis=1)

        with open(datasetPicklePath + "/dfMorador.pickle", "wb") as file:
            pickle.dump(dfMorador, file)

        return dfMorador


def getDfDieta() -> DataFrame:
    """Get dfDieta with columns:
    TODO:
    x:..
    y:..
    z:..
    """

    try:
        with open(datasetPicklePath + "/dfDieta.pickle", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        dfDieta = pd.read_sas(datasetPath + dietaPath)
        dfDieta["PESSOA"] = dfDieta.apply(lambda row: criarPessoa(row), axis=1)

        with open(datasetPicklePath + "/dfDieta.pickle", "wb") as file:
            pickle.dump(dfDieta, file)

        return dfDieta


def getDfConsumo() -> DataFrame:
    """Dataframe with meals registries
    Get dfConsumo with columns:
    TODO:
    x:..
    y:..
    z:..
    """

    try:
        with open(datasetPicklePath + "/dfConsumo.pickle", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        dfConsumo, _ = pyreadstat.read_sas7bdat(datasetPath + consumoPath)
        # dfConsumo = pd.read_sas(datasetPath + consumoPath)
        dfConsumo = dfConsumo[dfConsumo.QUADRO == 72]
        dfConsumo["PESSOA"] = dfConsumo.apply(lambda row: criarPessoa(row), axis=1)

        def decode(s: object):
            return s.decode()

        # dfConsumo["COD_TBCA"] = dfConsumo["COD_TBCA"].apply(decode).astype(str)
        dfConsumo["V9001"] = dfConsumo["V9001"].apply(int).astype(int)

        # labels = [
        #     [
        #         2,
        #         4,
        #         1,
        #         9,
        #         2,
        #         1,
        #         2,
        #         2,
        #         2,
        #         4,
        #         2,
        #         7,
        #         3,
        #         2,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         1,
        #         2,
        #         2,
        #         7,
        #         9,
        #         6,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         14,
        #         15,
        #         10,
        #         15,
        #         1,
        #     ],
        #     [
        #         "UF",
        #         "ESTRATO_POF",
        #         "TIPO_SITUACAO_REG",
        #         "COD_UPA",
        #         "NUM_DOM",
        #         "NUM_UC",
        #         "COD_INFORMANTE",
        #         "QUADRO",
        #         "SEQ",
        #         "V9005",
        #         "V9007",
        #         "V9001",
        #         "V9015",
        #         "V9016",
        #         "V9017",
        #         "V9018",
        #         "V9019",
        #         "V9020",
        #         "V9021",
        #         "V9022",
        #         "V9023",
        #         "V9024",
        #         "V9025",
        #         "V9026",
        #         "V9027",
        #         "V9028",
        #         "V9029",
        #         "V9030",
        #         "COD_UNIDADE_MEDIDA_FINAL",
        #         "COD_PREPARACAO_FINAL",
        #         "GRAMATURA1",
        #         "QTD",
        #         "COD_TBCA",
        #         "ENERGIA_KCAL",
        #         "ENERGIA_KJ",
        #         "PTN",
        #         "CHOTOT",
        #         "FIBRA",
        #         "LIP",
        #         "COLEST",
        #         "AGSAT",
        #         "AGMONO",
        #         "AGPOLI",
        #         "AGTRANS",
        #         "CALCIO",
        #         "FERRO",
        #         "SODIO",
        #         "MAGNESIO",
        #         "FOSFORO",
        #         "POTASSIO",
        #         "COBRE",
        #         "ZINCO",
        #         "VITA_RAE",
        #         "TIAMINA",
        #         "RIBOFLAVINA",
        #         "NIACINA",
        #         "PIRIDOXAMINA",
        #         "COBALAMINA",
        #         "VITD",
        #         "VITE",
        #         "VITC",
        #         "FOLATO",
        #         "PESO",
        #         "PESO_FINAL",
        #         "RENDA_TOTAL",
        #         "DIA_SEMANA",
        #         "DIA_ATIPICO",
        #     ],
        # ]

        # converters = {
        #     "UF": lambda x: str(x),
        #     "ESTRATO_POF": lambda x: int(x),
        #     "TIPO_SITUACAO_REG": lambda x: str(x),
        #     "COD_UPA": lambda x: str(x),
        #     "NUM_DOM": lambda x: str(x),
        #     "NUM_UC": lambda x: str(x),
        #     "COD_INFORMANTE": lambda x: str(x),
        #     "QUADRO": lambda x: int(x),
        #     "SEQ": lambda x: int(x),
        #     "V9005": lambda x: str(x),
        #     "V9007": lambda x: str(x),
        #     "V9001": lambda x: int(x),
        #     "V9015": lambda x: str(x),
        #     "V9016": lambda x: str(x),
        #     "V9017": lambda x: str(x),
        #     "V9018": lambda x: str(x),
        #     "V9019": lambda x: str(x),
        #     "V9020": lambda x: str(x),
        #     "V9021": lambda x: str(x),
        #     "V9022": lambda x: str(x),
        #     "V9023": lambda x: str(x),
        #     "V9024": lambda x: str(x),
        #     "V9025": lambda x: str(x),
        #     "V9026": lambda x: str(x),
        #     "V9027": lambda x: str(x),
        #     "V9028": lambda x: str(x),
        #     "V9029": lambda x: str(x),
        #     "V9030": lambda x: str(x),
        #     "COD_UNIDADE_MEDIDA_FINAL": lambda x: str(x),
        #     "COD_PREPARACAO_FINAL": lambda x: int(x),
        #     "GRAMATURA1": lambda x: float(x),
        #     "QTD": lambda x: float(x),
        #     "COD_TBCA": lambda x: str(x),
        #     "ENERGIA_KCAL": lambda x: float(x),
        #     "ENERGIA_KJ": lambda x: float(x),
        #     "PTN": lambda x: float(x),
        #     "CHOTOT": lambda x: float(x),
        #     "FIBRA": lambda x: float(x),
        #     "LIP": lambda x: float(x),
        #     "COLEST": lambda x: float(x),
        #     "AGSAT": lambda x: float(x),
        #     "AGMONO": lambda x: float(x),
        #     "AGPOLI": lambda x: float(x),
        #     "AGTRANS": lambda x: float(x),
        #     "CALCIO": lambda x: float(x),
        #     "FERRO": lambda x: float(x),
        #     "SODIO": lambda x: float(x),
        #     "MAGNESIO": lambda x: float(x),
        #     "FOSFORO": lambda x: float(x),
        #     "POTASSIO": lambda x: float(x),
        #     "COBRE": lambda x: float(x),
        #     "ZINCO": lambda x: float(x),
        #     "VITA_RAE": lambda x: float(x),
        #     "TIAMINA": lambda x: float(x),
        #     "RIBOFLAVINA": lambda x: float(x),
        #     "NIACINA": lambda x: float(x),
        #     "PIRIDOXAMINA": lambda x: float(x),
        #     "COBALAMINA": lambda x: float(x),
        #     "VITD": lambda x: float(x),
        #     "VITE": lambda x: float(x),
        #     "VITC": lambda x: float(x),
        #     "FOLATO": lambda x: float(x),
        #     "PESO": lambda x: float(x),
        #     "PESO_FINAL": lambda x: float(x),
        #     "RENDA_TOTAL": lambda x: float(x),
        #     "DIA_SEMANA": lambda x: str(x),
        #     "DIA_ATIPICO": lambda x: str(x),
        # }

        # dfConsumo = pd.read_fwf(
        #     datasetPath + consumoPath,
        #     widths=labels[0],
        #     index=False,
        #     header=None,
        #     dtype=str,
        #     encoding="ascii",
        # )
        # dfConsumo.columns = labels[1]

        # dfConsumo = dfConsumo.fillna(0)

        # for col in dfConsumo.columns:
        #     dfConsumo[col] = dfConsumo[col].apply(converters[col])

        dfConsumo = dfConsumo[dfConsumo.QUADRO == 72]
        dfConsumo["PESSOA"] = dfConsumo.apply(lambda row: criarPessoa(row), axis=1)

        with open(datasetPicklePath + "/dfConsumo.pickle", "wb") as file:
            pickle.dump(dfConsumo, file)

        return dfConsumo


def getDfPerson() -> DataFrame:
    """Dataframe with nutrition of each person
    Get dfPerson with columns:
    TODO:
    x:..
    y:..
    z:..
    """

    try:
        with open(datasetPicklePath + "/dfPerson.pickle", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        """List of useable features to calculate the nutrition of each person"""
        features = []
        features.append("PESSOA")
        features = features + list(nutrients)
        features.append("UF")
        features.append("RENDA_TOTAL")
        features.append("ESTRATO_POF")

        dfPerson = (
            getDfConsumo()[features]
            .groupby("PESSOA", as_index=False)
            .agg(
                {
                    "ENERGIA_KCAL": np.sum,
                    "CHOTOT": np.sum,
                    "PTN": np.sum,
                    "LIP": np.sum,
                    "FIBRA": np.sum,
                    "COLEST": np.sum,
                    "CALCIO": np.sum,
                    "SODIO": np.sum,
                    "POTASSIO": np.sum,
                    "FERRO": np.sum,
                    "MAGNESIO": np.sum,
                    "TIAMINA": np.sum,
                    "RIBOFLAVINA": np.sum,
                    "NIACINA": np.sum,
                    "PIRIDOXAMINA": np.sum,
                    "COBALAMINA": np.sum,
                    "VITC": np.sum,
                    "VITA_RAE": np.sum,
                    "COBRE": np.sum,
                    "FOLATO": np.sum,
                    "FOSFORO": np.sum,
                    "ZINCO": np.sum,
                    "UF": np.mean,
                    "RENDA_TOTAL": np.mean,
                    "ESTRATO_POF": np.mean,
                    # 'GENDER' : np.mean,
                    # 'AGE' : np.mean,
                    # 'WEIGHT': np.mean,
                    # 'HEIGHT' : np.mean,
                }
            )
        )

        dfPerson["EER"] = dfPerson.apply(
            lambda row: calc_eer(
                gender=get_gender(row["PESSOA"]),
                age=get_age(row["PESSOA"]),
                height=get_height(row["PESSOA"]),
                weight=get_weight(row["PESSOA"]),
                activity="active",
            ),
            axis=1,
        )

        dfPerson["AGE"] = dfPerson.apply(lambda row: get_age(row["PESSOA"]), axis=1)

        dfPerson["HEIGHT"] = dfPerson.apply(
            lambda row: get_height(row["PESSOA"]), axis=1
        )

        dfPerson["WEIGHT"] = dfPerson.apply(
            lambda row: get_weight(row["PESSOA"]), axis=1
        )

        dfPerson["GENDER"] = dfPerson.apply(
            lambda row: get_gender(row["PESSOA"]), axis=1
        )

        with open(datasetPicklePath + "/dfPerson.pickle", "wb") as file:
            pickle.dump(dfPerson, file)

        return dfPerson


def getDfPersonAdults() -> DataFrame:
    dfPerson = getDfPerson()

    return dfPerson[(dfPerson["AGE"] >= 25) & (dfPerson["AGE"] <= 60)]


def getDfPersonAdultsFemale() -> DataFrame:
    dfPerson = getDfPersonAdults()
    return dfPerson[dfPerson["GENDER"] == "female"]


def getDfPersonAdultsMale() -> DataFrame:
    dfPerson = getDfPersonAdults()
    return dfPerson[dfPerson["GENDER"] == "male"]


def getDfMealState(verbose=False) -> DataFrame:
    """Return dataframe with initial state of each person

    Returns:
         df (DataFrame): A dataframe initial state of each person
    """

    try:
        if verbose:
            print("Try open /dfMealState.pickle")

        with open(datasetPicklePath + "/dfMealState.pickle", "rb") as file:
            return pickle.load(file)

        if verbose:
            print("/dfMealState.pickle opened")

    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        if verbose:
            print("Error on open /dfMealState.pickle")
            print("Try create a new one")
            print("Reading the database Consumo")

        df = getDfConsumo()

        if verbose:
            print("Database Consumo readed ")

        dfMealState = DataFrame(df["PESSOA"].unique(), columns=["PESSOA"])

        if verbose:
            print("dfMealState initialized:", dfMealState)

        countQuantity = {}

        mealsCodes = get_meals_codes_list()

        if verbose:
            print("mealsCodes readed:", mealsCodes)

        for index, row in df.iterrows():
            v9001 = row["V9001"]
            try:
                countQuantity[(row["PESSOA"], v9001)] += 0
            except:
                countQuantity[(row["PESSOA"], v9001)] = 0

            countQuantity[(row["PESSOA"], v9001)] += row["QTD"]

        if verbose:
            print("countQuantity:", countQuantity)

        def get_QTD(pessoa: str, v9001: str) -> int:
            value = 0.0

            try:
                value = countQuantity[(pessoa, v9001)]
            except:
                value = 0

            return value

        newcolumns = dfMealState["PESSOA"].apply(
            lambda pessoa: get_QTD(pessoa, code) for code in mealsCodes
        )

        newcolumns.columns = mealsCodes

        if verbose:
            print("newcolumns", newcolumns)

        dfMealState = pd.concat([dfMealState, newcolumns], axis=1)
        # for code in mealsCodes:
        #     print("code", code)
        #     dfMealState[code] = dfMealState["PESSOA"].apply(
        #         lambda pessoa: get_QTD(pessoa, code)
        #     )
        #     dfMealState.head()
        #     break

        with open(datasetPicklePath + "/dfMealState.pickle", "wb") as file:
            pickle.dump(dfMealState, file)

        return dfMealState


def get_meals_codes() -> DataFrame:
    """Extract dataframe with all meals code

    Args:

    Returns:
        df (DataFrame): A dataframe with all uniques V9001 codes
    """

    return DataFrame(getDfConsumo()["V9001"].unique(), columns=["V9001"])


# List


def get_meals_codes_list() -> list:
    """Extract a list of unique V9001

    Args:

    Returns:
        l (list): A array list with all uniques V9001 codes
    """

    return [
        code
        for code in DataFrame(getDfConsumo()["V9001"].unique(), columns=["V9001"])[
            "V9001"
        ].to_list()
    ]


def get_tbca_codes_list() -> list:
    """Extract a list of unique V9001

    Args:

    Returns:
        l (list): A array list with all uniques V9001 codes
    """

    return [
        code
        for code in DataFrame(
            getDfConsumo()["COD_TBCA"].unique(), columns=["COD_TBCA"]
        )["COD_TBCA"].to_list()
    ]


# Dictonary
def getDictNutritionByMeal() -> dict[str:dict]:
    """Dictionary with nutrition of one gram of each meal

    TODO:
    x:..
    y:..
    z:..
    """

    fileName = "dictNutritionByMeal"

    try:
        with open(datasetPicklePath + f"/{fileName}.pickle", "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        dictNutritionByMeal: dict[str, dict] = {}  # CODEA : {ZINCO:4, PTN:4... etc}
        mealsCodesList = get_meals_codes_list()

        for code in mealsCodesList:
            dictNutritionByMeal[code] = dict()

        dfConsumo = getDfConsumo()
        for index, row in dfConsumo.iterrows():
            mealCode = row["V9001"]
            if dictNutritionByMeal[mealCode] != dict():
                continue

            for nutrient in list(nutrients):
                dictNutritionByMeal[mealCode][nutrient] = float(row[nutrient]) / float(
                    row["QTD"]
                )

        with open(datasetPicklePath + f"/{fileName}.pickle", "wb") as file:
            pickle.dump(dictNutritionByMeal, file)

        return dictNutritionByMeal


def getDictMealState() -> dict[str : dict[str, int]]:
    """Dictionary with person ID as key and a dict with key/value equal to (foodID, grams)

    Example:
    TODO:
    ....
    """

    fileName = "dictMealState"

    try:
        with open(datasetPicklePath + f"/{fileName}.pickle", "rb") as file:
            return pickle.load(file)

    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        dictMealState: dict[str, dict] = {}  # (PERSONID, dict[FOODID, GRAMS])
        dfMealState = getDfMealState()

        for index, row in dfMealState.iterrows():
            pessoaID = row["PESSOA"]
            dictMealState[pessoaID] = dict()

            for mealCode, grams in row.items():
                # if mealCode == "PESSOA" or grams == 0.0:
                if mealCode == "PESSOA":
                    continue

                if isinstance(mealCode, bytes):
                    mealCode = mealCode.decode(
                        "utf-8"
                    )  # Assuming 'b' is a bytes object

                dictMealState[pessoaID][mealCode] = grams

        with open(datasetPicklePath + f"/{fileName}.pickle", "wb") as file:
            pickle.dump(dictMealState, file)

        return dictMealState


def getDictV9001ToTbca() -> dict[str, str]:
    """Return a dictionary with (V9001, COD_TBCA)
    First try read a pickle file, if doesnt exist, create, write and return

    Returns:
        dict[str, str]: (V9001, COD_TBCA)
    """
    fileName = "dictV9001ToTbca"

    try:
        with open(datasetPicklePath + f"/{fileName}.pickle", "rb") as file:
            return pickle.load(file)

    except:
        dfConsumo = getDfConsumo()

        lV9001 = [str(int(el)) for el in list(dfConsumo["V9001"])]

        lTbca = [el for el in list(dfConsumo["COD_TBCA"])]

        dictV9001ToTbca: dict[str, str] = {}  # (V9001, COD_TBCA) []

        for v9001, tbca in list(zip(lV9001, lTbca)):
            dictV9001ToTbca[v9001] = tbca

        with open(datasetPicklePath + f"/{fileName}.pickle", "wb") as file:
            pickle.dump(dictV9001ToTbca, file)

        return dictV9001ToTbca


def getDictTbcaToV9001() -> dict[str, str]:
    """Return a dictionary with (COD_TBCA, V9001)
    First try read a pickle file, if doesnt exist, create, write and return

    Returns:
        dict[str, str]: (COD_TBCA, V9001)
    """
    fileName = "dictTbcaToV9001"

    try:
        with open(datasetPicklePath + f"/{fileName}.pickle", "rb") as file:
            return pickle.load(file)

    except:
        dfConsumo = getDfConsumo()

        lV9001 = [str(int(el)) for el in list(dfConsumo["V9001"])]

        lTbca = [el for el in list(dfConsumo["COD_TBCA"])]

        dictTbcaToV9001: dict[str, str] = {}  # (COD_TBCA, V9001) []

        for v9001, tbca in list(zip(lV9001, lTbca)):
            dictTbcaToV9001[tbca] = v9001

        with open(datasetPicklePath + f"/{fileName}.pickle", "wb") as file:
            pickle.dump(dictTbcaToV9001, file)

        return dictTbcaToV9001


def getDictPersonEer() -> dict[str:dict]:
    """Dictionary with eer by person id

    TODO:
    x:..
    y:..
    z:..
    """

    fileName = "dictPersonEer"

    try:
        with open(datasetPicklePath + f"/{fileName}.pickle", "rb") as file:
            return pickle.load(file)

    except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
        dictPersonEer: dict[str, float] = {}  # CODEA : {ZINCO:4, PTN:4... etc}

        dfPerson = getDfPerson()
        for index, row in dfPerson.iterrows():
            dictPersonEer[row["PESSOA"]] = row["EER"]

        with open(datasetPicklePath + f"/{fileName}.pickle", "wb") as file:
            pickle.dump(dictPersonEer, file)

        return dictPersonEer


def getDictPersonIdStrata() -> dict[int, int]:
    """Returns a dictionary with stratas, using personID as keys."""

    fileName = "dictStrataByPersonId.pickle"
    dictStrataByPersonId = {}
    try:
        with open(datasetPicklePath + f"/{fileName}", "rb") as file:
            dictStrataByPersonId = pickle.load(file)

    except:
        with open(datasetPicklePath + f"/{fileName}", "wb") as file:
            dfConsumo = getDfConsumo()

            dictStrataByPersonId = (
                dfConsumo.groupby("PESSOA")["ESTRATO_POF"].first().to_dict()
            )

            pickle.dump(dictStrataByPersonId, file)

    return dictStrataByPersonId


def getDictStrataMeals() -> dict[int, list[str]]:
    """Returns a dictionary with TBCA meal codes, using strata as keys."""
    fileName = "dictStrataMeals.pickle"

    try:
        with open(datasetPicklePath + f"/{fileName}", "rb") as file:
            dictStrataMeals = pickle.load(file)

    except:
        with open(datasetPicklePath + f"/{fileName}", "wb") as file:
            dfConsumo = getDfConsumo()

            dictStrataMeals: dict[int, list[str]] = {
                strata: [] for strata in list(dfConsumo["ESTRATO_POF"].astype(int))
            }

            for strata in dictStrataMeals.keys():
                dictStrataMeals[strata] = list(
                    set(
                        dfConsumo[dfConsumo["ESTRATO_POF"] == strata]["V9001"].to_list()
                    )
                )

            pickle.dump(dictStrataMeals, file)

    return dictStrataMeals


def getDictV9001ToGroupPtNames() -> dict[str, str]:
    """_summary_

    Returns:
        A dictionary with portuguese translate to portuguese group name
    """
    return {
        "Carnes e derivados": "Carnes e derivados",
        "Sementes e Oleaginosas": "Sementes e Oleaginosas",
        "Leguminosas e derivados": "Leguminosas e derivados",
        "Vegetais e derivados": "Vegetais e derivados",
        "Bebidas": "Bebidas",
        "Leite e derivados": "Leite e derivados",
        "Alimentos para fins especiais": "Alimentos para fins especiais",
        "Cereais e derivados": "Cereais e derivados",
        "Produtos açucarados": "Produtos açucarados",
        "Produtos açúcarados": "Produtos açúcarados",
        "Miscelânea": "Miscelânea",
        "Peixes e Frutos do mar": "Peixes e Frutos do mar",
        "Peixes e frutos do mar": "Peixes e Frutos do mar",
        "Ovos e derivados": "Ovos e derivados",
        "Frutas e derivados": "Frutas e derivados",
        "Gorduras e azeites": "Gorduras e azeites",
    }


def getDictV9001ToGroupEnNames() -> dict[str, str]:
    """_summary_

    Returns:
        A dictionary with english translate to portuguese group name
    """
    return {
        "Carnes e derivados": "Meat products",
        "Sementes e Oleaginosas": "Seeds and nuts",
        "Leguminosas e derivados": "Legume products",
        "Vegetais e derivados": "Vegetable products",
        "Bebidas": "Beverages",
        "Leite e derivados": "Milk and dairy products",
        "Alimentos para fins especiais": "Foods for special purposes",
        "Cereais e derivados": "Cereal products",
        "Produtos açucarados": "Sugary products",
        "Produtos açúcarados": "Sugary products",  # duplicado no dataset
        "Miscelânea": "Miscellaneous",
        "Peixes e Frutos do mar": "Fish and seafood",
        "Peixes e frutos do mar": "Fish and seafood",  # duplicado no dataset
        "Ovos e derivados": "Eggs and egg products",
        "Frutas e derivados": "Fruits and fruit products",
        "Gorduras e azeites": "Fats and oils",
    }


def getDictV9001toGroupPt() -> dict[str, str]:
    """Returns a portuguese dictionary with groups of each V9001 code"""
    fileName = "dictV9001toGroupPT.pickle"
    dictV9001toGroupPt = None

    try:
        with open(datasetPicklePath + f"/{fileName}", "rb") as file:
            dictV9001toGroupPt = pickle.load(file)

    except:
        with open(datasetPicklePath + f"/{fileName}", "wb") as file:
            dfGroup = None
            with open(datasetPath + "grupos.xlsx", "rb") as file:
                group = file.read()
                dfGroup = pd.read_excel(group)

            ptGroups = getDictV9001ToGroupPtNames()
            for id, row in dfGroup.iterrows():
                dictV9001toGroupPt[row["cod_pof_18"]] = ptGroups[row["grupo_tbca"]]

            pickle.dump(dictV9001toGroupPt, file)

    return dictV9001toGroupPt


def getDictV9001toGroupEn() -> dict[str, str]:
    """Returns a english dictionary with groups of each V9001 code"""
    fileName = "dictV9001toGroupEN.pickle"
    dictV9001toGroupEn = None

    try:
        with open(datasetPicklePath + f"/{fileName}", "rb") as file:
            dictV9001toGroupEn = pickle.load(file)

    except:
        with open(datasetPicklePath + f"/{fileName}", "wb") as file:
            dfGroup = None
            with open(datasetPath + "grupos.xlsx", "rb") as file:
                group = file.read()
                dfGroup = pd.read_excel(group)

            enGroups = getDictV9001ToGroupEnNames()
            for id, row in dfGroup.iterrows():
                dictV9001toGroupEn[row["cod_pof_18"]] = enGroups[row["grupo_tbca"]]

            pickle.dump(dictV9001toGroupEn, file)

    return dictV9001toGroupEn


# Remove unnecessary columns (at this time)


# TODO: improve it
dfMorador = getDfMorador()
dfDieta = getDfDieta()

"""gender dictionary of each person"""
gender = dict()
person_list = list(zip(dfMorador.PESSOA, dfMorador.V0404))
for person in person_list:
    gender[person[0]] = "male" if person[1] == 1 else "female"


def get_gender(person: str) -> str:
    """Given a person str, return the gender"""
    return gender.get(person, 0)


# dfPerson["GENDER"] = dfPerson.apply(lambda row: get_gender(row["PESSOA"]), axis=1)

"""age dictionary of each person"""
age = dict()
person_list = list(zip(dfMorador.PESSOA, dfMorador.V0403))
for person in person_list:
    age[person[0]] = person[1]


def get_age(person: str) -> int:
    """Given a person str, return the age"""
    return age.get(person, 0)


# dfPerson["AGE"] = dfPerson.apply(lambda row: get_age(row["PESSOA"]), axis=1)

"""weight dictionary of each person"""
weight = dict()
person_list = list(zip(dfDieta.PESSOA, dfDieta.V72C01))
for person in person_list:
    weight[person[0]] = person[1]


def get_weight(person: str) -> int:
    return weight.get(person, 0)


# dfPerson["WEIGHT"] = dfPerson.apply(lambda row: get_weight(row["PESSOA"]), axis=1)

"""heights dictionary of each person"""
height = dict()
person_list = list(zip(dfDieta.PESSOA, dfDieta.V72C02))
for person in person_list:
    height[person[0]] = person[1]


def get_height(person: str) -> int:
    """Given a person str, return the height"""
    return height.get(person, 0)


# dfPerson["HEIGHT"] = dfPerson.apply(lambda row: get_height(row["PESSOA"]), axis=1)


# print("Removing unnecessary columns")
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
