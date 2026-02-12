import os
import pickle
import requests
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from dataclasses import dataclass, field
from tqdm import tqdm


url_listagem = "https://www.tbca.net.br/base-dados/composicao_alimentos.php?pagina={}"
pages = 58


# --- Definição da Estrutura de Dados ---

@dataclass
class TbcaUnit:
    codigo: str
    nome: str
    grupo: str
    link: str
    # O mapa de nutrientes será: {"Energia": 100.5, "Proteína": 20.0, ...}
    nutrientes: dict = field(default_factory=dict)

# --- Funções de Scraping ---

def mapear_alimentos_tbca() -> dict[str, TbcaUnit]:
    """
    Passo 1: Varre as páginas de listagem para criar o esqueleto dos dados.
    Retorna um dicionário: { 'C001': TbcaUnit(codigo='C001', ...), ... }
    """
    arquivo_mapa = "mapa_tbca_basico.pkl" # Salva o progresso parcial
    
    if os.path.exists(arquivo_mapa):
        print(f"Carregando mapa básico existente de '{arquivo_mapa}'...")
        with open(arquivo_mapa, "rb") as f:
            return pickle.load(f)

    base_url = "https://www.tbca.net.br/base-dados/"
    
    mapa_unidades = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print("Iniciando mapeamento de códigos e links...")
    
    for pag in range(1, pages + 1):
        print(f"Lendo página {pag}/{pages}...")
        try:
            resp = requests.get(url_listagem.format(pag), headers=headers)
            soup = BeautifulSoup(resp.content, "html.parser")
            
            tabela = soup.find("table")
            if not tabela: continue

            # Pula o cabeçalho (thead) e pega o corpo
            tbody = tabela.find("tbody")
            linhas = tbody.find_all("tr") if tbody else tabela.find_all("tr")

            for linha in linhas:
                colunas = linha.find_all("td")
                # Estrutura esperada da listagem: 
                # [0] Código, [1] Nome, [2] Nome Científico, [3] Grupo, ...
                if len(colunas) >= 4:
                    codigo = colunas[0].get_text(strip=True)
                    nome = colunas[1].get_text(strip=True)
                    grupo = colunas[3].get_text(strip=True)
                    
                    # O link geralmente está na coluna do Nome (pos 1) ou num botão
                    tag_link = linha.find("a", href=True)
                    link_relativo = tag_link['href'] if tag_link else ""
                    link_completo = base_url + link_relativo if link_relativo else ""

                    if codigo and link_completo:
                        unidade = TbcaUnit(
                            codigo=codigo,
                            nome=nome,
                            grupo=grupo,
                            link=link_completo
                        )
                        mapa_unidades[codigo] = unidade
            
            # Pequena pausa para não bloquear o IP
            sleep(0.2)

        except Exception as e:
            print(f"Erro na página {pag}: {e}")

    # Salva o mapa básico antes de começar a pegar os nutrientes
    with open(arquivo_mapa, "wb") as f:
        pickle.dump(mapa_unidades, f)
    
    print(f"Mapeamento concluído! {len(mapa_unidades)} alimentos encontrados.")
    return mapa_unidades

def extrair_nutrientes_do_link(url: str) -> dict:
    """
    Acessa a página de detalhes e extrai o mapa nutrient-quantidade (por 100g).
    """
    nutrientes = {}
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        
        # Se der erro 404 ou 500, retorna vazio
        if resp.status_code != 200:
            return {}

        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Procura a tabela de composição
        tabela = soup.find("table", id="tabela1")
        if not tabela:
            # Fallback: tenta achar a primeira tabela da página
            tabela = soup.find("table")
        
        if not tabela: return {}

        tbody = tabela.find("tbody")
        linhas = tbody.find_all("tr") if tbody else tabela.find_all("tr")

        for linha in linhas:
            cols = linha.find_all("td")
            # Estrutura esperada do detalhe:
            # [0] Componente, [1] Unidade, [2] Valor por 100g, ...
            if len(cols) >= 3:
                nome_nutriente = cols[0].get_text(strip=True)
                valor_str = cols[2].get_text(strip=True)
                
                # Limpeza do valor (trata "NA", "Tr", "*", etc)
                if valor_str and valor_str.lower() not in ["na", "tr", "*", "-", ""]:
                    try:
                        # Converte "1.234,56" para float (padrão PT-BR)
                        valor_limpo = valor_str.replace(".", "").replace(",", ".")
                        nutrientes[nome_nutriente] = float(valor_limpo)
                    except ValueError:
                        pass # Ignora valores que não são números
                        
    except Exception:
        pass # Em caso de erro de conexão, retorna o que conseguiu
        
    return nutrientes

def get_dados_tbca_completo() -> dict[str, TbcaUnit]:
    """
    Função principal que orquestra tudo.
    Retorna (e salva) o mapa completo com nutrientes preenchidos.
    """
    arquivo_final = "mapa_tbca_completo.pkl"
    
    # Se já existir o arquivo final, carrega e retorna
    if os.path.exists(arquivo_final):
        print(f"Carregando dados completos de '{arquivo_final}'...")
        with open(arquivo_final, "rb") as f:
            return pickle.load(f)

    # Passo 1: Obter o mapa básico (Códigos, Links, Grupos)
    mapa_unidades = mapear_alimentos_tbca()
    
    print("Iniciando extração de nutrientes (isso pode demorar)...")
    
    # Passo 2: Iterar e preencher nutrientes
    # Convertemos para lista para usar o tqdm
    chaves = list(mapa_unidades.keys())
    
    for i, codigo in enumerate(tqdm(chaves, desc="Extraindo Nutrientes")):
        unidade = mapa_unidades[codigo]
        
        # Só busca se ainda não tiver nutrientes (caso reinicie o script)
        if not unidade.nutrientes:
            unidade.nutrientes = extrair_nutrientes_do_link(unidade.link)
            
        sleep(0.1) # Respeito ao servidor

    # Salvamento final
    with open(arquivo_final, "wb") as f:
        pickle.dump(mapa_unidades, f)
        
    print("Coleta completa finalizada com sucesso!")
    return mapa_unidades


tbca = get_dados_tbca_completo()