import sys

import io
import os
import pickle
import random

from tqdm import tqdm

from time import sleep

import pandas as pd
import requests

from bs4 import BeautifulSoup

import json

caminho_diretorio = os.path.dirname(os.path.abspath(__file__))


def listar_codigos_alimentos_tbca(pagina: str) -> list:
    """
    Extrai os códigos dos alimentos de uma página específica da TBCA.

    Args:
        url_pagina (str): A URL completa da página da TBCA contendo a tabela.
                          Ex: 'http://www.tbca.net.br/base-dados/composicao_alimentos.php?pagina=1'

    Returns:
        list: Uma lista de strings com todos os códigos dos alimentos encontrados.
              Retorna uma lista vazia se a tabela não for encontrada ou em caso de erro.
    """

    url = f"http://www.tbca.net.br/base-dados/composicao_alimentos.php?pagina={pagina}"

    try:
        # Adicionar um User-Agent para simular um navegador e evitar bloqueios simples.
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # O pandas lê todas as tabelas HTML da página e retorna uma lista de DataFrames.
        todas_as_tabelas = pd.read_html(requests.get(url, headers=headers).content)

        # Procura pela tabela correta, que é a que contém a coluna 'Código'.
        tabela_alimentos = None
        for tabela in todas_as_tabelas:
            if "Código" in tabela.columns:
                tabela_alimentos = tabela
                break  # Encontrou a tabela, pode sair do loop.

        # Se a tabela foi encontrada, extrai os códigos.
        if tabela_alimentos is not None:
            # Converte a coluna 'Código' para uma lista de strings.
            # Usamos .astype(str) para garantir que não haja problemas com formatação (ex: 1234.0)
            codigos = tabela_alimentos["Código"].astype(str).tolist()
            return codigos
        else:
            print(
                f"Aviso: Nenhuma tabela com a coluna 'Código' foi encontrada em {url}"
            )
            return []

    except Exception as e:
        print(f"Ocorreu um erro ao processar a URL '{url}': {e}")
        return []


def listar_dados_alimentos_tbca(numero_pagina: int) -> list[tuple]:
    """
    Extrai uma tupla (Código, Nome, Grupo) dos alimentos
    de uma página específica da TBCA.

    Args:
        numero_pagina (int): O número da página da TBCA a ser consultada.

    Returns:
        list[tuple]: Uma lista de tuplas, onde cada tupla contém
                     (Código, Nome, Grupo).
                     Retorna uma lista vazia em caso de erro.
    """
    url_pagina = f"http://www.tbca.net.br/base-dados/composicao_alimentos.php?pagina={numero_pagina}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        
        response = requests.get(url_pagina, headers=headers)
        todas_as_tabelas = pd.read_html(io.StringIO(response.text))

        tabela_alimentos = None

        colunas_necessarias = ["Código", "Nome", "Grupo"]

        for tabela in todas_as_tabelas:
            if all(coluna in tabela.columns for coluna in colunas_necessarias):
                tabela_alimentos = tabela
                break

        if tabela_alimentos is not None:
            df_selecionado = tabela_alimentos[colunas_necessarias]
            lista_de_tuplas = list(df_selecionado.itertuples(index=False, name=None))
            return lista_de_tuplas
        else:
            print(
                f"Aviso: Nenhuma tabela com as colunas {colunas_necessarias} foi encontrada na página {numero_pagina}"
            )
            return []

    except ValueError:
        print(
            f"Aviso: Nenhuma tabela foi encontrada pelo Pandas na página {numero_pagina}."
        )
        return []
    except Exception as e:
        print(f"Ocorreu um erro ao processar a página {numero_pagina}: {e}")
        return []


def get_codigos_tbca() -> list:
    nome_arquivo_pickle = "dados_completos_tbca.pkl"

    if os.path.exists(nome_arquivo_pickle):
        print(f"O arquivo '{nome_arquivo_pickle}' já existe.")
        print("O web scraping não será executado novamente.")

        with open(nome_arquivo_pickle, "rb") as f:
            dados_existentes = pickle.load(f)
        print(f"\nVerificação: {len(dados_existentes)} registros já estão salvos.")
        if dados_existentes:
            print("Exemplo do primeiro registro:", dados_existentes[0])

        return dados_existentes
    else:
        print(
            f"Arquivo '{nome_arquivo_pickle}' não encontrado. Iniciando a coleta de dados da TBCA..."
        )

        todos_os_dados = []
        # O site informa um total de 10 páginas na paginação, mas os dados vão além.
        # Vamos manter 58 por enquanto, que parece ser o total real de páginas com dados.
        total_paginas = 58

        for i in range(1, total_paginas + 1):
            print(f"Processando página {i}/{total_paginas}...")
            dados_da_pagina = listar_dados_alimentos_tbca(i)

            if dados_da_pagina:
                todos_os_dados.extend(dados_da_pagina)
            else:
                # Se uma página não retornar dados, podemos parar para não fazer requisições desnecessárias.
                print(f"Página {i} não retornou dados. Finalizando a busca.")
                break

            sleep(0.5)

        print("\nColeta finalizada.")
        print(f"Total de registros de alimentos encontrados: {len(todos_os_dados)}")

        if todos_os_dados:
            try:
                with open(nome_arquivo_pickle, "wb") as f:
                    pickle.dump(todos_os_dados, f)
                print(
                    f"Lista de dados salva com sucesso no arquivo '{nome_arquivo_pickle}'"
                )

                return todos_os_dados
            except Exception as e:
                print(f"Ocorreu um erro ao salvar o arquivo pickle: {e}")
                return []
        else:
            print("Nenhum dado foi coletado. O arquivo pickle não foi criado.")
            return []


def extrair_detalhes_alimento(alimento_info: tuple) -> dict:
    """
    Extrai os detalhes nutricionais de um alimento e já retorna o dicionário
    em formato "achatado", pronto para o DataFrame.

    Args:
        alimento_info (tuple): Uma tupla contendo (código, nome, grupo) do alimento.

    Returns:
        dict: Um dicionário "achatado" com o código, nome, grupo e cada
              componente nutricional como uma chave de nível superior.
              Retorna None em caso de erro.
    """
    codigo, nome, grupo = alimento_info
    url_detalhes = f"https://www.tbca.net.br/base-dados/int_composicao_alimentos_2_edit.php?cod_produto={codigo}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url_detalhes, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        tabela_nutrientes = soup.find("table", id="tabela1")

        if not tabela_nutrientes:
            print(f"Aviso: Tabela de nutrientes não encontrada para o código {codigo}")
            return None

        componentes = {}
        for linha in tabela_nutrientes.find("tbody").find_all("tr"):
            celulas = linha.find_all("td")
            if len(celulas) > 2:
                nome_componente = celulas[0].get_text(strip=True)
                valor_texto = celulas[2].get_text(strip=True)
                if valor_texto and valor_texto.lower() not in ["tr", "na", "-"]:
                    try:
                        valor_float = float(valor_texto.replace(",", "."))
                        componentes[nome_componente] = valor_float
                    except (ValueError, TypeError):
                        pass

        if not componentes:
            print(f"Aviso: Nenhum componente válido encontrado para o código {codigo}")
            return None

        # ***** LÓGICA DE TRANSFORMAÇÃO MOVIDA PARA DENTRO DA FUNÇÃO *****
        # 1. Cria o dicionário base
        dados_finais = {"codigo": codigo, "descricao": nome, "grupo": grupo}

        # 2. Atualiza o dicionário base com os componentes, achatando a estrutura
        dados_finais.update(componentes)

        # 3. Retorna o dicionário já formatado
        return dados_finais

    except Exception as e:
        print(f"Erro ao processar o código {codigo}: {e}")
        return None


def get_dados_tbca() -> pd.DataFrame:
    # Arquivo de entrada (gerado no script anterior)
    arquivo_lista_alimentos = "dados_completos_tbca.pkl"
    # Arquivo de saída (DataFrame com todos os detalhes)
    arquivo_dataframe_final = "dataframe_nutricional_tbca.pkl"

    # Verifica se o DataFrame final já existe
    if os.path.exists(arquivo_dataframe_final):
        print(f"O arquivo final '{arquivo_dataframe_final}' já existe.")
        print("Para gerar novamente, apague o arquivo manualmente.")

        # Exemplo de como carregar e visualizar o DataFrame
        df_final = pd.read_pickle(arquivo_dataframe_final)
        print("\nDataFrame carregado com sucesso!")
        print(f"Total de alimentos no DataFrame: {len(df_final)}")
        return df_final

    else:
        # Verifica se o arquivo de entrada existe
        if not os.path.exists(arquivo_lista_alimentos):
            print(
                f"Erro: Arquivo de entrada '{arquivo_lista_alimentos}' não encontrado."
            )
            print(
                "Por favor, execute o script anterior primeiro para gerar a lista de alimentos."
            )
            return pd.DataFrame()
        else:
            print(f"Carregando a lista de alimentos de '{arquivo_lista_alimentos}'...")
            with open(arquivo_lista_alimentos, "rb") as f:
                lista_alimentos = pickle.load(f)

            print(
                f"{len(lista_alimentos)} alimentos para processar. Iniciando coleta de detalhes..."
            )

            # Lista para armazenar todos os dicionários de alimentos detalhados
            dados_detalhados_lista = []

            # Itera sobre a lista de alimentos com uma barra de progresso (tqdm)
            for alimento in tqdm(lista_alimentos, desc="Coletando detalhes"):
                detalhes = extrair_detalhes_alimento(alimento)
                if detalhes:
                    dados_detalhados_lista.append(detalhes)
                sleep(0.2)  # Pausa para não sobrecarregar o servidor

            print("\nColeta de detalhes finalizada.")

            if dados_detalhados_lista:
                # Cria o DataFrame do pandas a partir da lista de dicionários
                df_final = pd.DataFrame(dados_detalhados_lista)

                print("DataFrame criado com sucesso!")
                print(f"Total de registros processados: {len(df_final)}")

                # Salvando o DataFrame como um arquivo pickle
                try:
                    df_final.to_pickle(arquivo_dataframe_final)
                    print(
                        f"DataFrame salvo com sucesso no arquivo '{arquivo_dataframe_final}'"
                    )
                    print("\nAmostra do DataFrame final:")
                    print(df_final.head())
                except Exception as e:
                    print(f"Ocorreu um erro ao salvar o DataFrame: {e}")

                return df_final
            else:
                print("Nenhum dado detalhado foi coletado. O DataFrame não foi criado.")
                return pd.DataFrame()


def carregar_mapa_codigo() -> dict:
    """
    Carrega um arquivo de texto e o converte em um dicionário Python.

    O arquivo deve ter uma entrada por linha, com a chave e o valor
    separados por espaços ou uma tabulação.

    Args:

    Returns:
        dict: Um dicionário contendo os dados do arquivo.
              Retorna um dicionário vazio se o arquivo não for encontrado ou ocorrer um erro.
    """
    caminho_arquivo = os.path.join(caminho_diretorio, "mapa_codigo.txt")

    mapa_alimentos = {}
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                if not linha.strip():
                    continue

                partes = linha.rsplit(None, 1)

                if len(partes) == 2:
                    chave = partes[0].strip()
                    valor = partes[1].strip()
                    mapa_alimentos[chave] = valor

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return {}
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return {}

    return mapa_alimentos


def carregar_alimentos_do_json(arquivo: str) -> list:
    """
    Carrega um arquivo JSON de planos alimentares e extrai uma lista
    de todos os nomes de alimentos únicos presentes.

    Args:

    Returns:
        list: Uma lista de strings com os nomes únicos de todos os alimentos.
              Retorna uma lista vazia se o arquivo não for encontrado ou ocorrer um erro.
    """

    caminho_arquivo = os.path.join(caminho_diretorio, arquivo)

    alimentos_unicos = set()

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_planos = json.load(f)

            # O arquivo é uma lista de planos
            for plano in dados_planos:
                # Cada plano é um dicionário de dias ('1', '2', ...)
                for dia in plano.values():
                    # Cada dia é um dicionário de refeições ('Café da Manhã', ...)
                    for refeicao in dia.values():
                        # Cada refeição é uma lista de itens
                        for item in refeicao:
                            if "alimento" in item:
                                alimentos_unicos.add(item["alimento"])

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return []
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não é um JSON válido.")
        return []
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        return []

    return sorted(list(alimentos_unicos))


def criar_dicionario_de_arquivo() -> dict:
    """
    Lê um arquivo de texto onde cada linha contém uma chave e um valor
    separados por espaços ou tabulação, e o converte em um dicionário.

    Args:
        caminho_arquivo (str): O caminho para o arquivo .txt.

    Returns:
        dict: Um dicionário com os nomes dos alimentos como chaves e os códigos como valores.
              Retorna um dicionário vazio se o arquivo não for encontrado ou ocorrer um erro.
    """

    caminho_arquivo = os.path.join(caminho_diretorio, "mapa_codigo.txt")
    mapa_dados = {}

    try:
        # Abre o arquivo com encoding 'utf-8' para ler acentos corretamente
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha_limpa = linha.strip()
                # Ignora linhas em branco
                if not linha_limpa:
                    continue

                # .rsplit(None, 1) divide a linha a partir da direita, apenas uma vez.
                # Isso é ideal para separar a última "palavra" (o código) do resto (o nome).
                partes = linha_limpa.rsplit(None, 1)

                # Garante que a linha foi dividida em exatamente duas partes
                if len(partes) == 2:
                    chave = partes[0].strip()
                    valor = partes[1].strip()
                    mapa_dados[chave] = valor

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return {}
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")
        return {}

    return mapa_dados


df_tbca = get_dados_tbca()
codigos_tbca = get_codigos_tbca()
alimentos_gemini = carregar_alimentos_do_json("gemini.json")
alimentos_gbt = carregar_alimentos_do_json("gbt.json")
alimentos_deepseek = carregar_alimentos_do_json("deepseek.json")
codigos = carregar_mapa_codigo()
mapa = criar_dicionario_de_arquivo()

gemini_diets = None
with open(os.path.join(caminho_diretorio, "gemini.json"), "r", encoding="utf-8") as f:
    gemini_diets = json.load(f)

gbt_diets = None
with open(os.path.join(caminho_diretorio, "gbt.json"), "r", encoding="utf-8") as f:
    gbt_diets = json.load(f)

deepseek_diets = None
with open(os.path.join(caminho_diretorio, "deepseek.json"), "r", encoding="utf-8") as f:
    deepseek_diets = json.load(f)
