import json


def converter_txt_para_json(arquivo_txt, arquivo_json):
    mapa_alimentos = {}

    try:
        # Abre o arquivo de texto para leitura
        with open(arquivo_txt, "r", encoding="utf-8") as f_in:
            linhas = f_in.readlines()

            for linha in linhas:
                linha = linha.strip()

                # Ignora linhas vazias
                if not linha:
                    continue

                # O pulo do gato: rsplit(maxsplit=3)
                # Ele separa a linha pelos espaços, mas de trás pra frente, no máximo 3 vezes.
                # Isso garante que o nome do alimento (mesmo cheio de espaços e vírgulas) fique inteiro na posição 0.
                partes = linha.rsplit(maxsplit=3)

                if len(partes) == 4:
                    nome = partes[0].strip()

                    try:
                        # Substitui a vírgula por ponto (ex: "0,4" -> "0.4") para o Python converter para float
                        carbon = float(partes[1].replace(",", "."))
                        water = float(partes[2].replace(",", "."))
                        eco = float(partes[3].replace(",", "."))

                        # Salva no dicionário.
                        # Nota: Se houver nomes repetidos (como o Arroz na sua imagem),
                        # o valor no JSON será o da última linha lida desse alimento.
                        mapa_alimentos[nome] = {
                            "carbon_footprint": carbon,
                            "water_footprint": water,
                            "ecological_footprint": eco,
                        }
                    except ValueError:
                        print(
                            f"Aviso: Não foi possível converter os números da linha -> {linha}"
                        )
                else:
                    print(
                        f"Aviso: Linha ignorada por estar fora do formato esperado -> {linha}"
                    )

        # Escreve o resultado no JSON
        with open(arquivo_json, "w", encoding="utf-8") as f_out:
            json.dump(mapa_alimentos, f_out, indent=4, ensure_ascii=False)

        print(
            f"Sucesso! Arquivo JSON gerado. Total de alimentos únicos: {len(mapa_alimentos)}"
        )

    except FileNotFoundError:
        print(f"Erro: O arquivo '{arquivo_txt}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


# ==========================================
# EXECUÇÃO DO SCRIPT
# ==========================================
nome_txt = "mapa-nome-sustentavel.txt"
nome_json = "mapa-nome-sustentavel.json"

converter_txt_para_json(nome_txt, nome_json)
