from app.extensions import db

class Upload(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # EXTRATO, SGTM, OUTRO
    nome_arquivo = db.Column(db.String(150), nullable=False)
    hash_arquivo = db.Column(db.String(100), unique=True, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    criado_em = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    transacoes = db.relationship(
        "TransacaoPix",
        back_populates="upload",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Upload id={self.id} tipo={self.tipo} arquivo={self.nome_arquivo}>"