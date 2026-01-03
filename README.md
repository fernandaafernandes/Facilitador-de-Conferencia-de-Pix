# Conferência de Doações PIX  – Extrato x SGTM

Projeto web para automatizar a conferência de doações via PIX comparando:
- **Extrato bancário (PDF)**
- **Relatório de recibos/baixas do SGTM (PDF)**

O sistema identifica automaticamente quais doações **já possuem recibo** e quais estão **pendentes de envio**.

## 🚀 Funcionalidades
- Upload de 2 PDFs (Extrato e SGTM)
- Extração de lançamentos PIX recebidos 
- Normalização de nomes (nomes abreviado / variações)
- Conciliação inteligente por **valor** e similaridade de **nome** (usando fuzzy)
- Tabela final com: **Nome | Valor | Data | Situação**

## 🧰 Tecnologias
- Python + Flask
- PyPDF (leitura de PDF texto)
- Pandas (estruturação e tratamento)
- RapidFuzz (comparação aproximada de nomes)
- Bootstrap (interface)

## ✅ Requisitos
- Python 3.10+
- PDFs devem ser **texto** (não imagem/scan). Para PDF imagem, será necessário OCR.

## ▶️ Como rodar
```bash
python -m venv .venv
source .venv/bin/activate   # mac/linux
# .venv\Scripts\activate    # windows

pip install -r requirements.txt
python run.py
