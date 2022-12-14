def UFtoNameRegion(uf:int) -> dict:
    return UF_code.get(uf, dict())

def UFtoName(uf:int) -> str:
    return UF_code.get(uf, dict()).get('name', '')

def UFtoRegion(uf:int) -> str:
    return UF_code.get(uf, dict()).get('region', '')

UF_code = {
    # Norte
    11: {
        "name": "Rondônia",
        "region": "Norte",
    },
    12: {
        "name": "Acre",
        "region": "Norte",
    },
    13: {
        "name": "Amazonas",
        "region": "Norte",
    },
    14: {
        "name": "Roraima",
        "region": "Norte",
    },
    15: {
        "name": "Pará",
        "region": "Norte",
    },
    16: {
        "name": "Amapá",
        "region": "Norte",
    },
    17: {
        "name": "Tocantins",
        "region": "Norte",
    },
    # Nordeste
    21: {
        "name": "Maranhão",
        "region": "Nordeste",
    },
    22: {
        "name": "Piauí",
        "region": "Nordeste",
    },
    23: {
        "name": "Ceará",
        "region": "Nordeste",
    },
    24: {
        "name": "Rio Grande do Norte",
        "region": "Nordeste",
    },
    25: {
        "name": "Paraíba",
        "region": "Nordeste",
    },
    26: {
        "name": "Pernambuco",
        "region": "Nordeste",
    },
    27: {
        "name": "Alagoas",
        "region": "Nordeste",
    },
    28: {
        "name": "Sergipe",
        "region": "Nordeste",
    },
    29: {
        "name": "Bahia",
        "region": "Nordeste",
    },
    # Sudeste
    31: {
        "name": "Minas Gerais",
        "region": "Sudeste",
    },
    32: {
        "name": "Espírito Santo",
        "region": "Sudeste",
    },
    33: {
        "name": "Rio de Janeiro",
        "region": "Sudeste",
    },
    35: {
        "name": "São Paulo",
        "region": "Sudeste",
    },
    # Sul
    41: {
        "name": "Paraná",
        "region": "Sul",
    },
    42: {
        "name": "Santa Catarina",
        "region": "Sul",
    },
    43: {
        "name": "Rio Grande do Sul",
        "region": "Sul",
    },
    # Centro-Oeste
    50: {
        "name": "Mato Grosso do Sul",
        "region": "Centro-Oeste",
    },
    51: {
        "name": "Mato Grosso",
        "region": "Centro-Oeste",
    },
    52: {
        "name": "Goiás",
        "region": "Centro-Oeste",
    },
    53: {
        "name": "Distrito Federal",
        "region": "Centro-Oeste",
    },
}