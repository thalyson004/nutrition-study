from dataclasses import asdict, dataclass, field
import json
import pickle


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

print(type(dados_tbca))

with open("mapa-tbca-completo.json", "w", encoding="utf-8") as arquivo:
    json.dump(dados_tbca, arquivo, indent=4, ensure_ascii=False)


mapa_nome_codigo = {valor["nome"]: chave for chave, valor in dados_tbca.items()}

with open("mapa-nome-codigo.json", "w", encoding="utf-8") as arquivo:
    json.dump(mapa_nome_codigo, arquivo, indent=4, ensure_ascii=False)
