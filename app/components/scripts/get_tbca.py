from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import os
import pickle
from app.components.extract_data.extract_data import (
    get_meals_codes_list,
    get_tbca_codes_list,
)
import time

datasetPath = os.path.dirname(os.path.abspath(__file__)) + "/../../../datasets/"
datasetPicklePath = (
    os.path.dirname(os.path.abspath(__file__)) + "/../../../datasets/pickle"
)

nutrient_name_to_key: dict = {
    "Energia": "ENERGIA_KCAL",
    "Carboidrato total": "CHOTOT",
    "Proteína": "PTN",
    "Lipídios": "LIP",
    "Fibra alimentar": "FIBRA",
    "Colesterol": "COLEST",
    "Cálcio": "CALCIO",
    "Ácidos graxos trans": "AGTRANS",
    "Ácidos graxos saturados": "AGSAT",
    "Ácidos graxos poliinsaturados": "AGPOLI",
    "Sódio": "SODIO",
    "Potássio": "POTASSIO",
    "Ferro": "FERRO",
    "Magnésio": "MAGNESIO",
    "Tiamina": "TIAMINA",
    "Riboflavina": "RIBOFLAVINA",
    "Vitamina B6": "PIRIDOXAMINA",
    "Niacina": "NIACINA",
    "Vitamina B12": "COBALAMINA",
    "Vitamina C": "VITC",
    "Vitamina A (RAE)": "VITA_RAE",
    "Cobre": "COBRE",
    "Equivalente de folato": "FOLATO",
    "Fósforo": "FOSFORO",
    "Zinco": "ZINCO",
    # 'Umidade':
    # 'Álcool':
    # 'Cinzas':
    # 'Ácidos graxos monoinsaturados':
    # 'Manganês':
    # 'Selênio':
    # 'Vitamina A (RE)':
    # 'Vitamina D':
    # 'Alfa-tocoferol (Vitamina E)':
    # 'Sal de adição':
    # 'Açúcar de adição':
}


@dataclass
class TBCA:

    def __init__(
        self,
        tbca: str = None,
        portuguese: str = None,
        english: str = None,
        nutrients: dict[str, float] = None,
    ):
        self.tbca = tbca
        self.portuguese = portuguese
        self.english = english
        self.nutrients = nutrients if isinstance(nutrients, dict) else {}

    def __str__(self):
        return f"""tbca code: {self.tbca}
portuguese: {self.portuguese}
english: {self.english}
nutrients: {self.nutrients}"""

    @staticmethod
    def getTBCA(tbca: str, verbose: bool = False) -> "TBCA":
        """Given a tbca code without BR, return a TBCA instance

        returns:
            TBCA:
            Tbca code
            english descripton
            portuguse description
            nutrients of 1 gram of the food as a dictionary
        """

        # Step 1: Send an HTTP request to the website
        url = "https://www.tbca.net.br/base-dados/int_composicao_alimentos.php?cod_produto="
        response = requests.get(url + "BR" + tbca)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            id: int = 1
            table = soup.find("table")
            if verbose:
                print(f'{id} Try get: {soup.find("h5").get_text(strip=True)}')
                id += 1
                print(
                    (
                        soup.find("h5")
                        .get_text(strip=True)
                        .split("Descrição:")[1]
                        .split("<< ")
                    )
                )

            # Step 1: Extract Headers from <thead>
            [portuguese, english] = (
                soup.find("h5").get_text(strip=True).split("Descrição:")[1].split("<< ")
            )

            # portuguese
            if portuguese.count(", Brasil,"):
                portuguese = portuguese.replace(", Brasil,", "")

            # english
            if english.count(", Brazil"):
                english = english.replace(", Brazil", "")

            if english.count(" >>"):
                english = english.replace(" >>", "")

            # Step 2: Extract Rows from <tbody>
            rows = []
            for tr in table.tbody.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                rows.append(
                    (
                        cells[0],
                        float(
                            str(
                                cells[2]
                                if cells[2] != "tr"
                                and cells[2] != "NA"
                                and cells[2] != "-"
                                else "0.0"
                            ).replace(",", ".")
                        ),
                    )
                )

            rows = rows[1:]

            tbca = TBCA(
                tbca=tbca,
                portuguese=portuguese,
                english=english,
                nutrients=dict(
                    [
                        (nutrient_name_to_key[key], quantity / 100.0)
                        for (key, quantity) in [
                            row
                            for row in rows
                            if nutrient_name_to_key.get(row[0]) != None
                        ]
                    ]
                ),
            )

            return tbca

        else:
            if verbose:
                print(
                    f"Failed to retrieve the page. Status code: {response.status_code}"
                )
            return TBCA()

    @staticmethod
    def getDictTBCA(verbose=False) -> dict[str, "TBCA"]:
        """Return a dictionary with:
        key: TBCA code
        Value: TBCA Object
        """

        fileName = "dictTBCA.pickle"
        try:
            with open(datasetPicklePath + f"/{fileName}", "rb") as file:
                return pickle.load(file)
        except:
            with open(datasetPicklePath + f"/{fileName}", "wb") as file:
                dictTBCA: dict[str, "TBCA"] = {}
                tbcaCodes = get_tbca_codes_list()

                for code in tbcaCodes:
                    time.sleep(0.01)
                    dictTBCA[code] = TBCA.getTBCA(code, verbose=verbose)

                pickle.dump(dictTBCA, file)

                return dictTBCA
