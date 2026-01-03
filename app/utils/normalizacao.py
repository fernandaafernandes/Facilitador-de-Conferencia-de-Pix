import re
from unidecode import unidecode

BLOQUEADOS = {
    "PIX", "RECEB", "RECEBIDO", "RECEBIMENTO",
    "SICOOB", "DOC", "TED",
    "TARIFA", "TARIFAS", "TAXA",
    "CHEQUE", "ESPECIAL", "VENCIMENTO",
    "DEB", "DEBITO", "JUROS", "IOF", "ENCARGOS",
    "SALDO", "LANCTO", "LANCAMENTO",
    "CREDITO", "DEBITO",
    "EMPRESARIAL", "PROVISIONADAS", "PROVISIONADA",
    "R", "RS"
}

def limpar_nome(texto: str) -> str:
    if not texto:
        return ""

    t = unidecode(str(texto)).upper()
    t = re.sub(r"[^A-Z\s]", " ", t)
    t = " ".join(t.split())

    palavras = [p for p in t.split() if p not in BLOQUEADOS]
    nome = " ".join(palavras).strip()

    return nome if len(nome) >= 6 else ""
