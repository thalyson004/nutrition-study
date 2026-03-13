import json
import os

def verificar_quantidade_dietas(caminho_arquivo):
    """
    Lê um arquivo JSON contendo uma lista de dietas e retorna a quantidade.
    """
    # Verifica se o arquivo realmente existe antes de tentar abrir
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return 0

    try:
        # Abre o arquivo com codificação UTF-8 para evitar problemas com acentuação
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            dietas = json.load(arquivo)
            
        # Verifica se a estrutura base é uma lista (array) como esperado: [ {...}, {...} ]
        if isinstance(dietas, list):
            quantidade = len(dietas)
            print(f"Sucesso! O arquivo '{caminho_arquivo}' contém {quantidade} dietas válidas.")
            return quantidade
        else:
            print("Aviso: O JSON foi carregado, mas a estrutura principal não é uma lista (array).")
            print(f"Tipo encontrado: {type(dietas)}")
            return 0

    except json.JSONDecodeError as e:
        print("Erro de Formatação: O arquivo não é um JSON válido.")
        print(f"Detalhes do erro: {e}")
        print("Dica: Verifique se há vírgulas separando cada dieta e se o arquivo começa com '[' e termina com ']'.")
        return 0


# nome_do_arquivo = "dietas-vegana.json" 
# nome_do_arquivo = "dietas-vegetariana.json" 
nome_do_arquivo = "dietas-regular.json" 

quantidade_total = verificar_quantidade_dietas(nome_do_arquivo)