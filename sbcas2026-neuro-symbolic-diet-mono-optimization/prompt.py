def calcular_tmb(sexo, peso, altura, idade):
    # Fórmula: Equação de Mifflin-St Jeor
    if sexo.lower() == 'masculino':
        return (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    elif sexo.lower() in ['feminino', 'feminina']:
        return (10 * peso) + (6.25 * altura) - (5 * idade) - 161
    else:
        raise ValueError("Sexo deve ser 'Masculino' ou 'Feminino'.")

def calcular_get(tmb, nivel_atividade):
    fatores = {
        "Sedentário": 1.2,
        "Levemente ativo": 1.375,
        "Moderadamente ativo": 1.55,
        "Muito ativo": 1.725,
        "Extremamente ativo": 1.9
    }
    fator = fatores.get(nivel_atividade, 1.2)
    return round(tmb * fator)

def gerar_prompt_dieta(
    sexo="Feminino",
    idade=30,
    peso=73.0,
    altura=165,
    nivel_atividade="Levemente ativo",
    tmb=None,
    get=None,
    tem_deficit="NÃO",
    qtd_deficit=0
):
    origem_calculo = "Valores fornecidos pelo usuário"

    # Calcula TMB e GET caso não sejam fornecidos
    if tmb is None:
        tmb = round(calcular_tmb(sexo, peso, altura, idade))
        origem_calculo = "Calculado via Equação de Mifflin-St Jeor"
        
    if get is None:
        get = calcular_get(tmb, nivel_atividade)
        origem_calculo = "Calculado via Equação de Mifflin-St Jeor e Fator de Atividade"

    prompt = f"""Atue como um gerador de dados nutricionais para modelagem computacional. Sua tarefa é criar um cardápio teórico de 5 dias, distribuído em 6 refeições diárias, utilizando alimentos comuns na dieta brasileira.

Parâmetros do Perfil Alvo:
* Sexo: {sexo}
* Idade: {idade} anos
* Peso: {peso} kg
* Altura: {altura} cm
* Nível de Atividade Física: {nivel_atividade}
* TMB (Taxa Metabólica Basal) estimada: {tmb} kcal
* GET (Gasto Energético Total) estimado: {get} kcal
* Origem dos Cálculos (TMB/GET): {origem_calculo}
* Presença de Déficit Calórico: {tem_deficit}
* Quantidade do Déficit: {qtd_deficit} kcal

Regras de Geração:
1. A soma calórica diária dos alimentos gerados deve corresponder ao GET subtraído do Déficit Calórico informado.
2. Utilize ingredientes do padrão alimentar brasileiro em gramas ou mililitros.
3. A resposta deve conter exclusivamente o código JSON. 
4. Não inclua saudações, explicações, observações ou formatação markdown ao redor do código. Retorne apenas o objeto JSON puro e validável.

Formato de Saída Obrigatório:
{{
    "1": {
      "Café da Manhã": [
        { "alimento": "Pão Integral", "quantidade": "50" },
        { "alimento": "Queijo Minas Frescal", "quantidade": "30" },
        { "alimento": "Suco de Laranja Natural", "quantidade": "200" }
      ],
      "Lanche da Manhã": [
        { "alimento": "Mamão Papaia", "quantidade": "120" },
        { "alimento": "Granola sem açúcar", "quantidade": "20" }
      ],
      "Almoço": [
        { "alimento": "Arroz Branco Cozido", "quantidade": "100" },
        { "alimento": "Feijão Carioca Cozido", "quantidade": "80" },
        { "alimento": "Carne Moída Magra Cozida", "quantidade": "100" },
        { "alimento": "Abobrinha Refogada", "quantidade": "100" },
        { "alimento": "Salada de Folhas Verdes", "quantidade": "150" }
      ],
      "Lanche da Tarde": [
        { "alimento": "Iogurte Natural Desnatado", "quantidade": "170" },
        { "alimento": "Maçã", "quantidade": "130" }
      ],
      "Jantar": [
        { "alimento": "Purê de Mandioca", "quantidade": "150" },
        { "alimento": "Peito de Frango Desfiado", "quantidade": "100" },
        { "alimento": "Salada de Beterraba e Pepino", "quantidade": "150" }
      ],
      "Ceia": [
        { "alimento": "Leite Desnatado", "quantidade": "200" },
        { "alimento": "Aveia em Flocos", "quantidade": "20" }
      ]
    },
    "2": { ... },
    "3": { ... },
    "4": { ... },
    "5": { ... }
}}"""
    
    return prompt

# Perfil 1
prompt_p1 = gerar_prompt_dieta(tmb=1500, get=2100)
print(prompt_p1 + "...\n") 

# Teste 2: Deixando a função calcular automaticamente
prompt = gerar_prompt_dieta(
    sexo="Masculino",
    idade=28,
    peso=72.0,
    altura=175,
    nivel_atividade="Moderadamente ativo"
)
print("--- Teste Automático ---")
print(prompt + "...")