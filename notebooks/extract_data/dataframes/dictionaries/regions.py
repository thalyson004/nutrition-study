def UFtoName(uf:int) -> str:
    '''Given a UF code, the name of the state
    
        Args:
            uf (int): UF Code
            
        Returns:
            state (str): Name of the state
    '''
    return UF_code.get(uf, dict()).get('name', '')

def UFtoRegion(uf:int) -> str:
    '''Given a UF code, retuns the name of the region
    
        Args:
            uf (int): UF Code
            
        Returns:
            region name (dict): Name of the region
    '''
    return UF_code.get(uf, dict()).get('region', '')


def UFtoNameRegion(uf:int) -> dict:
    '''Given a UF code, retuns the dictionary of the region
    
        Args:
            uf (int): UF Code
            
        Returns:
            region dictonary (dict): Dictionary of the region
    '''
    return UF_code.get(uf, dict())


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