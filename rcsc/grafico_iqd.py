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

from calcular_estatistica import *
# ==============================================================================
# CONFIGURAÇÕES DO IQD (Índice de Qualidade da Dieta)
# ==============================================================================

# Alvos do IQD baseados na imagem fornecida (usando o valor ideal/máximo como 100%)
# Para intervalos (ex: 3 a 5), foi utilizada a média geométrica/aritmética razoável.
ALVOS_IQD = {
    "Fruta total": 4.0,           # porções (média de 3 a 5)
    "Verduras e Legumes": 4.5,    # porções (média de 4 a 5)
    "Cereais totais": 7.0,        # porções (média de 5 a 9)
    "Leite e derivados": 3.0,     # porções
    "Carnes e ovos": 1.5,         # porções (média de 1 a 2)
    "Leguminosas": 1.0,           # porção
    "Gordura total": 30.0,        # % do VET (Limite Máximo)
    "Sódio": 2.4,                 # g (Limite Máximo)
    "Colesterol": 0.3,            # g (Limite Máximo)
    "Variedade da dieta": 8.0     # tipos de alimentos (Mínimo)
}

# Tamanho padrão estimado de porções em gramas (padrão Brasil)
PESO_PORCAO = {
    "Fruta total": 80.0,
    "Verduras e Legumes": 80.0,
    "Cereais totais": 100.0,     # Pães, massas, arroz, tubérculos
    "Leite e derivados": 200.0,  # Copo de leite / iogurte
    "Carnes e ovos": 100.0,      # Bife médio / 2 ovos
    "Leguminosas": 80.0          # Feijões (concha)
}

def mapear_grupo_iqd(grupo_tbca):
    """Mapeia os grupos originais da TBCA para as categorias do IQD."""
    if not grupo_tbca: return None
    g = grupo_tbca.lower()
    
    if "fruta" in g: return "Fruta total"
    if "vegetais" in g: return "Verduras e Legumes"
    if "nozes" in g or "cereais" in g: return "Cereais totais"
    if "leite" in g or "laticínio" in g: return "Leite e derivados"
    if "carne" in g or "ovo" in g or "pescado" in g or "ave" in g: return "Carnes e ovos"
    if "leguminosa" in g or "feijão" in g or "soja" in g: return "Leguminosas"
    
    return None

def encontrar_nutriente(nutrientes_dict, nomes_possiveis):
    """Busca o valor de um nutriente no dicionário permitindo variações de nome."""
    for n_tbca, valor in nutrientes_dict.items():
        n_lower = n_tbca.lower()
        if any(nome in n_lower for nome in nomes_possiveis):
            return valor
    return 0.0

# ==============================================================================
# EXTRAÇÃO DE DADOS PARA O IQD
# ==============================================================================

def extrair_metricas_iqd(caminho_json, mapa_codigos, dados_tbca):
    """Lê a dieta de um modelo e calcula as 10 métricas do IQD por dia."""
    with open(caminho_json, 'r', encoding='utf-8') as f:
        try: dietas = json.load(f)
        except json.JSONDecodeError: return {}

    historico_iqd = defaultdict(list)

    for plano in dietas:
        for dia, refeicoes in plano.items():
            
            # Acumuladores do dia
            porcoes_dia = defaultdict(float)
            energia_total = 0.0
            lipideos_total = 0.0
            sodio_mg_total = 0.0
            colesterol_mg_total = 0.0
            alimentos_unicos = set()
            
            for nome_refeicao, itens in refeicoes.items():
                for item in itens:
                    nome_alimento = item.get('alimento', '')
                    try: qtd_g = float(item.get('quantidade', 0))
                    except: qtd_g = 0
                    
                    if qtd_g <= 0: continue
                    alimentos_unicos.add(nome_alimento) # Para a variedade
                    
                    # Identifica o grupo TBCA do alimento para calcular as porções
                    codigos = mapa_codigos.get(nome_alimento, [])
                    if codigos:
                        # Pega o grupo do primeiro código válido
                        for code in codigos:
                            unidade = dados_tbca.get(code)
                            if unidade and unidade.grupo:
                                categoria_iqd = mapear_grupo_iqd(unidade.grupo)
                                if categoria_iqd:
                                    # Soma a porção (Quantidade ingerida / Tamanho da porção padrão)
                                    # Dividimos pelo len(codigos) para fazer a média exata do item
                                    porcoes_dia[categoria_iqd] += (qtd_g / PESO_PORCAO[categoria_iqd]) / len(codigos)
                                
                    # Calcula os nutrientes para Gordura, Sódio e Colesterol
                    nutris_item = calcular_nutrientes_item(nome_alimento, qtd_g, mapa_codigos, dados_tbca)
                    
                    energia_total += encontrar_nutriente(nutris_item, ["energia"])
                    lipideos_total += encontrar_nutriente(nutris_item, ["lipídios"])
                    sodio_mg_total += encontrar_nutriente(nutris_item, ["sódio", "sodio"])
                    colesterol_mg_total += encontrar_nutriente(nutris_item, ["colesterol"])
            
            # --- CÁLCULO FINAL DO DIA ---
            # 1 a 6. Porções dos Grupos
            for cat in ["Fruta total", "Verduras e Legumes", "Cereais totais", "Leite e derivados", "Carnes e ovos", "Leguminosas"]:
                historico_iqd[cat].append(porcoes_dia.get(cat, 0.0))
            
            # 7. Gordura Total (% do VET) -> 1g de lipídeo = 9 kcal
            if energia_total > 0:
                pct_gordura = ((lipideos_total * 9.0) / energia_total) * 100.0
            else:
                pct_gordura = 0.0
            historico_iqd["Gordura total"].append(pct_gordura)
            
            # 8 e 9. Sódio e Colesterol (Converter de mg para g)
            historico_iqd["Sódio"].append(sodio_mg_total / 1000.0)
            historico_iqd["Colesterol"].append(colesterol_mg_total / 1000.0)
            
            # 10. Variedade (Quantidade de alimentos únicos no dia)
            historico_iqd["Variedade da dieta"].append(float(len(alimentos_unicos)))
                
    return historico_iqd

# ==============================================================================
# GERAÇÃO DO GRÁFICO (COMPARATIVO RELATIVO AO ALVO DO IQD)
# ==============================================================================

def gerar_grafico_comparativo_iqd(dados_dict, nome_arquivo):
    """
    Gera um gráfico de barras agrupadas mostrando a porcentagem 
    de atingimento do alvo ideal para cada componente do IQD.
    """
    if not MATPLOTLIB_AVAILABLE: return

    modelos = list(dados_dict.keys())
    if not modelos: return

    categorias = list(ALVOS_IQD.keys())
    x = np.arange(len(categorias))
    
    total_width = 0.8
    width = total_width / len(modelos)
    offsets = np.linspace(-total_width/2 + width/2, total_width/2 - width/2, len(modelos))

    fig, ax = plt.subplots(figsize=(18, 9)) # Bem largo para caber as 10 métricas
    cores = {'GBT': '#4c72b0', 'DeepSeek': '#dd8452', 'Gemini': '#55a868'}

    for i, modelo in enumerate(modelos):
        pcts_alcancados = []
        
        for cat in categorias:
            valores = dados_dict[modelo].get(cat, [])
            media = np.mean(valores) if valores else 0
            alvo = ALVOS_IQD[cat]
            
            # Para Sódio, Colesterol e Gordura, o Alvo é um LIMITE (Teto). 
            # Mas a lógica matemática de (media/alvo)*100 continua sendo a melhor forma de visualizar
            # Ex: 1.2g de Sódio (Alvo 2.4g) = 50% (Ótimo). 4.8g de Sódio = 200% (Estourou).
            porcentagem = (media / alvo) * 100
            pcts_alcancados.append(porcentagem)

        cor = cores.get(modelo, '#888888')
        rects = ax.bar(x + offsets[i], pcts_alcancados, width, label=modelo, 
                       color=cor, edgecolor='black', alpha=0.9)
        
        ax.bar_label(rects, fmt='%.0f%%', padding=4, fontsize=10, fontweight='bold', rotation=45)

    # Linha Vermelha de 100% (O Ideal ou o Limite)
    ax.axhline(y=100, color='red', linestyle='--', linewidth=2, 
               label='100% (Meta/Limite Recomendado)')

    # Ajuste e anotação importante
    ax.set_ylabel('% em relação ao alvo do IQD', fontsize=14, fontweight='bold')
    
    # Nota de rodapé na imagem explicando a linha
    fig.text(0.5, 0.01, 
             "*Nota: Para Frutas, Verduras, Cereais, Leite, Carnes, Leguminosas e Variedade, atingir ou ultrapassar 100% é positivo.\n"
             "Para Gordura total, Sódio e Colesterol, valores acima de 100% indicam violação do limite recomendado.", 
             ha='center', fontsize=11, style='italic', color='darkred')

    ax.set_xticks(x)
    ax.set_xticklabels(categorias, fontsize=13, fontweight='bold', rotation=30, ha='right')
    ax.tick_params(axis='y', labelsize=12)
    
    ax.legend(loc='upper right', fontsize=12, title="Modelos", title_fontsize=12)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)

    plt.margins(y=0.2)
    # Adicionando espaço embaixo para o texto de rodapé não cortar
    plt.subplots_adjust(bottom=0.25)

    plt.savefig(nome_arquivo, dpi=300)
    print(f"[GRÁFICO IQD] Salvo: {nome_arquivo}")
    plt.close()

# ==============================================================================
# ORQUESTRAÇÃO
# ==============================================================================

def executar_analise_iqd(caminho_pickle, caminho_mapa):
    print("--- Análise do Índice de Qualidade da Dieta (IQD) ---")
    
    if not os.path.exists(caminho_pickle):
        print("Erro: Banco TBCA (.pkl) não encontrado.")
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
            continue
            
        dados_iqd = extrair_metricas_iqd(arquivo, mapa_codigos, dados_tbca)
        if dados_iqd:
            dados_comparativos[nome_modelo] = dados_iqd
            print(f"Dados do IQD extraídos para {nome_modelo}.")

    if len(dados_comparativos) > 1:
        gerar_grafico_comparativo_iqd(dados_comparativos, "comparativo_iqd_relativo.png")
    else:
        print("Não há modelos suficientes para gerar o gráfico comparativo do IQD.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera gráfico de análise do Índice de Qualidade da Dieta (IQD).")
    parser.add_argument("--pickle", type=str, default="mapa_tbca_completo.pkl", help="Banco TBCA")
    parser.add_argument("--mapa", type=str, default="mapa_codigo.txt", help="Mapa txt")
    args = parser.parse_args()

    executar_analise_iqd(args.pickle, args.mapa)