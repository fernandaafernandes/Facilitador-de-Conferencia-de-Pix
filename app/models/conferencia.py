from app.extensions import db

class Conferencia(db.Model):
    __tablename__ = "conferencias"

    id = db.Column(db.Integer, primary_key=True)

    transacao_id = db.Column(
        db.Integer,
        db.ForeignKey("transacoes_pix.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    beneficiario_id = db.Column(
        db.Integer,
        db.ForeignKey("beneficiarios.id", ondelete="SET NULL"),
        nullable=True
    )

    status = db.Column(db.String(30), nullable=False)  # BAIXADO, PENDENTE_DE_ENVIO
    origem_status = db.Column(db.String(20))  
    observacao = db.Column(db.Text)
    match_score = db.Column(db.Integer) 
    conferido_em = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    transacao = db.relationship("TransacaoPix", back_populates="conferencia")
    beneficiario = db.relationship("Beneficiario", back_populates="conferencias")

    def __repr__(self) -> str:
        return f"<Conferencia id={self.id} status={self.status} transacao_id={self.transacao_id}>"
