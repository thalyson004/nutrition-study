import json

def unificar_mapas_tbca(arq_sustentavel_nome, arq_nome_tbca, arq_saida):
    try:
        # 1. Carrega os dois dicionários originais
        with open(arq_sustentavel_nome, 'r', encoding='utf-8') as f1:
            mapa_sustentavel_nome = json.load(f1)

        with open(arq_nome_tbca, 'r', encoding='utf-8') as f2:
            mapa_nome_tbca = json.load(f2)

        # Dicionário que vai guardar a relação direta (Nome Alterado -> Código)
        mapa_final = {}
        nomes_reais_sem_codigo = []

        # 2. Faz o cruzamento dos dados
        for nome_alterado, nome_real in mapa_sustentavel_nome.items():
            
            # Verifica se o nome real (encontrado no primeiro arquivo) existe como chave no segundo
            if nome_real in mapa_nome_tbca:
                codigo_tbca = mapa_nome_tbca[nome_real]
                mapa_final[nome_alterado] = codigo_tbca
            else:
                # Caso algum nome real não tenha sido mapeado para um código
                nomes_reais_sem_codigo.append(nome_real)

        # 3. Salva o resultado no novo arquivo JSON
        with open(arq_saida, 'w', encoding='utf-8') as f_out:
            json.dump(mapa_final, f_out, indent=4, ensure_ascii=False)

        # ==========================================
        # RESUMO DA OPERAÇÃO
        # ==========================================
        print(f"✅ Arquivo '{arq_saida}' gerado com sucesso!")
        print(f"   -> Total de itens mapeados diretamente para o TBCA: {len(mapa_final)}")

        if nomes_reais_sem_codigo:
            print(f"⚠️  Aviso: {len(nomes_reais_sem_codigo)} nomes reais não possuíam código correspondente.")

    except FileNotFoundError as e:
        print(f"Erro: Arquivo não encontrado. Detalhes: {e}")
    except json.JSONDecodeError:
        print("Erro: Um dos arquivos não possui um formato JSON válido.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# ==========================================
# EXECUÇÃO DO SCRIPT
# ==========================================
unificar_mapas_tbca(
    "mapa-sustentavel-nome.json", 
    "mapa-nome-tbca.json", 
    "mapa-sustentavel-tbca.json"
)