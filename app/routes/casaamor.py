import os
from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename

from app.services.extracao import extrair_sicoob, extrair_sgtm
from app.services.conciliacao import conciliar

casaamor_bp = Blueprint("casaamor", __name__)

@casaamor_bp.route("/casaamor", methods=["GET", "POST"])
def casaamor():
    dados = []
    erro = None

    if request.method == "POST":
        extrato = request.files.get("extrato")
        sgtm = request.files.get("sgtm")

        if not extrato or not sgtm:
            erro = "Envie os dois PDFs."
            return render_template("index.html", dados=[], erro=erro)

        pasta = current_app.config.get("UPLOAD_DIR", "uploads")
        os.makedirs(pasta, exist_ok=True)

        p_extrato = os.path.join(pasta, secure_filename(extrato.filename or "extrato.pdf"))
        p_sgtm = os.path.join(pasta, secure_filename(sgtm.filename or "sgtm.pdf"))

        extrato.save(p_extrato)
        sgtm.save(p_sgtm)

        try:
            df_banco = extrair_sicoob(p_extrato)
            df_sgtm = extrair_sgtm(p_sgtm)

            df_final = conciliar(df_banco, df_sgtm)

            dados = df_final.to_dict(orient="records")
        except Exception as e:
            erro = f"Erro ao processar os PDFs: {e}"

    return render_template("index.html", dados=dados, erro=erro)
