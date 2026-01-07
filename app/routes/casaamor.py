import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename

from app.services.extracao import extrair_sicoob, extrair_sgtm
from app.services.conciliacao import conciliar

casaamor_bp = Blueprint("casaamor", __name__)

@casaamor_bp.route("/", methods=["GET", "POST"])
def home():
    dados = []  # Inicializa como lista vazia
    erro = None

    if request.method == "POST":
        extrato = request.files.get("extrato")
        sgtm = request.files.get("sgtm")

        if not extrato or not sgtm:
            erro = "Envie os dois PDFs."
            return render_template("index.html", dados=[], erro=erro)

        pasta = current_app.config["UPLOAD_DIR"]

        p_extrato = os.path.join(pasta, secure_filename(extrato.filename))
        p_sgtm = os.path.join(pasta, secure_filename(sgtm.filename))

        extrato.save(p_extrato)
        sgtm.save(p_sgtm)

        try:
            df_banco = extrair_sicoob(p_extrato)
            df_sgtm = extrair_sgtm(p_sgtm)
            
            
            df_resultado = conciliar(df_banco, df_sgtm)
            
            # Converte para lista de dicionários
            if df_resultado is not None and not df_resultado.empty:
                dados = df_resultado.to_dict(orient='records')
            else:
                dados = []
                
        except Exception as e:
            erro = f"Erro no processamento: {str(e)}"

    return render_template("index.html", dados=dados, erro=erro)