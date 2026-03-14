import json
import random
import os
import copy
from collections import defaultdict

# ==========================================
# CONFIGURAÇÕES E METAS NUTRICIONAIS
# ==========================================
FATOR_DIVISAO_TBCA = 100.0
FATOR_DIVISAO_PEGADA = 1000.0

METAS_MAX = {
    "Energia": {"meta": 2200.0, "tolerancia": 1.05},
    "Sódio": {"meta": 2300.0, "tolerancia": 1.00},
    "Colesterol": {"meta": 300.0, "tolerancia": 1.00},
}

METAS_MIN = {
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
}

PESO_FALTA_BASE = 50.0
PESO_EXCESSO_LEVE = 0.5
PESO_PEGADA = 0.5
PENALIDADE_BIG_M = 10000.0

ORDEM_REFEICOES = [
    "Café da Manhã",
    "Lanche da Manhã",
    "Almoço",
    "Lanche da Tarde",
    "Jantar",
    "Ceia",
]


def carregar_json(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


# ==========================================
# CÁLCULOS NUTRICIONAIS E AMBIENTAIS
# ==========================================
def calcular_macros_pegadas(itens, mapa_tbca, tbca_completo, mapa_pegadas):
    nutrientes = defaultdict(float)
    pegadas = {
        "carbon_footprint": 0.0,
        "water_footprint": 0.0,
        "ecological_footprint": 0.0,
    }

    for item in itens:
        alimento = item.get("alimento")
        qtd = float(str(item.get("quantidade", "0")).replace(",", "."))

        cod = mapa_tbca.get(alimento)
        if cod and cod in tbca_completo:
            fator_n = qtd / FATOR_DIVISAO_TBCA
            for n, v in tbca_completo[cod].get("nutrientes", {}).items():
                nutrientes[n] += float(v) * fator_n

        if alimento in mapa_pegadas:
            fator_p = qtd / FATOR_DIVISAO_PEGADA
            peg = mapa_pegadas[alimento]
            pegadas["carbon_footprint"] += (
                float(peg.get("carbon_footprint", 0)) * fator_p
            )
            pegadas["water_footprint"] += float(peg.get("water_footprint", 0)) * fator_p
            pegadas["ecological_footprint"] += (
                float(peg.get("ecological_footprint", 0)) * fator_p
            )

    return dict(nutrientes), pegadas


# ==========================================
# FUNÇÃO DE FITNESS (COM PENALIDADE DINÂMICA)
# ==========================================
def calcular_fitness(cromossomo, geracao):
    diario = defaultdict(float)
    pegada_diaria = defaultdict(float)

    for refeicao in cromossomo:
        for n, v in refeicao["nutrientes"].items():
            diario[n] += v / 5.0
        for p, v in refeicao["pegadas"].items():
            pegada_diaria[p] += v / 5.0

    penalidade_total = 0.0

    # Fator Dinâmico: A pressão aumenta 1% a cada geração para forçar a convergência
    fator_dinamico = 1.0 + (0.01 * geracao)
    peso_falta_atual = PESO_FALTA_BASE * fator_dinamico

    # 1. Conjunto K_max (Limites Superiores Intoleráveis)
    for nutriente, regras in METAS_MAX.items():
        valor = diario.get(nutriente, 0)
        limite_teto = regras["meta"] * regras["tolerancia"]

        if valor > limite_teto:
            penalidade_total += (
                PENALIDADE_BIG_M
                + peso_falta_atual * ((valor - limite_teto) / regras["meta"]) ** 2
            )

        if nutriente == "Energia" and valor < regras["meta"]:
            penalidade_total += (
                peso_falta_atual * ((regras["meta"] - valor) / regras["meta"]) ** 2
            )

    # 2. Conjunto K_min (Metas Mínimas de Saúde)
    for nutriente, meta in METAS_MIN.items():
        valor = diario.get(nutriente, 0)
        if valor < meta:
            penalidade_total += peso_falta_atual * ((meta - valor) / meta) ** 2
        else:
            penalidade_total += PESO_EXCESSO_LEVE * ((valor - meta) / meta) ** 2

    # 3. Minimização Ambiental
    p_carbono = pegada_diaria["carbon_footprint"] / 2000.0
    p_agua = pegada_diaria["water_footprint"] / 1500.0
    p_eco = pegada_diaria["ecological_footprint"] / 10.0

    penalidade_total += PESO_PEGADA * (p_carbono + p_agua + p_eco)

    return 1.0 / (1.0 + penalidade_total)


# ==========================================
# ALGORITMO GENÉTICO (ESTADO DA ARTE)
# ==========================================
def otimizar_dieta(pool_refeicoes, pool_alimentos, pop_size=150):
    populacao = []

    # População Inicial
    for _ in range(pop_size):
        individuo = []
        for _ in range(5):
            for tipo_ref in ORDEM_REFEICOES:
                individuo.append(copy.deepcopy(random.choice(pool_refeicoes[tipo_ref])))
        populacao.append(individuo)

    geracao = 0
    melhor_fitness_global = -1.0
    contador_estagnacao = 0

    # Parâmetros de Parada e Adaptação
    TOLERANCIA_PLATO = 1e-6
    MAX_ESTAGNACAO = 40  # Para após 40 gerações sem melhoria
    LIMIAR_HIPERMUTACAO = 15  # Ativa hipermutação após 15 gerações estagnado

    while True:
        # Avaliação com penalidade dinâmica
        fitnesses = [calcular_fitness(ind, geracao) for ind in populacao]
        pop_avaliada = list(zip(populacao, fitnesses))
        pop_avaliada.sort(key=lambda x: x[1], reverse=True)

        melhor_fitness_atual = pop_avaliada[0][1]

        # Verificação de Platô
        if (melhor_fitness_atual - melhor_fitness_global) < TOLERANCIA_PLATO:
            contador_estagnacao += 1
        else:
            melhor_fitness_global = melhor_fitness_atual
            contador_estagnacao = 0

        # Log simplificado para monitoramento do platô
        print(
            f"Ger: {geracao:03d} | Fit: {melhor_fitness_atual:.6f} | Platô: {contador_estagnacao}/{MAX_ESTAGNACAO}",
            end="\r",
        )

        # Condição de Parada
        if contador_estagnacao >= MAX_ESTAGNACAO:
            print(f"\n[!] Convergência atingida na geração {geracao}. Platô detectado.")
            break

        # Taxas Adaptativas de Mutação (Hipermutação se preso no platô)
        if contador_estagnacao >= LIMIAR_HIPERMUTACAO:
            taxa_mut_global = 0.15  # 3x maior
            taxa_mut_local = 0.30  # 2x maior
        else:
            taxa_mut_global = 0.05
            taxa_mut_local = 0.15

        nova_populacao = []
        # Elitismo (Top 5% sempre passam direto e são re-avaliados na próx geração)
        elite_size = int(pop_size * 0.05)
        nova_populacao.extend(
            [copy.deepcopy(ind) for ind, fit in pop_avaliada[:elite_size]]
        )

        while len(nova_populacao) < pop_size:
            # Torneio
            torneio1 = random.sample(pop_avaliada, 3)
            pai1 = max(torneio1, key=lambda x: x[1])[0]
            torneio2 = random.sample(pop_avaliada, 3)
            pai2 = max(torneio2, key=lambda x: x[1])[0]

            # Crossover Uniforme
            filho = []
            for i in range(len(pai1)):
                if random.random() > 0.5:
                    filho.append(copy.deepcopy(pai1[i]))
                else:
                    filho.append(copy.deepcopy(pai2[i]))

            # Mutações
            for i in range(len(filho)):
                tipo_ref = ORDEM_REFEICOES[i % 6]
                prob = random.random()

                # Mutação 1 (Global): Substitui a refeição inteira
                if prob < taxa_mut_global:
                    filho[i] = copy.deepcopy(random.choice(pool_refeicoes[tipo_ref]))

                # Mutação 2 (Local): Substitui apenas um alimento
                elif prob < (taxa_mut_global + taxa_mut_local):
                    itens = filho[i]["itens"]
                    if len(itens) > 0:
                        idx = random.randint(0, len(itens) - 1)
                        novo_alimento = copy.deepcopy(
                            random.choice(pool_alimentos[tipo_ref])
                        )
                        itens[idx] = novo_alimento

                        nutris, pegadas = calcular_macros_pegadas(
                            itens,
                            mapa_tbca_global,
                            tbca_completo_global,
                            mapa_pegadas_global,
                        )
                        filho[i]["nutrientes"] = nutris
                        filho[i]["pegadas"] = pegadas

            nova_populacao.append(filho)

        populacao = nova_populacao
        geracao += 1

    return pop_avaliada[0][0]  # Retorna o melhor cromossomo do último rank


# ==========================================
# VARIÁVEIS GLOBAIS
# ==========================================
mapa_tbca_global = {}
tbca_completo_global = {}
mapa_pegadas_global = {}


# ==========================================
# PIPELINE PRINCIPAL
# ==========================================
def executar_otimizacao_arquivos(
    arquivos_dietas, arq_mapa_tbca, arq_tbca_completo, arq_mapa_pegadas
):
    global mapa_tbca_global, tbca_completo_global, mapa_pegadas_global

    mapa_tbca_global = carregar_json(arq_mapa_tbca)
    tbca_completo_global = carregar_json(arq_tbca_completo)
    mapa_pegadas_global = carregar_json(arq_mapa_pegadas)

    for arquivo_dieta in arquivos_dietas:
        if not os.path.exists(arquivo_dieta):
            continue
        print(f"\n{'='*50}\n🧬 Otimizando: {arquivo_dieta}\n{'='*50}")

        dietas = carregar_json(arquivo_dieta)

        pool_refeicoes = {tipo: [] for tipo in ORDEM_REFEICOES}
        pool_alimentos = {tipo: [] for tipo in ORDEM_REFEICOES}

        for plano in dietas:
            for dia, refeicoes in plano.items():
                if not isinstance(refeicoes, dict):
                    continue
                for nome_refeicao, itens in refeicoes.items():
                    if (
                        nome_refeicao in ORDEM_REFEICOES
                        and isinstance(itens, list)
                        and itens
                    ):
                        nutris, pegadas = calcular_macros_pegadas(
                            itens,
                            mapa_tbca_global,
                            tbca_completo_global,
                            mapa_pegadas_global,
                        )
                        pool_refeicoes[nome_refeicao].append(
                            {
                                "itens": copy.deepcopy(itens),
                                "nutrientes": nutris,
                                "pegadas": pegadas,
                            }
                        )
                        for item in itens:
                            if item not in pool_alimentos[nome_refeicao]:
                                pool_alimentos[nome_refeicao].append(
                                    copy.deepcopy(item)
                                )

        # Algoritmo Base
        melhor_cromossomo = otimizar_dieta(pool_refeicoes, pool_alimentos)

        # Reconstrução
        dieta_otimizada = {"1": {}}
        for dia_idx in range(5):
            dia_chave = str(dia_idx + 1)
            dieta_otimizada[dia_chave] = {}
            for ref_idx, tipo_ref in enumerate(ORDEM_REFEICOES):
                idx_linear = (dia_idx * 6) + ref_idx
                dieta_otimizada[dia_chave][tipo_ref] = melhor_cromossomo[idx_linear][
                    "itens"
                ]

        nome_saida = f"otimizada-{os.path.basename(arquivo_dieta)}"
        with open(nome_saida, "w", encoding="utf-8") as f_out:
            json.dump([dieta_otimizada], f_out, indent=4, ensure_ascii=False)

        print(f"✅ Arquivo salvo: {nome_saida}")


# ==========================================
# INÍCIO DA EXECUÇÃO
# ==========================================
arquivos_para_otimizar = [
    "dietas-regular.json",
    "dietas-vegetariana.json",
    "dietas-vegana.json",
]

executar_otimizacao_arquivos(
    arquivos_dietas=arquivos_para_otimizar,
    arq_mapa_tbca="mapa-sustentavel-tbca.json",
    arq_tbca_completo="mapa-tbca-completo.json",
    arq_mapa_pegadas="mapa-sustentavel-pegadas.json",
)
