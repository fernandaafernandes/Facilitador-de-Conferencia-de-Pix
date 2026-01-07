import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename

from app.services.extracao import extrair_sicoob, extrair_sgtm
from app.services.conciliacao import conciliar

casaamor_bp = Blueprint("casaamor", __name__)

@casaamor_bp.route("/", methods=["GET", "POST"])
def home():
    
    dados = []
    erro = None

    if request.method == "POST":
        extrato = request.files.get("extrato")
        sgtm = request.files.get("sgtm")

        if not extrato or not sgtm:
            return render_template("index.html", dados=[], erro="Envie os dois PDFs.")

        pasta = "/tmp"
        
        try:
            p_extrato = os.path.join(pasta, secure_filename(extrato.filename))
            p_sgtm = os.path.join(pasta, secure_filename(sgtm.filename))

            # Salva arquivos
            extrato.save(p_extrato)
            sgtm.save(p_sgtm)

            # Processamento 
            df_banco = extrair_sicoob(p_extrato)
            df_sgtm = extrair_sgtm(p_sgtm)
            df_resultado = conciliar(df_banco, df_sgtm)
            
            # Conversão para lista de dicionários
            if df_resultado is not None:
                if hasattr(df_resultado, 'to_dict'):
                    dados = df_resultado.to_dict(orient='records')
                else:
                    dados = df_resultado
            
        except Exception as e:
            dados = []
            erro = f"Erro técnico: {str(e)}"
        finally:
            if 'p_extrato' in locals() and os.path.exists(p_extrato):
                os.remove(p_extrato)
            if 'p_sgtm' in locals() and os.path.exists(p_sgtm):
                os.remove(p_sgtm)

    
    if hasattr(dados, 'empty'):
        dados = dados.to_dict(orient='records')
    
    if not isinstance(dados, list):
        dados = []

    return render_template("index.html", dados=dados, erro=erro)