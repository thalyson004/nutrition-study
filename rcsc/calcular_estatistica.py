import json
import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field
import os
import pickle
import re
import argparse
import sys

import matplotlib.pyplot as plt
MATPLOTLIB_AVAILABLE = True


@dataclass
class TbcaUnit:
    codigo: str
    nome: str
    grupo: str
    link: str
    
    nutrientes: dict = field(default_factory=dict)

from get_data import *

# ==============================================================================
# 1. FUNÇÕES AUXILIARES (CARREGAMENTO E CÁLCULO BÁSICO)
# ==============================================================================

def carregar_mapa_codigos_limpo(caminho_arquivo: str) -> dict:
    if os.path.exists("mapa_codigo.pkl"):
        try:
            with open("mapa_codigo.pkl", "rb") as f:
                return pickle.load(f)
        except: pass 
    
    mapa = {}
    if not os.path.exists(caminho_arquivo):
        return mapa

    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: continue
                partes = linha.split()
                codigos_encontrados = []
                while partes:
                    ultimo_token = partes[-1]
                    eh_codigo = (ultimo_token.startswith("BR") or ultimo_token == "-" or ("," in ultimo_token and "BR" in ultimo_token))
                    if eh_codigo:
                        token = partes.pop()
                        if token != "-":
                            sub_cods = [c.strip() for c in token.split(',')]
                            for c in sub_cods:
                                if c and c.startswith("BR"): codigos_encontrados.append(c)
                    else: break
                if partes:
                    nome_alimento = " ".join(partes)
                    mapa[nome_alimento] = codigos_encontrados     
    except Exception as e:
        print(f"Erro ao processar mapa: {e}")

    try:
        with open("mapa_codigo.pkl", "wb") as f: pickle.dump(mapa, f)
    except: pass
    return mapa

def calcular_nutrientes_item(nome_alimento: str, quantidade_g: float, mapa_codigos: dict, dados_tbca: dict) -> dict:
    codigos = mapa_codigos.get(nome_alimento)
    if not codigos: return {}

    nutrientes_acumulados = defaultdict(float)
    codigos_validos = 0

    for code in codigos:
        unidade = dados_tbca.get(code)
        if unidade and unidade.nutrientes:
            codigos_validos += 1
            for nutriente, valor_por_100g in unidade.nutrientes.items():
                qtd_real = (valor_por_100g * quantidade_g) / 100.0
                nutrientes_acumulados[nutriente] += qtd_real
    
    if codigos_validos == 0: return {}
    return {k: v / codigos_validos for k, v in nutrientes_acumulados.items()}

# ==============================================================================
# 2. FUNÇÕES DE GRÁFICOS
# ==============================================================================

def gerar_grafico_individual(totais_refeicao, nome_base_arquivo):
    """
    Gera gráfico de barras VERTICAIS para uma única dieta.
    """
    if not MATPLOTLIB_AVAILABLE: return

    # 1. Definição de Ordem e Cores
    ordem_refeicoes = ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
    
    cores_refeicoes = {
        "Café da Manhã": "#a1c9f4",      # Azul suave
        "Lanche da Manhã": "#ffb482",    # Laranja suave
        "Almoço": "#8de5a1",             # Verde suave
        "Lanche da Tarde": "#ff9f9b",    # Vermelho suave
        "Jantar": "#d0bbff",             # Roxo suave
        "Ceia": "#debb9b"                # Marrom/Bege
    }
    fallback_colors = plt.cm.Pastel1.colors

    # 2. Prepara Dados Ordenados
    labels = []
    means = []
    bar_colors = []

    refeicoes_presentes = [r for r in ordem_refeicoes if r in totais_refeicao]
    outras_refeicoes = [r for r in totais_refeicao if r not in ordem_refeicoes]
    lista_final = refeicoes_presentes + outras_refeicoes

    for i, refeicao in enumerate(lista_final):
        dados = totais_refeicao.get(refeicao, {})
        valores_energia = dados.get("Energia", [])
        
        if valores_energia:
            media = np.mean(valores_energia)
            
            if media > 1: # Filtra vazios
                labels.append(refeicao)
                means.append(media)
                if refeicao in cores_refeicoes:
                    bar_colors.append(cores_refeicoes[refeicao])
                else:
                    bar_colors.append(fallback_colors[i % len(fallback_colors)])

    if not means:
        print("Sem dados de energia suficientes para gráfico individual.")
        return

    # 3. Plotagem
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(12, 7))

    rects = ax.bar(x, means, color=bar_colors, edgecolor='black', alpha=0.9, width=0.6)
    ax.bar_label(rects, fmt='%.0f', padding=3, fontsize=11, fontweight='bold')

    ax.set_ylabel('Energia Média (kcal)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight='bold')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    plt.margins(y=0.1)
    plt.tight_layout()

    nome_arquivo_png = f"{nome_base_arquivo}_distribuicao_individual.png"
    plt.savefig(nome_arquivo_png, dpi=300)
    print(f"[GRÁFICO INDIVIDUAL] Salvo: {nome_arquivo_png}")
    plt.close()

def gerar_grafico_comparativo(dados_modelos: dict):
    """
    Gera DOIS gráficos comparativos:
    1. Absoluto (Kcal)
    2. Relativo (Porcentagem)
    """
    if not MATPLOTLIB_AVAILABLE: return

    ordem_refeicoes = ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
    labels = [ref for ref in ordem_refeicoes if any(ref in d for d in dados_modelos.values())]
    
    if not labels:
        print("Sem dados compatíveis para gráfico comparativo.")
        return

    cores = {'GBT': '#4c72b0', 'DeepSeek': '#dd8452', 'Gemini': '#55a868'}
    x = np.arange(len(labels))
    width = 0.25

    # ==========================================================================
    # GRÁFICO 1: ABSOLUTO (KCAL)
    # ==========================================================================
    fig, ax = plt.subplots(figsize=(14, 9)) # Mais altura
    multiplier = 0

    for modelo, dados_refeicao in dados_modelos.items():
        means = []
        for refeicao in labels:
            valores = dados_refeicao.get(refeicao, [])
            means.append(np.mean(valores) if valores else 0)
        
        offset = width * multiplier
        rects = ax.bar(x + offset, means, width, label=modelo, 
                       color=cores.get(modelo, 'gray'), edgecolor='black', alpha=0.9)
        
        ax.bar_label(rects, 
                     fmt='%.0f', 
                     padding=3, 
                     fontsize=14,        # Fonte 14
                     fontweight='bold', 
                     rotation=60)        # Diagonal
        
        multiplier += 1

    ax.set_ylabel('Energia Média (kcal)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width) 
    ax.set_xticklabels(labels, fontsize=14, fontweight='bold')
    ax.tick_params(axis='y', labelsize=14)
    ax.legend(loc='upper right', fontsize=14, title="Modelos", title_fontsize=12)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    
    plt.margins(y=0.2) # Margem extra para o texto caber
    plt.tight_layout()

    nome_arquivo_kcal = "comparativo_modelos_energia_kcal.png"
    plt.savefig(nome_arquivo_kcal, dpi=300)
    print(f"[GRÁFICO COMPARATIVO KCAL] Salvo: {nome_arquivo_kcal}")
    plt.close()

    # ==========================================================================
    # GRÁFICO 2: PORCENTAGEM (%)
    # ==========================================================================
    fig, ax = plt.subplots(figsize=(14, 9))
    multiplier = 0

    for modelo, dados_refeicao in dados_modelos.items():
        means = []
        for refeicao in labels:
            valores = dados_refeicao.get(refeicao, [])
            means.append(np.mean(valores) if valores else 0)
        
        total_energia_modelo = sum(means)
        if total_energia_modelo > 0:
            pcts = [(m / total_energia_modelo) * 100 for m in means]
        else:
            pcts = [0] * len(means)

        offset = width * multiplier
        rects = ax.bar(x + offset, pcts, width, label=modelo, 
                       color=cores.get(modelo, 'gray'), edgecolor='black', alpha=0.9)
        
        ax.bar_label(rects, 
                     fmt='%.1f%%', 
                     padding=3, 
                     fontsize=14,        # Fonte 14
                     fontweight='bold', 
                     rotation=60)        # Diagonal
                     
        multiplier += 1

    ax.set_ylabel('Distribuição Energética (%)', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width) 
    ax.set_xticklabels(labels, fontsize=14, fontweight='bold')
    ax.tick_params(axis='y', labelsize=14)
    ax.legend(loc='upper right', fontsize=14, title="Modelos", title_fontsize=12)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    
    plt.margins(y=0.2)
    plt.tight_layout()

    nome_arquivo_pct = "comparativo_modelos_energia_porcentagem.png"
    plt.savefig(nome_arquivo_pct, dpi=300)
    print(f"[GRÁFICO COMPARATIVO %] Salvo: {nome_arquivo_pct}")
    plt.close()

# ==============================================================================
# 3. LÓGICA DE ANÁLISE
# ==============================================================================

def analisar_arquivo_unico(caminho_json, mapa_codigos, dados_tbca):
    if not os.path.exists(caminho_json):
        print(f"Erro: Arquivo {caminho_json} não encontrado.")
        return

    base_nome = os.path.splitext(caminho_json)[0]
    arquivo_saida_txt = f"{base_nome}_estatisticas.txt"
    
    def log(msg):
        print(msg)
        with open(arquivo_saida_txt, "a", encoding="utf-8") as f: f.write(msg + "\n")
    
    open(arquivo_saida_txt, "w").close()
    
    log(f"--- Relatório Individual: {caminho_json} ---")

    with open(caminho_json, 'r', encoding='utf-8') as f:
        try: dietas = json.load(f)
        except: 
            log("Erro JSON inválido.")
            return

    totais_diarios = defaultdict(lambda: defaultdict(list))
    totais_refeicao = defaultdict(lambda: defaultdict(list))
    
    for plano in dietas:
        for dia, refeicoes in plano.items():
            nutrientes_do_dia = defaultdict(float)
            buffer_refeicoes = {}
            
            for nome_refeicao, itens in refeicoes.items():
                nutrientes_ref = defaultdict(float)
                for item in itens:
                    try: qtd = float(item.get('quantidade', 0))
                    except: qtd = 0
                    nutris = calcular_nutrientes_item(item.get('alimento'), qtd, mapa_codigos, dados_tbca)
                    for n, v in nutris.items():
                        nutrientes_ref[n] += v
                        nutrientes_do_dia[n] += v
                buffer_refeicoes[nome_refeicao] = nutrientes_ref
            
            total_energia = nutrientes_do_dia["Energia"]
            for nome_refeicao, nutris in buffer_refeicoes.items():
                for n, v in nutris.items():
                    totais_refeicao[nome_refeicao][n].append(v)
                prop = (nutris["Energia"] / total_energia * 100) if total_energia > 0 else 0
                totais_refeicao[nome_refeicao]["Proporção Energética"].append(prop)
            
            for n, v in nutrientes_do_dia.items():
                totais_diarios["Geral"][n].append(v)

    def formatar_saida(titulo, dados_dict):
        log(f"\n>> {titulo}")
        nutrientes_foco = ["Energia", "Proporção Energética", "Carboidrato", "Proteína", "Lipídeos", "Fibra alimentar", "Sódio"]
        for categoria, nutris_map in dados_dict.items():
            log(f"   [{categoria.upper()}]")
            todos = set(nutris_map.keys())
            chaves = [k for k in nutrientes_foco if k in todos] + sorted(list(todos - set(nutrientes_foco)))
            for nutri in chaves:
                vals = nutris_map[nutri]
                if not vals: continue
                media = np.mean(vals)
                if media > 0.1:
                    un = "kcal" if nutri == "Energia" else "%" if nutri == "Proporção Energética" else "g"
                    if nutri == "Sódio": un = "mg"
                    log(f"    {nutri:.<25} {media:>8.2f} ± {np.std(vals):<6.2f} {un}")

    formatar_saida("MÉDIA DIÁRIA", totais_diarios)
    formatar_saida("MÉDIA POR REFEIÇÃO", totais_refeicao)
    
    print(f"[RELATÓRIO TXT] Salvo: {arquivo_saida_txt}")
    gerar_grafico_individual(totais_refeicao, base_nome)


def executar_comparativo(mapa_codigos, dados_tbca):
    print("\n--- Iniciando Análise Comparativa ---")
    arquivos_modelos = {"GBT": "gbt.json", "DeepSeek": "deepseek.json", "Gemini": "gemini.json"}
    
    for mod, arq in arquivos_modelos.items():
        if not os.path.exists(arq) and os.path.exists(os.path.join("rcsc", arq)):
            arquivos_modelos[mod] = os.path.join("rcsc", arq)

    dados_consolidados = {}

    for nome_modelo, arquivo in arquivos_modelos.items():
        if not os.path.exists(arquivo):
            print(f"Aviso: Arquivo do modelo {nome_modelo} ({arquivo}) não encontrado.")
            continue
            
        with open(arquivo, 'r', encoding='utf-8') as f:
            try: dietas = json.load(f)
            except: continue
        
        dados_energia_refeicao = defaultdict(list)
        for plano in dietas:
            for dia, refeicoes in plano.items():
                for nome_refeicao, itens in refeicoes.items():
                    energia_total = 0
                    for item in itens:
                        try: qtd = float(item.get('quantidade', 0))
                        except: qtd = 0
                        nutris = calcular_nutrientes_item(item.get('alimento'), qtd, mapa_codigos, dados_tbca)
                        energia_total += nutris.get("Energia", 0)
                    dados_energia_refeicao[nome_refeicao].append(energia_total)
        
        dados_consolidados[nome_modelo] = dados_energia_refeicao
        print(f"Dados processados: {nome_modelo}")

    if dados_consolidados:
        gerar_grafico_comparativo(dados_consolidados)
    else:
        print("Não há dados suficientes para o comparativo.")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Análise Nutricional de Dietas (Individual e Comparativa)")
    parser.add_argument("arquivo_json", nargs='?', type=str, help="Caminho do arquivo JSON para análise individual")
    parser.add_argument("--comparar", action="store_true", help="Gera o gráfico comparativo entre GBT, DeepSeek e Gemini")
    parser.add_argument("--pickle", type=str, default="mapa_tbca_completo.pkl", help="Banco TBCA")
    parser.add_argument("--mapa", type=str, default="mapa_codigo.txt", help="Mapa txt")

    args = parser.parse_args()

    if not os.path.exists(args.pickle):
        print(f"Erro Crítico: {args.pickle} não encontrado.")
        sys.exit(1)

    print("Carregando bases de dados...")
    with open(args.pickle, "rb") as f: dados_tbca = pickle.load(f)
    mapa_codigos = carregar_mapa_codigos_limpo(args.mapa)

    executou_algo = False
    if args.arquivo_json:
        analisar_arquivo_unico(args.arquivo_json, mapa_codigos, dados_tbca)
        executou_algo = True

    if args.comparar:
        executar_comparativo(mapa_codigos, dados_tbca)
        executou_algo = True

    if not executou_algo:
        print("\nNenhuma ação definida. Uso:")
        print("  1. Analisar arquivo único:  python main.py meuarquivo.json")
        print("  2. Gerar comparativo:       python main.py --comparar")