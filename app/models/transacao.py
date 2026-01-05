from app.extensions import db

class TransacaoPix(db.Model):
    __tablename__ = "transacoes_pix"

    id = db.Column(db.Integer, primary_key=True)

    upload_id = db.Column(
        db.Integer,
        db.ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False
    )

    data_transacao = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(12, 2), nullable=False)

    nome_pagador = db.Column(db.String(150), nullable=False)
    documento_pagador = db.Column(db.String(20))
    descricao = db.Column(db.Text)

    id_externo = db.Column(db.String(100))  
    tipo_movimento = db.Column(db.String(10), nullable=False)  # ENTRADA / SAIDA

    criado_em = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    upload = db.relationship("Upload", back_populates="transacoes")
    conferencia = db.relationship("Conferencia", back_populates="transacao", uselist=False)

    __table_args__ = (
        db.Index("idx_transacoes_data", "data_transacao"),
        db.Index("idx_transacoes_valor", "valor"),
        db.Index("idx_transacoes_nome", "nome_pagador"),
    )

    def __repr__(self) -> str:
        return f"<TransacaoPix id={self.id} data={self.data_transacao} valor={self.valor}>"
