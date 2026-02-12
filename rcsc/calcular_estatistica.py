import json
import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
import os
import pickle
import re
import argparse

@dataclass
class TbcaUnit:
    codigo: str
    nome: str
    grupo: str
    link: str
    
    nutrientes: dict = field(default_factory=dict)

from get_data import *

# --- 1. Nova Lógica de Parsing (De trás para frente) ---
def carregar_mapa_codigos_limpo(caminho_arquivo: str) -> dict:
    """
    Lê o arquivo mapa_codigo.txt varrendo de trás para frente.
    Enquanto o 'token' for um código (inicia com BR ou é -), ele é removido.
    O que sobrar é o nome do alimento.
    """
    
    if os.path.exists("mapa_codigo.pkl"):
        with open("mapa_codigo.pkl", "rb") as f:
            return pickle.load(f)
    
    mapa = {}
    
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo {caminho_arquivo} não encontrado.")
        return mapa

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: 
                    continue
    
                
                # 2. Divide a linha em palavras (tokens)
                partes = linha.split()
                
                codigos_encontrados = []
                
                while partes:
                    ultimo_token = partes[-1]
                    
            
                    eh_codigo = (ultimo_token.startswith("BR") or 
                                 ultimo_token == "-" or 
                                 ("," in ultimo_token and "BR" in ultimo_token))
                    
                    if eh_codigo:
                        token = partes.pop()
                        if token != "-":
                            sub_cods = [c.strip() for c in token.split(',')]
                            for c in sub_cods:
                                if c and c.startswith("BR"):
                                    codigos_encontrados.append(c)
                    else:
                        break
                
                
                if partes:
                    nome_alimento = " ".join(partes)
                    mapa[nome_alimento] = codigos_encontrados
                        
    except Exception as e:
        print(f"Erro ao processar o arquivo mapa_codigo: {e}")

    with open("mapa_codigo.pkl", "wb") as f:
        pickle.dump(mapa, f)
    
    return mapa

# --- 2. Função Auxiliar de Cálculo (Mantida) ---
def calcular_nutrientes_item(nome_alimento: str, quantidade_g: float, 
                             mapa_codigos: dict, dados_tbca: dict) -> dict:
    codigos = mapa_codigos.get(nome_alimento)
    if not codigos: return {}

    nutrientes_acumulados = defaultdict(float)
    codigos_validos_encontrados = 0

    for code in codigos:
        unidade = dados_tbca.get(code)
        if unidade and unidade.nutrientes:
            codigos_validos_encontrados += 1
            for nutriente, valor_por_100g in unidade.nutrientes.items():
                qtd_real = (valor_por_100g * quantidade_g) / 100.0
                nutrientes_acumulados[nutriente] += qtd_real
    
    if codigos_validos_encontrados == 0: return {}

    return {k: v / codigos_validos_encontrados for k, v in nutrientes_acumulados.items()}

# --- 3. Função Principal de Estatísticas (Atualizada) ---
def calcular_estatisticas_dietas(caminho_pickle_tbca: str = "mapa_tbca_completo.pkl", 
                                 caminho_gbt_json: str = "gbt.json", 
                                 caminho_mapa_txt: str = "mapa_codigo.txt"):
    
    if not os.path.exists(caminho_pickle_tbca):
        print("Erro: Pickle TBCA não encontrado.")
        return
        
    print("Carregando dados da TBCA...")
    with open(caminho_pickle_tbca, "rb") as f:
        dados_tbca = pickle.load(f)

    print("Processando mapa de códigos...")
    mapa_codigos = carregar_mapa_codigos_limpo(caminho_mapa_txt)
    
    if not os.path.exists(caminho_gbt_json):
        print(f"Erro: JSON {caminho_gbt_json} não encontrado.")
        return

    with open(caminho_gbt_json, 'r', encoding='utf-8') as f:
        dietas = json.load(f)

    print("Calculando estatísticas...")
    
    totais_diarios = defaultdict(lambda: defaultdict(list))
    totais_refeicao = defaultdict(lambda: defaultdict(list))
    
    for plano in dietas:
        for dia, refeicoes in plano.items():
            nutrientes_do_dia = defaultdict(float)
            
            # Buffer para armazenar os nutrientes de cada refeição deste dia
            # para calcularmos a proporção energética depois
            buffer_refeicoes_dia = {}
            
            # 1. Primeira passada: Calcular nutrientes absolutos e totais do dia
            for nome_refeicao, itens in refeicoes.items():
                nutrientes_da_refeicao = defaultdict(float)
                
                for item in itens:
                    nome = item.get('alimento')
                    try: qtd = float(item.get('quantidade', 0))
                    except: qtd = 0
                    
                    nutris_item = calcular_nutrientes_item(nome, qtd, mapa_codigos, dados_tbca)
                    
                    for n, v in nutris_item.items():
                        nutrientes_da_refeicao[n] += v
                        nutrientes_do_dia[n] += v
                
                # Guarda no buffer
                buffer_refeicoes_dia[nome_refeicao] = nutrientes_da_refeicao
            
            # 2. Segunda passada: Calcular proporções e salvar históricos
            total_energia_dia = nutrientes_do_dia["Energia"]

            for nome_refeicao, nutris_ref in buffer_refeicoes_dia.items():
                # Salva valores absolutos
                for n, v in nutris_ref.items():
                    totais_refeicao[nome_refeicao][n].append(v)
                
                # CÁLCULO DA PROPORÇÃO ENERGÉTICA
                if total_energia_dia > 0:
                    prop = (nutris_ref["Energia"] / total_energia_dia) * 100
                else:
                    prop = 0.0
                
                # Adiciona essa nova métrica ao dicionário da refeição
                totais_refeicao[nome_refeicao]["Proporção Energética"].append(prop)
            
            # Salva o total do dia
            for n, v in nutrientes_do_dia.items():
                totais_diarios["Geral"][n].append(v)

    # --- Exibição ---
    def formatar_saida(titulo, dados_dict):
        print(f"\n{'='*40}")
        print(f"ESTATÍSTICAS: {titulo}")
        print(f"{'='*40}")
        
        # Adicionei "Proporção Energética" na lista de prioridades
        nutrientes_foco = ["Energia", "Proporção Energética", "Carboidrato", "Proteína", "Lipídeos", "Fibra alimentar", "Sódio"]
        
        for categoria, nutris_map in dados_dict.items():
            print(f"\n>> {categoria.upper()}")
            
            todos_keys = set(nutris_map.keys())
            chaves_ordenadas = [k for k in nutrientes_foco if k in todos_keys]
            chaves_ordenadas += sorted(list(todos_keys - set(nutrientes_foco)))
            
            count_exibidos = 0
            for nutri in chaves_ordenadas:
                valores = nutris_map[nutri]
                if not valores: continue
                
                media = np.mean(valores)
                desvio = np.std(valores)
                
                if media > 0.1:
                    unidade = "g"
                    if nutri == "Energia": unidade = "kcal"
                    elif nutri == "Sódio": unidade = "mg"
                    elif nutri == "Proporção Energética": unidade = "%" # Unidade para a nova métrica
                    
                    print(f"  {nutri:.<25} {media:>8.2f} ± {desvio:<6.2f} {unidade}")
                    count_exibidos += 1
            
            if count_exibidos == 0:
                print("  (Sem dados significativos calculados)")

    formatar_saida("DIÁRIO (Média por dia)", totais_diarios)
    formatar_saida("POR REFEIÇÃO (Média por refeição)", totais_refeicao)

# Execução
calcular_estatisticas_dietas(
    caminho_pickle_tbca="mapa_tbca_completo.pkl", 
    caminho_gbt_json="gemini.json",
    caminho_mapa_txt="mapa_codigo.txt"
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calcula estatísticas nutricionais (Média e Desvio Padrão) a partir de arquivos JSON de dietas."
    )

    # Argumento posicional obrigatório: O arquivo JSON
    parser.add_argument(
        "arquivo_json", 
        type=str, 
        help="Caminho para o arquivo JSON contendo as dietas (ex: gemini.json)"
    )

    # Argumentos opcionais para os arquivos de suporte
    parser.add_argument(
        "--pickle", 
        type=str, 
        default="mapa_tbca_completo.pkl", 
        help="Caminho para o banco de dados TBCA .pkl (Padrão: mapa_tbca_completo.pkl)"
    )

    parser.add_argument(
        "--mapa", 
        type=str, 
        default="mapa_codigo.txt", 
        help="Caminho para o arquivo de texto mapa_codigo.txt (Padrão: mapa_codigo.txt)"
    )

    args = parser.parse_args()

    # Executa a função com os argumentos passados via terminal
    calcular_estatisticas_dietas(
        caminho_pickle_tbca=args.pickle,
        caminho_gbt_json=args.arquivo_json,
        caminho_mapa_txt=args.mapa
    )