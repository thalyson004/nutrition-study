from dataclasses import asdict, dataclass, field
import json
import pickle
import difflib


@dataclass
class TbcaUnit:
    codigo: str
    nome: str
    grupo: str
    link: str

    nutrientes: dict = field(default_factory=dict)


caminho_pickle = "mapa-tbca-completo.pkl"
dados_tbca = None
with open(caminho_pickle, "rb") as f:
    dados_tbca = pickle.load(f)

dados_tbca = {chave: asdict(valor) for chave, valor in dados_tbca.items()}


with open("mapa-tbca-completo.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados_tbca, arquivo, indent=4, ensure_ascii=False)


mapa_nome_codigo = {valor["nome"]: chave for chave, valor in dados_tbca.items()}

with open("mapa-nome-codigo.json", "w", encoding="utf-8") as arquivo:
    json.dump(mapa_nome_codigo, arquivo, indent=4, ensure_ascii=False)


## SALVO


def limpar_texto(texto):
    """
    Remove vírgulas e coloca em minúsculo para melhorar a precisão da comparação.
    "Arroz, polido" vira "arroz polido"
    """
    return texto.lower().replace(",", "").strip()


def encontrar_chaves_por_similaridade(
    arquivo_a, arquivo_b, arquivo_saida="relacao_chaves.json"
):
    try:
        with open(arquivo_a, "r", encoding="utf-8") as f1:
            mapa_a = json.load(f1)

        with open(arquivo_b, "r", encoding="utf-8") as f2:
            mapa_b = json.load(f2)

        matches_encontrados = []
        chaves_sem_match = []

        # Dicionário que será salvo no JSON final
        dicionario_final = {}

        cur = 1
        total_chaves = len(mapa_a.keys())

        for chave_a in mapa_a.keys():
            print(
                f"Processando {cur} / {total_chaves}", end="\r"
            )  # end="\r" faz o print atualizar na mesma linha
            cur += 1

            texto_a_limpo = limpar_texto(chave_a)
            melhor_match = None
            maior_score = 0

            # Compara a chave A com todas as chaves B para achar a mais parecida
            for chave_b in mapa_b.keys():
                texto_b_limpo = limpar_texto(chave_b)

                # Calcula a similaridade entre as duas frases
                score = difflib.SequenceMatcher(
                    None, texto_a_limpo, texto_b_limpo
                ).ratio()

                # Se for o maior score até agora, salva ele
                if score > maior_score:
                    maior_score = score
                    melhor_match = chave_b

            matches_encontrados.append((chave_a, melhor_match, maior_score))

            dicionario_final[chave_a] = melhor_match
        print("\n")  # Quebra a linha após o contador terminar

        # ==========================================
        # SALVANDO O ARQUIVO JSON
        # ==========================================
        with open(arquivo_saida, "w", encoding="utf-8") as f_out:
            json.dump(dicionario_final, f_out, indent=4, ensure_ascii=False)

        print(f"💾 Arquivo de mapeamento salvo com sucesso em: '{arquivo_saida}'\n")

        return matches_encontrados

    except Exception as e:
        print(f"Erro ao processar os arquivos: {e}")


# ==========================================
# EXECUÇÃO DO SCRIPT
# ==========================================
# Agora você passa o nome do arquivo que deseja gerar como terceiro parâmetro
# encontrar_chaves_por_similaridade(
#     "mapa-nome-sustentavel.json",
#     "mapa-nome-codigo.json",
#     "mapa-de-para.json",  # O arquivo final será criado com esse nome
# )
