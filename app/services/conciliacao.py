import pandas as pd
from rapidfuzz import fuzz
from app.utils.normalizacao import limpar_nome


def _sem_iniciais(nome_norm: str) -> str:
    # remove tokens de 1 letra (G, N, R, F, C...)
    if not nome_norm:
        return ""
    toks = [t for t in nome_norm.split() if len(t) > 1]
    return " ".join(toks)


def conciliar(df_banco: pd.DataFrame, df_sgtm: pd.DataFrame, score_min: int = 62, tol_valor: float = 0.01):
    """
    Para cada PIX do extrato:
      - filtra candidatos no SGTM por valor (com tolerância)
      - casa por similaridade de nome (fuzzy)
      - marca RECIBO ENVIADO quando achar

    Retorna SOMENTE:
      nome, valor, data, situacao
    """
    if df_banco is None or df_banco.empty:
        return pd.DataFrame(columns=["nome", "valor", "data", "situacao"])

    df_banco = df_banco.copy()
    df_sgtm = df_sgtm.copy() if df_sgtm is not None else pd.DataFrame()

    df_banco["valor"] = pd.to_numeric(df_banco["valor"], errors="coerce").round(2)
    df_banco = df_banco.dropna(subset=["valor"]).reset_index(drop=True)

    df_banco["nome_norm"] = df_banco["nome"].apply(limpar_nome).apply(_sem_iniciais)

    # se SGTM vazio, tudo pendente
    if df_sgtm.empty:
        out = df_banco.rename(columns={"data_banco": "data"})
        out["situacao"] = "PENDENTE DE ENVIO"
        return out[["nome", "valor", "data", "situacao"]]

    df_sgtm["valor_sis"] = pd.to_numeric(df_sgtm["valor_sis"], errors="coerce").round(2)
    df_sgtm = df_sgtm.dropna(subset=["valor_sis"]).reset_index(drop=True)
    df_sgtm["nome_norm"] = df_sgtm["nome_sis"].apply(limpar_nome)
    df_sgtm["__usado"] = False

    resultado = []

    for _, b in df_banco.iterrows():
        nome = b["nome"]
        nome_norm = b["nome_norm"]
        valor = float(b["valor"])
        data = b.get("data_banco")

        candidatos = df_sgtm[
            (~df_sgtm["__usado"]) &
            (abs(df_sgtm["valor_sis"] - valor) <= tol_valor)
        ]

        best_idx = None
        best_score = -1

        for idx, s in candidatos.iterrows():
            score = fuzz.token_set_ratio(nome_norm, s["nome_norm"])
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is not None and best_score >= score_min:
            df_sgtm.loc[best_idx, "__usado"] = True
            situacao = "RECIBO ENVIADO"
        else:
            situacao = "PENDENTE DE ENVIO"

        resultado.append({
            "nome": nome,
            "valor": valor,
            "data": data,
            "situacao": situacao
        })

    return pd.DataFrame(resultado)
