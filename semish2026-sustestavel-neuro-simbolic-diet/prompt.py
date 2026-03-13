def calcular_tmb(sexo, peso, altura, idade):
    if sexo.lower() == "masculino":
        return (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    elif sexo.lower() in ["feminino", "feminina"]:
        return (10 * peso) + (6.25 * altura) - (5 * idade) - 161
    else:
        raise ValueError("Sexo deve ser 'Masculino' ou 'Feminino'.")


def calcular_get(tmb, nivel_atividade):
    fatores = {
        "Sedentário": 1.2,
        "Levemente ativo": 1.375,
        "Moderadamente ativo": 1.55,
        "Muito ativo": 1.725,
        "Extremamente ativo": 1.9,
    }
    return round(tmb * fatores.get(nivel_atividade, 1.2))


def gerar_prompt_dieta(
    sexo="Feminino",
    idade=30,
    peso=73.0,
    altura=165,
    nivel_atividade="Levemente ativo",
    tmb=None,
    get=None,
    qtd_deficit=0,
    tipo_dieta="Vegetariana",
):
    if tmb is None:
        tmb = round(calcular_tmb(sexo, peso, altura, idade))
    if get is None:
        get = calcular_get(tmb, nivel_atividade)

    if qtd_deficit > 0:
        meta_calorica = get - qtd_deficit
        objetivo_dieta = "Emagrecimento (Déficit Calórico)"
    else:
        meta_calorica = get
        objetivo_dieta = "Manutenção (Isocalórica)"

    regra_restricao = ""
    if tipo_dieta.lower() == "vegana":
        regra_restricao = "DIETA VEGANA: Proibido ingredientes de origem animal (carnes, peixes, ovos, laticínios, mel). Use apenas fontes vegetais presentes no arquivo."
    elif tipo_dieta.lower() == "vegetariana":
        regra_restricao = "DIETA VEGETARIANA: Proibido qualquer tipo de carne (bovina, suína, frango, peixes). Ovos e laticínios são permitidos, desde que constem no arquivo."
    else:
        regra_restricao = "DIETA REGULAR: Não há restrições de grupos alimentares. Utilize qualquer combinação de alimentos (carnes, vegetais, grãos, laticínios), desde que constem EXATAMENTE no arquivo anexo."

    prompt = f"""Atue como um nutricionista clínico especialista em modelagem computacional.
Sua tarefa é criar um cardápio teórico de 5 dias, distribuído em 6 refeições diárias.

**Parâmetros do Perfil Alvo:**
* Sexo: {sexo}
* Idade: {idade} anos
* Peso: {peso} kg
* Altura: {altura} cm
* Nível de Atividade Física: {nivel_atividade}
* TMB Estimada: {tmb} kcal
* GET Estimado: {get} kcal
* Objetivo: {objetivo_dieta} (Meta Diária: {meta_calorica} kcal)
* Tipo de Dieta: {tipo_dieta.upper()}

**REGRA DE OURO (Restrição de Banco de Dados):**
É ESTRITAMENTE PROIBIDO inventar alimentos ou usar nomes genéricos. Você deve utilizar APENAS os alimentos presentes no arquivo de texto enviado em anexo. O campo "alimento" do JSON deve conter o nome do alimento por extenso, copiado EXATAMENTE como aparece no arquivo anexo.

**Cadeia de Pensamentos (Resumo da Estratégia):**
1. Valide a meta calórica e a restrição da dieta ({tipo_dieta.upper()}).
2. {regra_restricao}
3. Consulte o ARQUIVO ANEXO e selecione exclusivamente os itens permitidos para esta dieta.
4. Estruture o plano final validando as calorias totais baseadas nas quantidades.

**Regras de Saída:**
* O formato de saída deve ser EXCLUSIVAMENTE código JSON validável. Não inclua texto markdown (como ```json) ou introduções.
* O exemplo abaixo utiliza itens reais do seu arquivo anexo apenas para demonstrar a estrutura de chaves exigida. Adapte os alimentos do exemplo para a dieta {tipo_dieta.upper()} se for necessário.
* A quantidade dos alimentos representa a quantidade, em gramas, que deve ser consumida.
* Varie as recomendações. Tente não fazer uma mesma recomendação semanal já realizada.

**Exemplo de Formato Estrutural:**
{{
    "1": {{
      "Café da Manhã": [
        {{ "alimento": "Pão francês, trigo, branco, de padaria (médias de diferentes amostras)", "quantidade": "50" }},
        {{ "alimento": "Queijo, minas, frescal, light", "quantidade": "30" }},
        {{ "alimento": "Suco, laranja, s/ açúcar", "quantidade": "200" }}
      ],
      "Lanche da Manhã": [
        {{ "alimento": "Mamão, Papaia, polpa, in natura", "quantidade": "120" }},
        {{ "alimento": "Aveia, crua (média de diferentes tipos)", "quantidade": "20" }}
      ],
      "Almoço": [
        {{ "alimento": "Arroz, polido, cozido, c/ óleo, cebola e alho, c/ sal", "quantidade": "100" }},
        {{ "alimento": "Feijão, carioca, cozido (50% grão e 50% caldo), c/ óleo, cebola e alho, c/ sal", "quantidade": "80" }},
        {{ "alimento": "Carne, boi, patinho, s/ gordura, grelhada/assada, s/ óleo, c/ sal", "quantidade": "100" }},
        {{ "alimento": "Alface, crua", "quantidade": "50" }},
        {{ "alimento": "Tomate, in natura", "quantidade": "50" }}
      ],
      "Lanche da Tarde": [
        {{ "alimento": "Iogurte, natural, desnatado", "quantidade": "170" }},
        {{ "alimento": "Maçã, c/ casca, in natura", "quantidade": "130" }}
      ],
      "Jantar": [
        {{ "alimento": "Macarrão, trigo, cozido, drenado, s/ óleo, c/ sal", "quantidade": "100" }},
        {{ "alimento": "Carne, frango, peito, s/ pele, grelhada, s/ gordura, s/ óleo, c/ sal", "quantidade": "100" }},
        {{ "alimento": "Cenoura, s/ casca, cozida, drenada, s/ óleo, c/ sal", "quantidade": "80" }}
      ],
      "Ceia": [
        {{ "alimento": "Leite, vaca, desnatado, fluído (média de diferentes amostras)", "quantidade": "200" }}
      ]
    }}
}}"""

    return prompt


# Teste de Geração
# vegana
# vegetariana
# regular

prompt_teste = gerar_prompt_dieta(tipo_dieta="regular", qtd_deficit=0)

print(prompt_teste)
