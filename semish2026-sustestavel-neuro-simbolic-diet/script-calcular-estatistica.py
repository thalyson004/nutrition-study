import json
import statistics
import os
from collections import defaultdict
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURAÇÕES E METAS
# ==========================================
FATOR_DIVISAO_TBCA = 100.0
FATOR_DIVISAO_PEGADA = 1000.0

METAS_NUTRICIONAIS = {
    "Energia": 2200.0,
    "Carboidrato total": 302.5,
    "Proteína": 110.0,
    "Lipídios": 61.11,
    "Fibra alimentar": 25.0,
    "Vitamina A (RE)": 900.0,
    "Vitamina C": 90.0,
    "Vitamina D": 15.0,
    "Alfa-tocoferol (Vitamina E)": 15.0,
    "Tiamina": 1.2,
    "Riboflavina": 1.3,
    "Niacina": 16.0,
    "Vitamina B6": 1.3,
    "Vitamina B12": 2.4,
    "Cálcio": 1000.0,
    "Magnésio": 420.0,
    "Sódio": 2300.0,
}

MAPA_NOMES_GRAFICO = {
    "Carboidrato total": "Carboidrato",
    "Fibra alimentar": "Fibra",
    "Alfa-tocoferol (Vitamina E)": "Vit. E",
    "Vitamina A (RE)": "Vit. A",
    "Lipídios": "Lipídeos",
}

MACROS = ["Energia", "Carboidrato total", "Proteína", "Lipídios", "Fibra alimentar"]
MICROS = [
    "Vitamina A (RE)",
    "Vitamina C",
    "Vitamina D",
    "Alfa-tocoferol (Vitamina E)",
    "Tiamina",
    "Riboflavina",
    "Niacina",
    "Vitamina B6",
    "Vitamina B12",
    "Cálcio",
    "Magnésio",
    "Sódio",
]
PEGADAS = ["Pegada de Carbono", "Pegada Hídrica", "Pegada Ecológica"]

# A ORDEM EXATA EXIGIDA PARA OS GRÁFICOS
ORDEM_DIETAS = ["Regular", "Vegetariana", "Vegana"]


# ==========================================
# FUNÇÕES AUXILIARES E GRÁFICOS
# ==========================================
def carregar_json(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def calcular_estatisticas_comportamento(dietas):
    assinaturas_dias = set()
    total_dias = 0
    total_almocos = 0
    almocos_com_arroz_feijao = 0

    for plano in dietas:
        for dia, refeicoes in plano.items():
            if not isinstance(refeicoes, dict):
                continue
            total_dias += 1
            assinatura_dia = []

            for nome_refeicao, itens in refeicoes.items():
                if not isinstance(itens, list):
                    continue
                alimentos = [
                    str(item.get("alimento", "")).strip().lower()
                    for item in itens
                    if item.get("alimento")
                ]
                assinatura_dia.append(
                    (nome_refeicao.strip().lower(), tuple(sorted(alimentos)))
                )

                if nome_refeicao.strip().lower() in ["almoço", "almoco"]:
                    total_almocos += 1
                    if any("arroz" in al for al in alimentos) and any(
                        "feijão" in al or "feijao" in al for al in alimentos
                    ):
                        almocos_com_arroz_feijao += 1

            assinaturas_dias.add(tuple(assinatura_dia))

    taxa_arroz_feijao = (
        (almocos_com_arroz_feijao / total_almocos * 100) if total_almocos > 0 else 0
    )
    return len(assinaturas_dias), total_dias, taxa_arroz_feijao


def gerar_graficos_comparativos(dados_consolidados):
    print("\n📊 Gerando gráficos comparativos...")
    sns.set_theme(style="whitegrid")

    cores_dietas = {"Regular": "#4c72b0", "Vegetariana": "#dd8452", "Vegana": "#55a868"}

    # ==========================================
    # 1. MACROS (%)
    # ==========================================
    df_macro = pd.DataFrame(
        [
            {
                "Dieta": dieta,
                "Nutriente": MAPA_NOMES_GRAFICO.get(macro, macro),
                "Percentual (%)": (
                    nutris.get(macro, 0) / METAS_NUTRICIONAIS.get(macro, 1)
                )
                * 100,
            }
            for dieta, nutris in dados_consolidados.items()
            for macro in MACROS
        ]
    )
    plt.figure(figsize=(14, 7))

    # Adicionando borda preta (edgecolor)
    ax1 = sns.barplot(
        data=df_macro,
        x="Nutriente",
        y="Percentual (%)",
        hue="Dieta",
        palette=cores_dietas,
        hue_order=ORDEM_DIETAS,
        edgecolor="black",
        linewidth=1.5,
    )

    ax1.axhline(100, color="red", linestyle="--", linewidth=1.0, label="Meta (100%)")

    # Rótulos nas barras maiores e em negrito
    for container in ax1.containers:
        ax1.bar_label(
            container,
            fmt="%.1f",
            padding=3,
            fontsize=14,
            fontweight="bold",
            rotation=60,
        )

    ax1.set_ylabel("Percentual da Meta (%)", fontsize=18, fontweight="bold")
    ax1.set_xlabel("")
    plt.xticks(fontsize=16, fontweight="bold")
    plt.yticks(fontsize=16, fontweight="bold")
    plt.legend(
        bbox_to_anchor=(1.01, 1), loc="upper left", prop={"size": 16, "weight": "bold"}
    )
    plt.tight_layout()
    plt.savefig("comparativo_macronutrientes_pct.png", dpi=300)
    plt.close()

    # ==========================================
    # 2. MICROS (%)
    # ==========================================
    df_micro = pd.DataFrame(
        [
            {
                "Dieta": dieta,
                "Nutriente": MAPA_NOMES_GRAFICO.get(micro, micro),
                "Percentual (%)": (
                    nutris.get(micro, 0) / METAS_NUTRICIONAIS.get(micro, 1)
                )
                * 100,
            }
            for dieta, nutris in dados_consolidados.items()
            for micro in MICROS
        ]
    )
    plt.figure(figsize=(18, 8))

    ax2 = sns.barplot(
        data=df_micro,
        x="Nutriente",
        y="Percentual (%)",
        hue="Dieta",
        palette=cores_dietas,
        hue_order=ORDEM_DIETAS,
        edgecolor="black",
        linewidth=1.5,
    )

    ax2.axhline(100, color="red", linestyle="--", linewidth=1.0, label="Meta (100%)")

    for container in ax2.containers:
        ax2.bar_label(
            container,
            fmt="%.1f",
            padding=4,
            fontsize=14,
            fontweight="bold",
            rotation=60,
        )

    ax2.set_ylabel("Percentual da Meta (%)", fontsize=16, fontweight="bold")
    ax2.set_xlabel("")
    plt.xticks(rotation=45, ha="right", fontsize=18, fontweight="bold")
    plt.yticks(fontsize=16, fontweight="bold")
    ax2.set_ylim(0, ax2.get_ylim()[1] * 1.2)  # Margem maior para caber o texto girado
    plt.legend(
        bbox_to_anchor=(1.01, 1), loc="upper left", prop={"size": 16, "weight": "bold"}
    )
    plt.tight_layout()
    plt.savefig("comparativo_micronutrientes_pct.png", dpi=300)
    plt.close()

    # ==========================================
    # 3. PEGADAS AMBIENTAIS
    # ==========================================
    df_pegada = pd.DataFrame(
        [
            {"Dieta": dieta, "Pegada": pegada, "Valor": nutris.get(pegada, 0)}
            for dieta, nutris in dados_consolidados.items()
            for pegada in PEGADAS
        ]
    )
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))

    for i, pegada in enumerate(PEGADAS):
        ax3 = sns.barplot(
            data=df_pegada[df_pegada["Pegada"] == pegada],
            x="Dieta",
            y="Valor",
            hue="Dieta",
            ax=axes[i],
            palette=cores_dietas,
            order=ORDEM_DIETAS,
            hue_order=ORDEM_DIETAS,
            edgecolor="black",
            linewidth=1.5,
            legend=False,
        )

        for container in ax3.containers:
            ax3.bar_label(
                container, fmt="%.1f", padding=4, fontsize=14, fontweight="bold"
            )

        axes[i].set_title(
            pegada, fontsize=16, fontweight="bold"
        )  # Mantido para saber qual pegada é
        axes[i].set_xlabel("")
        axes[i].set_ylabel("Valor" if i == 0 else "", fontsize=16, fontweight="bold")

        # Negrito nos rótulos dos eixos
        for label in axes[i].get_xticklabels():
            label.set_fontweight("bold")
            label.set_fontsize(16)
        for label in axes[i].get_yticklabels():
            label.set_fontweight("bold")
            label.set_fontsize(16)

        axes[i].set_ylim(0, axes[i].get_ylim()[1] * 1.15)

    plt.tight_layout()
    plt.savefig("comparativo_pegadas_ambientais.png", dpi=300)
    plt.close()
    print("✅ Todos os Gráficos foram gerados e salvos!")


# ==========================================
# PROCESSAMENTO PRINCIPAL (TXT + DADOS)
# ==========================================
def processar_tudo(arquivos_dietas, arq_mapa_tbca, arq_tbca_completo, arq_mapa_pegadas):
    mapa_sustentavel_tbca = carregar_json(arq_mapa_tbca)
    tbca_completo = carregar_json(arq_tbca_completo)
    mapa_pegadas = carregar_json(arq_mapa_pegadas)

    if not all([mapa_sustentavel_tbca, tbca_completo, mapa_pegadas]):
        print("❌ Erro crítico: Falha ao carregar mapas de referência.")
        return

    dados_para_graficos = {}

    for arquivo_dieta in arquivos_dietas:
        if not os.path.exists(arquivo_dieta):
            print(
                f"⚠️ AVISO: O arquivo '{arquivo_dieta}' não foi encontrado. Pulando..."
            )
            continue

        dietas = carregar_json(arquivo_dieta)
        if not dietas:
            continue

        nome_dieta_limpo = (
            arquivo_dieta.replace("dietas-", "")
            .replace(".json", "")
            .replace("corrigido_", "")
            .title()
        )
        base_nome = os.path.splitext(arquivo_dieta)[0]
        arquivo_saida_txt = f"{base_nome}-estatisticas.txt"

        totais_diarios = defaultdict(lambda: defaultdict(list))
        totais_refeicao = defaultdict(lambda: defaultdict(list))
        itens_sem_tbca = set()
        itens_sem_pegada = set()

        qtd_dias_unicos, total_dias, taxa_arroz_feijao = (
            calcular_estatisticas_comportamento(dietas)
        )

        print(f"Processando dados de: {nome_dieta_limpo}...")

        for plano in dietas:
            for dia, refeicoes in plano.items():
                if not isinstance(refeicoes, dict):
                    continue
                nutrientes_do_dia = defaultdict(float)

                for nome_refeicao, itens in refeicoes.items():
                    if not isinstance(itens, list):
                        continue
                    nutrientes_ref = defaultdict(float)

                    for item in itens:
                        alimento = item.get("alimento")
                        qtd = float(str(item.get("quantidade", "0")).replace(",", "."))

                        cod = mapa_sustentavel_tbca.get(alimento)
                        if cod and cod in tbca_completo:
                            fator = qtd / FATOR_DIVISAO_TBCA
                            for n, v in (
                                tbca_completo[cod].get("nutrientes", {}).items()
                            ):
                                nutrientes_ref[n] += float(v) * fator
                        else:
                            if alimento:
                                itens_sem_tbca.add(alimento)

                        if alimento in mapa_pegadas:
                            fator_p = qtd / FATOR_DIVISAO_PEGADA
                            peg = mapa_pegadas[alimento]
                            nutrientes_ref["Pegada de Carbono"] += (
                                float(peg.get("carbon_footprint", 0)) * fator_p
                            )
                            nutrientes_ref["Pegada Hídrica"] += (
                                float(peg.get("water_footprint", 0)) * fator_p
                            )
                            nutrientes_ref["Pegada Ecológica"] += (
                                float(peg.get("ecological_footprint", 0)) * fator_p
                            )
                        else:
                            if alimento:
                                itens_sem_pegada.add(alimento)

                    for n, v in nutrientes_ref.items():
                        totais_refeicao[nome_refeicao][n].append(v)
                        nutrientes_do_dia[n] += v

                for n, v in nutrientes_do_dia.items():
                    totais_diarios["Geral"][n].append(v)

        with open(arquivo_saida_txt, "w", encoding="utf-8") as f_out:

            def log(msg):
                f_out.write(msg + "\n")

            log(f"--- Relatório Individual: {arquivo_dieta} ---")
            log("========================================")
            log("ESTATÍSTICAS DO MODELO (COMPORTAMENTO)")
            log(f"Total de dias simulados: {total_dias}")
            log(f"Dietas (dias) efetivamente únicas geradas: {qtd_dias_unicos}")
            log(
                f"Taxa de originalidade (variedade): {(qtd_dias_unicos/total_dias*100 if total_dias>0 else 0):.1f}%"
            )
            log(
                f"Taxa de presença de Arroz e Feijão no Almoço: {taxa_arroz_feijao:.1f}%"
            )
            log("========================================\n")

            def formatar_saida(titulo, dados_dict):
                log(f"\n>> {titulo}")
                nutrientes_foco = [
                    "Energia",
                    "Pegada de Carbono",
                    "Pegada Hídrica",
                    "Pegada Ecológica",
                    "Carboidrato total",
                    "Proteína",
                    "Lipídios",
                    "Fibra alimentar",
                    "Sódio",
                ]
                ordem_ref = [
                    "Geral",
                    "Café da Manhã",
                    "Lanche da Manhã",
                    "Almoço",
                    "Lanche da Tarde",
                    "Jantar",
                    "Ceia",
                ]
                categorias = [o for o in ordem_ref if o in dados_dict]
                for c in dados_dict.keys():
                    if c not in categorias:
                        categorias.append(c)

                for categoria in categorias:
                    nutris_map = dados_dict[categoria]
                    log(f"   [{categoria.upper()}]")
                    todos = set(nutris_map.keys())
                    chaves = [k for k in nutrientes_foco if k in todos] + sorted(
                        list(todos - set(nutrientes_foco))
                    )

                    for nutri in chaves:
                        vals = nutris_map[nutri]
                        if not vals:
                            continue
                        media = statistics.mean(vals)
                        desvio = statistics.stdev(vals) if len(vals) > 1 else 0.0
                        if media > 0.1:
                            un = "g"
                            if nutri == "Energia":
                                un = "kcal"
                            elif nutri == "Sódio":
                                un = "mg"
                            elif "Pegada" in nutri:
                                un = ""
                            log(f"    {nutri:.<25} {media:>8.2f} ± {desvio:<6.2f} {un}")

            formatar_saida("MÉDIA DIÁRIA", totais_diarios)
            formatar_saida("MÉDIA POR REFEIÇÃO", totais_refeicao)

            if itens_sem_tbca or itens_sem_pegada:
                log("\n========================================")
                log("ALIMENTOS NÃO MAPEADOS")
                log("========================================")
                if itens_sem_tbca:
                    log("\n--- Não encontrados no TBCA ---")
                    [log(i) for i in sorted(itens_sem_tbca)]
                if itens_sem_pegada:
                    log("\n--- Não encontrados nas Pegadas ---")
                    [log(i) for i in sorted(itens_sem_pegada)]

        print(f"📄 Arquivo de texto gerado: {arquivo_saida_txt}")

        medias_dessa_dieta = {
            n: statistics.mean(vals)
            for n, vals in totais_diarios["Geral"].items()
            if vals
        }
        dados_para_graficos[nome_dieta_limpo] = medias_dessa_dieta

    if dados_para_graficos:
        gerar_graficos_comparativos(dados_para_graficos)


# ==========================================
# EXECUÇÃO DO SCRIPT
# ==========================================
arquivos_para_analisar = [
    "dietas-regular.json",
    "dietas-vegetariana.json",
    "dietas-vegana.json",
    #     "otimizada-dietas-regular.json",
    #     "otimizada-dietas-vegetariana.json",
    #     "otimizada-dietas-vegana.json",
]

processar_tudo(
    arquivos_dietas=arquivos_para_analisar,
    arq_mapa_tbca="mapa-sustentavel-tbca.json",
    arq_tbca_completo="mapa-tbca-completo.json",
    arq_mapa_pegadas="mapa-sustentavel-pegadas.json",
)
