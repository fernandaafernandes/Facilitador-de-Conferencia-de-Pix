import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename

from app.services.extracao import extrair_sicoob, extrair_sgtm
from app.services.conciliacao import conciliar

casaamor_bp = Blueprint("casaamor", __name__)

@casaamor_bp.route("/", methods=["GET", "POST"])
def home():
    dados_para_template = [] 
    erro = None

    if request.method == "POST":
        try:
            extrato = request.files.get("extrato")
            sgtm = request.files.get("sgtm")

            if not extrato or not sgtm:
                return render_template("index.html", dados=[], erro="Envie os dois PDFs.")

            pasta = "/tmp" 
            p_extrato = os.path.join(pasta, secure_filename(extrato.filename))
            p_sgtm = os.path.join(pasta, secure_filename(sgtm.filename))

            extrato.save(p_extrato)
            sgtm.save(p_sgtm)

            df_banco = extrair_sicoob(p_extrato)
            df_sgtm = extrair_sgtm(p_sgtm)
            df_resultado = conciliar(df_banco, df_sgtm)
            
            if df_resultado is not None and hasattr(df_resultado, 'to_dict'):
                dados_para_template = df_resultado.to_dict(orient='records')
            
        except Exception as e:
            erro = f"Erro no processamento: {str(e)}"
            dados_para_template = []

    return render_template("index.html", dados=dados_para_template, erro=erro)