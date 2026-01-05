from app.extensions import db

class Beneficiario(db.Model):
    __tablename__ = "beneficiarios"

    id = db.Column(db.Integer, primary_key=True)
    nome_canonico = db.Column(db.String(150), nullable=False)
    cpf_cnpj = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, nullable=False, server_default=db.text("true"))
    criado_em = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    conferencias = db.relationship("Conferencia", back_populates="beneficiario")

    def __repr__(self) -> str:
        return f"<Beneficiario id={self.id} nome={self.nome_canonico}>"
