import json
import difflib
import os

def limpar_texto(texto):
    """Padroniza o texto para melhorar a precisão da comparação."""
    return texto.lower().replace(',', '').strip()

def encontrar_melhor_match(nome_busca, chaves_validas, cache_mapeamento):
    """
    Encontra a chave mais parecida usando o SequenceMatcher.
    Usa um cache (dicionário) para não calcular a mesma palavra duas vezes.
    """
    # 1. Se já corrigiu essa palavra antes, pega do cache (muito mais rápido)
    if nome_busca in cache_mapeamento:
        return cache_mapeamento[nome_busca]
    
    texto_limpo = limpar_texto(nome_busca)
    melhor_match = nome_busca # Mantém o original por padrão caso não ache nada
    maior_score = 0.0
    
    # 2. Procura a maior similaridade entre todas as chaves válidas
    for chave in chaves_validas:
        chave_limpa = limpar_texto(chave)
        
        # Calcula a similaridade (ratio de 0.0 a 1.0)
        score = difflib.SequenceMatcher(None, texto_limpo, chave_limpa).ratio()
        
        if score > maior_score:
            maior_score = score
            melhor_match = chave
            
    # 3. Salva no cache para uso futuro e retorna
    cache_mapeamento[nome_busca] = melhor_match
    return melhor_match

def corrigir_nomes_dietas(arquivos_dietas, arquivo_pegadas):
    # Carrega as chaves válidas do mapa de pegadas
    print("Carregando banco de nomes válidos (Pegadas Ambientais)...")
    try:
        with open(arquivo_pegadas, 'r', encoding='utf-8') as f:
            mapa_pegadas = json.load(f)
            chaves_validas = list(mapa_pegadas.keys())
    except Exception as e:
        print(f"Erro ao carregar mapa de pegadas: {e}")
        return

    # Dicionário de memória para otimizar velocidade
    cache_mapeamento = {}

    for arquivo_dieta in arquivos_dietas:
        print(f"\n{'='*50}\nProcessando: {arquivo_dieta}\n{'='*50}")
        
        try:
            with open(arquivo_dieta, 'r', encoding='utf-8') as f:
                dietas = json.load(f)
        except Exception as e:
            print(f"Erro ao ler {arquivo_dieta}: {e}")
            continue

        alteracoes_feitas = 0
        itens_analisados = 0

        # Navega na estrutura do JSON: Dieta -> Dia -> Refeição -> Itens
        for dieta in dietas:
            for dia, refeicoes in dieta.items():
                if not isinstance(refeicoes, dict):
                    continue
                
                for nome_refeicao, itens in refeicoes.items():
                    if not isinstance(itens, list):
                        continue
                        
                    for item in itens:
                        nome_original = item.get('alimento')
                        if not nome_original:
                            continue
                            
                        itens_analisados += 1
                        
                        # Chama a função mágica que busca o nome correto
                        novo_nome = encontrar_melhor_match(nome_original, chaves_validas, cache_mapeamento)
                        
                        # Se o nome mudou, atualiza no JSON
                        if nome_original != novo_nome:
                            item['alimento'] = novo_nome
                            alteracoes_feitas += 1

        # Salva o novo arquivo JSON com os nomes corrigidos
        novo_nome_arquivo = f"corrigido_{os.path.basename(arquivo_dieta)}"
        
        with open(novo_nome_arquivo, 'w', encoding='utf-8') as f_out:
            # indent=2 ou 4 para manter legível
            json.dump(dietas, f_out, indent=4, ensure_ascii=False)
            
        print(f"✅ Concluído!")
        print(f"   - Total de alimentos analisados: {itens_analisados}")
        print(f"   - Nomes corrigidos/alterados: {alteracoes_feitas}")
        print(f"💾 Novo arquivo gerado: {novo_nome_arquivo}")

# ==========================================
# EXECUÇÃO DO SCRIPT
# ==========================================
arquivos_para_corrigir = [
    "dietas-regular.json",
    "dietas-vegana.json",
    "dietas-vegetariana.json"
]

corrigir_nomes_dietas(
    arquivos_dietas=arquivos_para_corrigir, 
    arquivo_pegadas="mapa-sustentavel-pegadas.json"
)