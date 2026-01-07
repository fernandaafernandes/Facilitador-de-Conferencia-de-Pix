# app/services/extracao.py

import re
from collections import Counter

import pandas as pd
from pypdf import PdfReader

from app.utils.normalizacao import limpar_nome


def _safe_text(page) -> str:
    """Evita None quando o PDF vem com página vazia/quebrada."""
    return page.extract_text() or ""


def _infer_ano_do_pdf(texto: str) -> str:
    """
    Se tiver vários anos, pega o mais frequente.
    Se não tiver nenhum, usa fallback.
    """
    anos = re.findall(r"\b(20\d{2})\b", texto)
    if not anos:
        return "2025"  # fallback se o PDF vier MUITO quebrado
    return Counter(anos).most_common(1)[0][0]


def extrair_sicoob(caminho_pdf: str) -> pd.DataFrame:
    """
    Extrato SICOOB:
    - captura PIX recebidos (crédito 'C') com variações no texto
    - extrai data para todos:
        * se tiver dd/mm/aaaa, usa
        * se tiver só dd/mm, usa ano inferido do próprio PDF
    - pega nome nas próximas linhas após o lançamento

    Retorna DataFrame: nome, valor, data_banco
    """
    reader = PdfReader(caminho_pdf)

    linhas = []
    for p in reader.pages:
        linhas.extend(_safe_text(p).splitlines())

    texto_full = "\n".join(linhas).upper()
    ano_inferido = _infer_ano_do_pdf(texto_full)

    # Coisas que NÃO são doação
    termos_ignorar = [
        "TARIFA", "TARIFAS", "TAXA", "CHEQUE ESPECIAL", "VENCIMENTO",
        "DEB", "DEBITO", "JUROS", "IOF", "ENCARGOS", "SALDO", "LIMITE",
        "RESUMO", "EXTRATO", "MOVIMENTACAO"
    ]

    # Datas
    pad_data_full = re.compile(r"(?P<data>\d{2}/\d{2}/\d{4})")
    pad_dm_inicio = re.compile(r"^(?P<dm>\d{2}/\d{2})\b")

    # Valor crédito: "40,00C" ou "40,00 C"
    pad_valor_credito = re.compile(
        r"(?P<valor>\d{1,3}(?:\.\d{3})*,\d{2})\s*C\b",
        re.IGNORECASE
    )

    def parece_pix_recebido(linha_upper: str) -> bool:
        if "PIX" not in linha_upper:
            return False
        return any(t in linha_upper for t in ["RECEB", "RECEBIDO", "RECEBIMENTO"])

    dados = []
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()
        up = linha.upper()

        # mata lixo rápido
        if any(t in up for t in termos_ignorar):
            i += 1
            continue

        # precisa ter data (completa ou dd/mm no início)
        tem_data = bool(pad_data_full.search(linha)) or bool(pad_dm_inicio.search(linha))
        if not tem_data:
            i += 1
            continue

        # precisa ser pix recebido
        if not parece_pix_recebido(up):
            i += 1
            continue

        # precisa ser crédito (C)
        m_val = pad_valor_credito.search(linha)
        if not m_val:
            i += 1
            continue

        valor = float(m_val.group("valor").replace(".", "").replace(",", "."))

        # data: completa se tiver, senão monta dd/mm/ano
        m_full = pad_data_full.search(linha)
        if m_full:
            data_banco = m_full.group("data")
        else:
            m_dm = pad_dm_inicio.search(linha)
            dm = m_dm.group("dm") if m_dm else None
            data_banco = f"{dm}/{ano_inferido}" if dm else None

        # nome: pega nas próximas linhas (até 6)
        nome = ""
        for j in range(i + 1, min(i + 7, len(linhas))):
            cand = limpar_nome(linhas[j])
            if not cand:
                continue
            # ignora rótulos comuns
            if "RECEBIMENTO" in cand and "PIX" in cand:
                continue
            if len(cand.split()) >= 2:
                nome = cand
                break

        if not nome:
            nome = "DESCONHECIDO"

        dados.append({
            "nome": nome,
            "valor": round(valor, 2),
            "data_banco": data_banco
        })

        i += 1

    df = pd.DataFrame(dados)
    if df.empty:
        return df

    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").round(2)
    df = df.dropna(subset=["valor"]).reset_index(drop=True)
    return df


def extrair_sgtm(caminho_pdf: str) -> pd.DataFrame:
    """
      - pega código no início (dígitos)
      - acha o PRIMEIRO valor monetário
      - nome = tudo entre código e valor
      - data_sgtm = última data dd/mm/aaaa encontrada após o valor

    Retorna DataFrame: nome_sis, valor_sis, data_sgtm
    """
    reader = PdfReader(caminho_pdf)
    texto = "\n".join(_safe_text(p) for p in reader.pages)

    dados = []

    for ln in texto.splitlines():
        ln = ln.strip()
        if not ln:
            continue

        low = ln.lower()
        if low.startswith("código") or low.startswith("codigo"):
            continue

        # código no início 
        m_code = re.match(r"^(\d+)\s*(.*)$", ln)
        if not m_code:
            continue

        resto = m_code.group(2)

        # primeiro valor monetário na linha
        m_val = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", resto)
        if not m_val:
            continue

        valor = float(m_val.group(1).replace(".", "").replace(",", "."))

        nome_raw = resto[:m_val.start()].strip()
        nome = limpar_nome(nome_raw)
        if not nome:
            continue

        # datas depois do valor
        datas = re.findall(r"\d{2}/\d{2}/\d{4}", resto[m_val.end():])
        data_sgtm = datas[-1] if datas else None

        dados.append({
            "nome_sis": nome,
            "valor_sis": round(valor, 2),
            "data_sgtm": data_sgtm
        })

    df = pd.DataFrame(dados)
    if df.empty:
        return df

    df["valor_sis"] = pd.to_numeric(df["valor_sis"], errors="coerce").round(2)
    df = df.dropna(subset=["valor_sis"]).reset_index(drop=True)
    return df
