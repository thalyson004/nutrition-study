import json
import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
import os
import pickle
import argparse
import sys

# Tenta importar matplotlib
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Aviso: 'matplotlib' não encontrado. Gráficos não serão gerados.")
    

@dataclass
class TbcaUnit:
    codigo: str
    nome: str
    grupo: str
    link: str
    
    nutrientes: dict = field(default_factory=dict)

# --- Importa as funções do seu script anterior ---
try:
    from calcular_estatistica import carregar_mapa_codigos_limpo, calcular_nutrientes_item, TbcaUnit
except ImportError:
    print("Erro: Não foi possível importar as funções do 'main.py'.")
    print("Certifique-se de que o script anterior se chama 'main.py' e está na mesma pasta.")
    sys.exit(1)

# ==============================================================================
# CONFIGURAÇÕES E VALORES DIÁRIOS (VD) RECOMENDADOS
# Valores baseados nas diretrizes médias para adultos (ANVISA/FDA - 2000 kcal)
# ==============================================================================

MACROS = ["Energia", "Proteína", "Lipídeos Totais", "Gordura Saturada"]
MICROS = ["Cálcio", "Zinco", "Selênio", "Ferro", "Vitamina C", "Vitamina B12", 
          "Folato", "Colesterol", "Fibras", "Magnésio"]

VALORES_DIARIOS_RECOMENDADOS = {
    "Energia": 2000.0,         # kcal
    "Proteína": 50.0,          # g
    "Lipídeos Totais": 65.0,   # g
    "Gordura Saturada": 20.0,  # g (Limite)
    "Cálcio": 1000.0,          # mg
    "Zinco": 11.0,             # mg
    "Selênio": 55.0,           # mcg
    "Ferro": 14.0,             # mg
    "Vitamina C": 90.0,        # mg
    "Vitamina B12": 2.4,       # mcg
    "Folato": 400.0,           # mcg
    "Colesterol": 300.0,       # mg (Limite)
    "Fibras": 25.0,            # g
    "Magnésio": 400.0          # mg
}

def normalizar_nome_nutriente(nome_tbca):
    n = nome_tbca.lower()
    if n == "energia" or "energia" in n: return "Energia"
    if "proteína" in n or "proteina" in n: return "Proteína"
    if "lipídeos" in n or "lipidios" in n or "lipídios" in n: return "Lipídeos Totais"
    if "saturados" in n or "saturada" in n: return "Gordura Saturada"
    if "cálcio" in n or "calcio" in n: return "Cálcio"
    if "zinco" in n: return "Zinco"
    if "selênio" in n or "selenio" in n: return "Selênio"
    if "ferro" in n: return "Ferro"
    if "vitamina c" in n: return "Vitamina C"
    if "vitamina b12" in n or "cobalamina" in n: return "Vitamina B12"
    if "folato" in n or "fólico" in n or "folico" in n: return "Folato"
    if "colesterol" in n: return "Colesterol"
    if "fibra" in n: return "Fibras"
    if "magnésio" in n or "magnesio" in n: return "Magnésio"
    return None 

# ==============================================================================
# EXTRAÇÃO DE DADOS
# ==============================================================================

def extrair_totais_diarios(caminho_json, mapa_codigos, dados_tbca):
    with open(caminho_json, 'r', encoding='utf-8') as f:
        try: dietas = json.load(f)
        except json.JSONDecodeError: return {}

    totais_dias = defaultdict(list)

    for plano in dietas:
        for dia, refeicoes in plano.items():
            nutris_dia = defaultdict(float)
            for nome_refeicao, itens in refeicoes.items():
                for item in itens:
                    try: qtd = float(item.get('quantidade', 0))
                    except: qtd = 0
                    
                    nutris_item = calcular_nutrientes_item(item.get('alimento'), qtd, mapa_codigos, dados_tbca)
                    
                    for nome_tbca, valor in nutris_item.items():
                        nome_norm = normalizar_nome_nutriente(nome_tbca)
                        if nome_norm: nutris_dia[nome_norm] += valor
            
            for nutri_foco in MACROS + MICROS:
                totais_dias[nutri_foco].append(nutris_dia.get(nutri_foco, 0.0))
                
    return totais_dias

# ==============================================================================
# GERAÇÃO DO GRÁFICO (BARRAS AGRUPADAS - PORCENTAGEM)
# ==============================================================================

def gerar_grafico_percentual_agrupado(dados_dict, lista_nutrientes, nome_arquivo):
    if not MATPLOTLIB_AVAILABLE: return

    modelos = list(dados_dict.keys())
    if not modelos: return

    x = np.arange(len(lista_nutrientes))
    
    # Cálculos para alinhar as barras agrupadas
    total_width = 0.8
    width = total_width / len(modelos)
    offsets = np.linspace(-total_width/2 + width/2, total_width/2 - width/2, len(modelos))

    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Cores fixas para modelos comparativos
    cores_modelos = {'GBT': '#4c72b0', 'DeepSeek': '#dd8452', 'Gemini': '#55a868'}
    
    # Paleta de cores distintas para os gráficos individuais (tem cores suficientes para os micros)
    paleta_individual = plt.cm.Set3.colors 

    for i, modelo in enumerate(modelos):
        pcts = []
        for nutri in lista_nutrientes:
            valores = dados_dict[modelo].get(nutri, [])
            media_absoluta = np.mean(valores) if valores else 0
            vd = VALORES_DIARIOS_RECOMENDADOS.get(nutri, 1) # Evita divisão por zero
            
            porcentagem = (media_absoluta / vd) * 100
            pcts.append(porcentagem)

        # Lógica de Cor: Uma cor por nutriente no Individual, uma cor por modelo no Comparativo
        if len(modelos) == 1:
            cor_usada = [paleta_individual[j % len(paleta_individual)] for j in range(len(lista_nutrientes))]
        else:
            cor_usada = cores_modelos.get(modelo, '#4c72b0')

        # Cria as barras
        rects = ax.bar(x + offsets[i], pcts, width, 
                       label=modelo if len(modelos) > 1 else None, 
                       color=cor_usada, edgecolor='black', alpha=0.9)
        
        # Valores escritos sobre as barras
        ax.bar_label(rects, fmt='%.0f%%', padding=4, fontsize=11, fontweight='bold', rotation=45)

    # Linha Vermelha do Ideal (100%)
    ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='100% (Recomendação Diária)')

    # Estilização Profissional (Sem Título)
    ax.set_ylabel('% do Valor Diário Recomendado', fontsize=14, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(lista_nutrientes, fontsize=14, fontweight='bold', rotation=45, ha='right')
    ax.tick_params(axis='y', labelsize=12)
    
    # Mostra a legenda dos modelos só se for comparativo. 
    # Se for individual, mostra só a legenda da linha de 100%.
    if len(modelos) > 1:
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=12, title="Modelos", title_fontsize=12)
    else:
        ax.legend(loc='upper right', fontsize=12)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)

    plt.margins(y=0.15)
    plt.tight_layout()

    plt.savefig(nome_arquivo, dpi=300)
    print(f"[GRÁFICO PERCENTUAL] Salvo: {nome_arquivo}")
    plt.close()

# ==============================================================================
# ORQUESTRAÇÃO PRINCIPAL
# ==============================================================================

def executar_analise_total(caminho_pickle, caminho_mapa):
    print("--- Análise Percentual de Nutrientes (Em Relação à Meta Diária) ---")
    
    if not os.path.exists(caminho_pickle):
        print("Erro: Banco de dados TBCA (.pkl) não encontrado.")
        return

    print("Carregando bases...")
    with open(caminho_pickle, "rb") as f: dados_tbca = pickle.load(f)
    mapa_codigos = carregar_mapa_codigos_limpo(caminho_mapa)

    arquivos_modelos = {"GBT": "gbt.json", "DeepSeek": "deepseek.json", "Gemini": "gemini.json"}
    dados_comparativos = {}

    print("\n[PROCESSANDO ARQUIVOS]")
    for nome_modelo, arquivo in arquivos_modelos.items():
        if not os.path.exists(arquivo) and os.path.exists(os.path.join("rcsc", arquivo)):
            arquivo = os.path.join("rcsc", arquivo)

        if not os.path.exists(arquivo):
            print(f"Ignorando {nome_modelo}: arquivo não encontrado.")
            continue
            
        totais_diarios = extrair_totais_diarios(arquivo, mapa_codigos, dados_tbca)
        if totais_diarios:
            dados_comparativos[nome_modelo] = totais_diarios
            
            # Gráficos Individuais
            dados_individuais = {"Individual": totais_diarios}
            gerar_grafico_percentual_agrupado(dados_individuais, MACROS, 
                                              f"{nome_modelo}_macronutrientes_pct.png")
            gerar_grafico_percentual_agrupado(dados_individuais, MICROS, 
                                              f"{nome_modelo}_micronutrientes_pct.png")

    # Gráficos Comparativos
    if len(dados_comparativos) > 1:
        print("\n[GERANDO GRÁFICOS COMPARATIVOS]")
        gerar_grafico_percentual_agrupado(dados_comparativos, MACROS, 
                                          "comparativo_macronutrientes_pct.png")
        
        gerar_grafico_percentual_agrupado(dados_comparativos, MICROS, 
                                          "comparativo_micronutrientes_pct.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera gráficos de Macro/Micronutrientes agrupados e percentuais.")
    parser.add_argument("--pickle", type=str, default="mapa_tbca_completo.pkl", help="Banco TBCA")
    parser.add_argument("--mapa", type=str, default="mapa_codigo.txt", help="Mapa txt")
    args = parser.parse_args()

    executar_analise_total(args.pickle, args.mapa)