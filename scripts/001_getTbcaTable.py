from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


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


# Step 1: Send an HTTP request to the website
url = "https://www.tbca.net.br/base-dados/int_composicao_alimentos.php?cod_produto="
code_tbca = "BRC0044G"
response = requests.get(url + code_tbca)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")

    # Step 1: Extract Headers from <thead>
    [portuguese, english] = (
        soup.find("h5")
        .get_text(strip=True)
        .split("Descrição:")[1]
        .split(", Brasil,  << ")
    )

    english = english.split(", Brazil")[0]

    # Step 2: Extract Rows from <tbody>
    rows = []
    for tr in table.tbody.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        rows.append(
            (
                cells[0],
                float(str(cells[2] if cells[2] != "tr" else "0.0").replace(",", ".")),
            )
        )

    rows = rows[1:]

    tbca = TBCA(
        tbca=code_tbca,
        portuguese=portuguese,
        english=english,
        nutrients=dict(
            [
                (nutrient_name_to_key[key], quantity / 100.0)
                for (key, quantity) in [
                    row for row in rows if nutrient_name_to_key.get(row[0]) != None
                ]
            ]
        ),
    )

    print(tbca)

else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
