import json
import statistics
import os
from collections import defaultdict

# ==========================================
# CONFIGURAÇÕES E ESCALAS
# ==========================================
FATOR_DIVISAO_TBCA = 100.0
FATOR_DIVISAO_PEGADA = 100.0


def carregar_json(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {caminho}: {e}")
        return None


# ==========================================
# 1. ESTATÍSTICAS DE COMPORTAMENTO
# ==========================================
def calcular_estatisticas_comportamento(dietas):
    """
    Calcula os dias únicos e a verificação cultural exata como no script original.
    """
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
                assinatura_refeicao = (
                    nome_refeicao.strip().lower(),
                    tuple(sorted(alimentos)),
                )
                assinatura_dia.append(assinatura_refeicao)

                nome_ref_lower = nome_refeicao.strip().lower()
                if nome_ref_lower == "almoço" or nome_ref_lower == "almoco":
                    total_almocos += 1
                    tem_arroz = any("arroz" in al for al in alimentos)
                    tem_feijao = any(
                        "feijão" in al or "feijao" in al for al in alimentos
                    )
                    if tem_arroz and tem_feijao:
                        almocos_com_arroz_feijao += 1

            assinaturas_dias.add(tuple(assinatura_dia))

    taxa_arroz_feijao = (
        (almocos_com_arroz_feijao / total_almocos * 100) if total_almocos > 0 else 0
    )
    return len(assinaturas_dias), total_dias, taxa_arroz_feijao


# ==========================================
# 2. PROCESSAMENTO E EXPORTAÇÃO
# ==========================================
def processar_arquivos(
    arquivos_dietas, arq_mapa_tbca, arq_tbca_completo, arq_mapa_pegadas
):
    mapa_sustentavel_tbca = carregar_json(arq_mapa_tbca)
    tbca_completo = carregar_json(arq_tbca_completo)
    mapa_pegadas = carregar_json(arq_mapa_pegadas)

    if not all([mapa_sustentavel_tbca, tbca_completo, mapa_pegadas]):
        print("Erro crítico: Falha ao carregar os mapas de referência.")
        return

    for arquivo_dieta in arquivos_dietas:
        if not os.path.exists(arquivo_dieta):
            print(f"Aviso: Arquivo {arquivo_dieta} não encontrado.")
            continue

        dietas = carregar_json(arquivo_dieta)
        if not dietas:
            continue

        # Cria o nome do arquivo de saída igual ao original (ex: dietas-vegana_estatisticas.txt)
        base_nome = os.path.splitext(arquivo_dieta)[0]
        arquivo_saida_txt = f"{base_nome}-estatisticas.txt"

        totais_diarios = defaultdict(lambda: defaultdict(list))
        totais_refeicao = defaultdict(lambda: defaultdict(list))
        itens_sem_tbca = set()
        itens_sem_pegada = set()

        qtd_dias_unicos, total_dias, taxa_arroz_feijao = (
            calcular_estatisticas_comportamento(dietas)
        )

        # Agrupamento e acumulação dos dados
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
                        qtd_texto = str(item.get("quantidade", "0")).replace(",", ".")
                        qtd = float(qtd_texto)

                        # 1. TBCA
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

                        # 2. Pegadas Ambientais
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

                    # Salva os totais no dicionário da Refeição
                    for n, v in nutrientes_ref.items():
                        totais_refeicao[nome_refeicao][n].append(v)
                        nutrientes_do_dia[n] += v

                # Salva os totais no dicionário do Dia (Geral)
                for n, v in nutrientes_do_dia.items():
                    totais_diarios["Geral"][n].append(v)

        # ==========================================
        # GERAÇÃO DO ARQUIVO DE TEXTO
        # ==========================================
        with open(arquivo_saida_txt, "w", encoding="utf-8") as f_out:

            def log(msg):
                print(msg)  # Imprime no terminal
                f_out.write(msg + "\n")  # Salva no TXT

            # Cabeçalho Original
            log(f"--- Relatório Individual: {arquivo_dieta} ---")
            log("========================================")
            log("ESTATÍSTICAS DO MODELO (COMPORTAMENTO)")
            log(f"Total de dias simulados: {total_dias}")
            log(f"Dietas (dias) efetivamente únicas geradas: {qtd_dias_unicos}")
            if total_dias > 0:
                log(
                    f"Taxa de originalidade (variedade): {(qtd_dias_unicos/total_dias*100):.1f}%"
                )
            else:
                log("Taxa de originalidade (variedade): 0.0%")
            log(
                f"Taxa de presença de Arroz e Feijão no Almoço: {taxa_arroz_feijao:.1f}%"
            )
            log("========================================\n")

            # Função de formatação interna fiel ao código fornecido
            def formatar_saida(titulo, dados_dict):
                log(f"\n>> {titulo}")

                # Força que Energia e as Pegadas Ambientais apareçam primeiro no bloco
                nutrientes_foco = [
                    "Energia",
                    "Pegada de Carbono",
                    "Pegada Hídrica",
                    "Pegada Ecológica",
                    "Carboidrato disponível",
                    "Carboidrato total",
                    "Proteína",
                    "Lipídios",
                    "Fibra alimentar",
                    "Sódio",
                ]

                # Garante a ordem correta das refeições
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

                        if media > 0.1:  # Filtro original do seu script
                            un = "g"
                            if nutri == "Energia":
                                un = "kcal"
                            elif nutri == "Sódio":
                                un = "mg"
                            elif "Pegada" in nutri:
                                un = ""  # Pegadas ficam com a unidade limpa no visual

                            # Formatação exata com pontos corridos
                            log(f"    {nutri:.<25} {media:>8.2f} ± {desvio:<6.2f} {un}")

            formatar_saida("MÉDIA DIÁRIA", totais_diarios)
            formatar_saida("MÉDIA POR REFEIÇÃO", totais_refeicao)

            # Relatório de Falhas de Mapeamento no final do TXT
            if itens_sem_tbca or itens_sem_pegada:
                log("\n========================================")
                log("ALIMENTOS NÃO MAPEADOS")
                log("========================================")
                if itens_sem_tbca:
                    log("\n--- Não encontrados no TBCA ---")
                    for i in sorted(itens_sem_tbca):
                        log(i)
                if itens_sem_pegada:
                    log("\n--- Não encontrados nas Pegadas ---")
                    for i in sorted(itens_sem_pegada):
                        log(i)

        print(f"\n💾 Relatório fiel gerado com sucesso: {arquivo_saida_txt}\n")


# ==========================================
# INÍCIO DA EXECUÇÃO
# ==========================================
arquivos_para_analisar = [
    "dietas-regular.json",
    "dietas-vegana.json",
    "dietas-vegetariana.json",
]

processar_arquivos(
    arquivos_dietas=arquivos_para_analisar,
    arq_mapa_tbca="mapa-sustentavel-tbca.json",
    arq_tbca_completo="mapa-tbca-completo.json",
    arq_mapa_pegadas="mapa-sustentavel-pegadas.json",
)
