import pypdf
import pandas as pd
import re
from unidecode import unidecode
from rapidfuzz import fuzz

def limpar_nome_final(texto):
    if not texto: return ""
    t = unidecode(str(texto)).upper()
    
    # Remove termos técnicos do Sicoob que poluem o nome
    lixo = [
        "SICOOB", "SISTEMA DE", "COOPERATIVAS", "PLATAFORMA", "EXTRATO", "CONTA",
        "HISTORICO", "MOVIMENTACAO", "SALDO", "DOC PIX", "OUTRA IF", "PIX RECEB",
        "RECEBIMENTO", "DEB PARC", "SUBS INTEG", "VALOR", "DATA", "PERIODO", "TRA IF C"
    ]
    for item in lixo:
        t = t.replace(item, "")
    
    t = re.sub(r'[^A-Z ]', ' ', t)
    partes = t.split()
    
    # Mantém apenas os dois primeiros nomes para facilitar a conciliação
    if len(partes) >= 2:
        return f"{partes[0]} {partes[1]}"
    return " ".join(partes)

def extrair_sicoob(caminho):
    dados = []
    reader = pypdf.PdfReader(caminho)
    texto_completo = "\n".join([p.extract_text() for p in reader.pages])
    
    for match in re.finditer(r'([\d\.,]+)C', texto_completo):
        valor = float(match.group(1).replace('.', '').replace(',', '.'))
        contexto = texto_completo[max(0, match.start()-150):match.end()+50]
        
        nome_limpo = ""
        for linha in contexto.split('\n'):
            res = limpar_nome_final(linha)
            if len(res) > 3:
                nome_limpo = res
                break
        
        if nome_limpo:
            dados.append({'nome': nome_limpo, 'valor': valor})
    return pd.DataFrame(dados)

def extrair_sgtm(caminho):
    dados = []
    reader = pypdf.PdfReader(caminho)
    for page in reader.pages:
        for linha in page.extract_text().split('\n'):
            m_data = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
            m_valor = re.search(r'(\d+,\d{2})', linha)
            if m_data and m_valor:
                data = m_data.group(1)
                valor = float(m_valor.group(1).replace(',', '.'))
                nome = limpar_nome_final(linha.replace(data, "").replace(m_valor.group(1), ""))
                dados.append({'nome_sis': nome, 'valor_sis': valor, 'data_sgtm': data})
    return pd.DataFrame(dados)

def conciliar(df_banco, df_sgtm, score_min=80):
    if df_banco.empty: return pd.DataFrame()
    
    matches = []
    for _, b in df_banco.iterrows():
        valor = b["valor"]
        nome = b["nome"]
        
        # Filtra no sistema com o mesmo valor
        candidatos = df_sgtm[df_sgtm["valor_sis"] == valor].copy()
        
        best_score = -1
        best_data = "---"
        
        for _, s in candidatos.iterrows():
            score = fuzz.token_set_ratio(nome, s["nome_sis"])
            if score > best_score:
                best_score = score
                best_data = s["data_sgtm"]
        
        situacao = "RECIBO ENVIADO" if best_score >= score_min else "PENDENTE"
        matches.append({
            "nome": nome,
            "valor": valor,
            "data": best_data,
            "situacao": situacao
        })
    return pd.DataFrame(matches)