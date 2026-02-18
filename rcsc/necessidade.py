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
# 1. CÁLCULO DE METAS E GERAÇÃO DE RELATÓRIO DO PACIENTE
# ==============================================================================
def calcular_metas_nutricionais(peso_kg, altura_m, idade_anos, sexo, nivel_atividade, objetivo):
    """
    Retorna um dicionário com as metas e um texto formatado com o passo a passo dos cálculos.
    """
    altura_cm = altura_m * 100
    sexo_lower = sexo.strip().lower()
    
    # IMC
    imc = peso_kg / (altura_m ** 2)
    
    # TMB (Mifflin-St Jeor)
    if sexo_lower == 'feminino':
        tmb = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade_anos) - 161
        eq_str = f"(10 x {peso_kg}) + (6.25 x {altura_cm}) - (5 x {idade_anos}) - 161"
    else:
        tmb = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade_anos) + 5
        eq_str = f"(10 x {peso_kg}) + (6.25 x {altura_cm}) - (5 x {idade_anos}) + 5"
        
    fatores_fa = {'sedentario': 1.2, 'leve': 1.375, 'moderado': 1.55, 'intenso': 1.725}
    fa = fatores_fa.get(nivel_atividade.strip().lower(), 1.2)
    get = tmb * fa
    
    # Objetivo
    objetivo_lower = objetivo.strip().lower()
    if 'emagrecimento' in objetivo_lower:
        vet = get - 500
        ajuste_str = "Déficit de 500 kcal para Emagrecimento Saudável"
    elif 'hipertrofia' in objetivo_lower:
        vet = get + 300
        ajuste_str = "Superávit de 300 kcal para Hipertrofia"
    else:
        vet = get
        ajuste_str = "Manutenção (Sem déficit/superávit)"
        
    if sexo_lower == 'feminino' and vet < 1200: 
        vet = 1200
        ajuste_str += " (Ajustado para o mínimo de segurança: 1200 kcal)"

    # Macronutrientes
    proteina_g = peso_kg * 1.5 # 1.5g/kg
    lipideos_g = (vet * 0.25) / 9.0 # 25% das calorias
    carbo_g = (vet - (proteina_g * 4.0) - (lipideos_g * 9.0)) / 4.0
    gordura_sat_g = (vet * 0.10) / 9.0 # Máx 10% do VET

    # Dicionário com as metas numéricas
    metas = {
        "Energia": vet,
        "Proteínas": proteina_g,
        "Carboidratos": carbo_g,
        "Lipídios totais": lipideos_g,
        "Gordura Saturada": gordura_sat_g,
        "Cálcio": 1000.0,
        "Zinco": 8.0 if sexo_lower == 'feminino' else 11.0,
        "Selênio": 55.0,
        "Ferro": 18.0 if sexo_lower == 'feminino' else 8.0,
        "Vitamina C": 75.0 if sexo_lower == 'feminino' else 90.0,
        "Vitamina B12": 2.4,
        "Folato": 400.0,
        "Colesterol": 300.0,
        "Fibras": 25.0,
        "Magnésio": 310.0 if sexo_lower == 'feminino' else 400.0,
        "Sódio": 2000.0
    }
    
    # Montagem do Relatório em Texto
    relatorio = f"""==================================================
RESUMO DO PERFIL DO PACIENTE
==================================================
Sexo: {sexo.capitalize()}
Idade: {idade_anos} anos
Peso: {peso_kg} kg
Altura: {altura_m} m
IMC: {imc:.1f} kg/m²
Nível de Atividade: {nivel_atividade.capitalize()}
Objetivo: {objetivo}

==================================================
PASSO A PASSO DO CÁLCULO ENERGÉTICO
==================================================
1. Taxa Metabólica Basal (TMB):
   Equação utilizada: Mifflin-St Jeor
   TMB = {eq_str}
   TMB = {tmb:.1f} kcal

2. Gasto Energético Total (GET):
   Fator de Atividade (FA) = {fa}
   GET = {tmb:.1f} x {fa}
   GET = {get:.1f} kcal

3. Meta Calórica (VET):
   Ajuste: {ajuste_str}
   VET Final = {vet:.1f} kcal

==================================================
METAS NUTRICIONAIS RECOMENDADAS
==================================================
>> MACRONUTRIENTES
   Energia: {metas['Energia']:.1f} kcal
   Proteínas: {metas['Proteínas']:.1f} g ({metas['Proteínas']*4/vet*100:.1f}%)
   Carboidratos: {metas['Carboidratos']:.1f} g ({metas['Carboidratos']*4/vet*100:.1f}%)
   Lipídios totais: {metas['Lipídios totais']:.1f} g (25.0%)
   Gordura Saturada: < {metas['Gordura Saturada']:.1f} g (Máximo de 10%)

>> MICRONUTRIENTES E FIBRAS
   Fibras: > {metas['Fibras']} g
   Cálcio: {metas['Cálcio']} mg
   Zinco: {metas['Zinco']} mg
   Selênio: {metas['Selênio']} mcg
   Ferro: {metas['Ferro']} mg
   Vitamina C: {metas['Vitamina C']} mg
   Vitamina B12: {metas['Vitamina B12']} mcg
   Folato: {metas['Folato']} mcg
   Magnésio: {metas['Magnésio']} mg
   Sódio: < {metas['Sódio']} mg
   Colesterol: < {metas['Colesterol']} mg
==================================================
"""
    return metas, relatorio

# ==============================================================================
# 2. EXTRAÇÃO E NORMALIZAÇÃO DOS DADOS
# ==============================================================================

MACROS = ["Energia", "Proteínas", "Lipídios totais", "Gordura Saturada"]
MICROS = ["Cálcio", "Zinco", "Selênio", "Ferro", "Vitamina C", "Vitamina B12", 
          "Folato", "Colesterol", "Fibras", "Magnésio", "Sódio"]

def normalizar_nome_nutriente(nome_tbca):
    n = nome_tbca.lower()
    if n == "energia" or "energia" in n: return "Energia"
    if "proteína" in n or "proteina" in n: return "Proteínas"
    if "lipídeos" in n or "lipidios" in n or "lipídios" in n: return "Lipídios totais"
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
    if "sódio" in n or "sodio" in n: return "Sódio"
    return None 

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
# 3. GERAÇÃO DOS GRÁFICOS (RELATIVO ÀS METAS)
# ==============================================================================
def gerar_grafico_relativo(dados_dict, metas, lista_nutrientes, nome_arquivo):
    if not MATPLOTLIB_AVAILABLE: return

    modelos = list(dados_dict.keys())
    if not modelos: return

    x = np.arange(len(lista_nutrientes))
    total_width = 0.8
    width = total_width / len(modelos)
    offsets = np.linspace(-total_width/2 + width/2, total_width/2 - width/2, len(modelos))

    fig, ax = plt.subplots(figsize=(16, 9))
    
    cores_modelos = {'GBT': '#4c72b0', 'DeepSeek': '#dd8452', 'Gemini': '#55a868'}
    paleta_individual = plt.cm.Set3.colors 

    for i, modelo in enumerate(modelos):
        pcts = []
        for nutri in lista_nutrientes:
            valores = dados_dict[modelo].get(nutri, [])
            media_consumo = np.mean(valores) if valores else 0
            
            meta_esperada = metas.get(nutri, 1) 
            porcentagem = (media_consumo / meta_esperada) * 100
            pcts.append(porcentagem)

        if len(modelos) == 1:
            cor_usada = [paleta_individual[j % len(paleta_individual)] for j in range(len(lista_nutrientes))]
        else:
            cor_usada = cores_modelos.get(modelo, '#888888')

        rects = ax.bar(x + offsets[i], pcts, width, 
                       label=modelo if len(modelos) > 1 else None, 
                       color=cor_usada, edgecolor='black', alpha=0.9)
        
        ax.bar_label(rects, fmt='%.0f%%', padding=4, fontsize=11, fontweight='bold', rotation=45)

    # Linha Vermelha de 100%
    ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='100% (Meta Calculada)')

    ax.set_ylabel('% em relação à Meta Recomendada', fontsize=14, fontweight='bold')
    
    ax.set_xticks(x)
    ax.set_xticklabels(lista_nutrientes, fontsize=14, fontweight='bold', rotation=45, ha='right')
    ax.tick_params(axis='y', labelsize=12)
    
    if len(modelos) > 1:
        ax.legend(loc='upper right', fontsize=12, title="Modelos", title_fontsize=12)
    else:
        ax.legend(loc='upper right', fontsize=12)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)

    plt.margins(y=0.2)
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300)
    print(f"Gráfico salvo: {nome_arquivo}")
    plt.close()

# ==============================================================================
# 4. ORQUESTRAÇÃO PRINCIPAL
# ==============================================================================
def executar():
    print("--- Análise de Adequação de Dieta vs Metas ---")
    
    # 1. Definição do Perfil
    metas_paciente, texto_relatorio = calcular_metas_nutricionais(
        peso_kg=71.0, 
        altura_m=1.62, 
        idade_anos=30, 
        sexo='Feminino', 
        nivel_atividade='leve', 
        objetivo='Emagrecimento'
    )
    
    # SALVANDO O RELATÓRIO EM TEXTO
    with open("relatorio_metas_paciente.txt", "w", encoding="utf-8") as f_rel:
        f_rel.write(texto_relatorio)
    print(">> Arquivo salvo: 'relatorio_metas_paciente.txt' (Contém todo o passo a passo matemático)")

    # 2. Carregar Bases de Dados
    if not os.path.exists("mapa_tbca_completo.pkl"):
        print("Erro: Banco 'mapa_tbca_completo.pkl' não encontrado.")
        return

    with open("mapa_tbca_completo.pkl", "rb") as f: 
        dados_tbca = pickle.load(f)
    mapa_codigos = carregar_mapa_codigos_limpo("mapa_codigo.txt")

    arquivos_modelos = {"GBT": "gbt.json", "DeepSeek": "deepseek.json", "Gemini": "gemini.json"}
    dados_comparativos = {}

    # 3. Processamento e Gráficos Individuais
    for nome_modelo, arquivo in arquivos_modelos.items():
        if not os.path.exists(arquivo) and os.path.exists(os.path.join("rcsc", arquivo)):
            arquivo = os.path.join("rcsc", arquivo)

        if not os.path.exists(arquivo):
            continue
            
        totais_diarios = extrair_totais_diarios(arquivo, mapa_codigos, dados_tbca)
        if totais_diarios:
            dados_comparativos[nome_modelo] = totais_diarios
            dados_individuais = {"Individual": totais_diarios}
            
            # Gráficos individuais
            gerar_grafico_relativo(dados_individuais, metas_paciente, MACROS, f"{nome_modelo}_macros_relativo.png")
            gerar_grafico_relativo(dados_individuais, metas_paciente, MICROS, f"{nome_modelo}_micros_relativo.png")

    # 4. Gráficos Comparativos
    if len(dados_comparativos) > 1:
        print("\nGerando Gráficos Comparativos...")
        gerar_grafico_relativo(dados_comparativos, metas_paciente, MACROS, "comparativo_macros_relativo.png")
        gerar_grafico_relativo(dados_comparativos, metas_paciente, MICROS, "comparativo_micros_relativo.png")

if __name__ == "__main__":
    executar()